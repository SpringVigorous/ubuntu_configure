import json
import os
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from base import (
    UpdateTimeType,
    audio_root,
    current_user,
    exception_decorator,
    except_stack,
    logger_helper,
    read_from_json_utf8_sig,
    singleton,
    write_to_json_utf8_sig,
    intersect_df,
    sub_df,
    DataFrameComparator,
    df_empty,
    xlsx_manager,
    unique,
    concat_dfs,
    path_equal,
)

relative_path_id="relative_path"
mod_time_id="mod_time"
readable_time_id="readable_time"

class FileSyncManager(xlsx_manager):
    """
    文件同步管理类，继承自xlsx_manager
    """
    def __init__(self):
        super().__init__()
    def before_save(self)->bool:
        return True



@singleton
class FileSyncUtil:
    """
    文件同步工具类，提供文件遍历、比较和同步功能
    """
    
    def __init__(self):
        """
        初始化工具类
        
        Args:
            logger: 日志工具实例
        """
        self.logger = logger_helper(self.__class__.__name__)

        self.manager=FileSyncManager()
    
    @exception_decorator(error_state=False)
    def scan_folder(self, folder)-> pd.DataFrame:
        if not folder or not os.path.exists(folder):
            return []
        
        
        """
        功能1: 递归扫描文件夹，获取文件相对路径和修改时间
        
        Args:
            folder_path: 要扫描的文件夹路径
            output_json_path: JSON输出路径(可选)
            
        Returns:
            pd.DataFrame: 文件信息列表
        """
        self.logger.update_time(UpdateTimeType.STAGE)
        with self.logger.raii_target(f"扫描目录: {folder}") as logger:
            
            file_list = []
            try:
                folder = Path(folder)           
                # 使用os.walk递归遍历目录[1,2](@ref)
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = Path(root) / file
                        with self.logger.raii_target(detail= f"当前文件{file_path}") as file_logger:
                            
                            # 获取相对路径[1](@ref)
                            try:
                                relative_path = file_path.relative_to(folder)
                            except ValueError:
                                # 处理路径计算异常
                                continue
                            
                            # 获取文件修改时间[3,5](@ref)
                            try:
                                mod_time = os.path.getmtime(file_path)
                                # 转换为可读格式（可选）
                                readable_time = datetime.fromtimestamp(mod_time).isoformat()
                            except OSError as e:
                                file_logger.warn("忽略",f"无法获取文件时间\n{e}\n{except_stack()}")
                                continue
                            
                            file_info = {
                                relative_path_id: str(relative_path),
                                mod_time_id: mod_time,
                                readable_time_id: readable_time
                            }
                            file_list.append(file_info)
                
                logger.info("完成",f"找到 {len(file_list)} 个文件",update_time_type=UpdateTimeType.STAGE)               
            except Exception as e:
                logger.error("错误",f"{e}\n{except_stack()}")
            finally:
                return pd.DataFrame(file_list)
    #相对于df2来说，df1 特有的，以及 最新的
    @exception_decorator(error_state=False,error_return=[pd.DataFrame(),pd.DataFrame()])
    def diff_results(self, df1:pd.DataFrame, df2:pd.DataFrame)->tuple[pd.DataFrame,pd.DataFrame]:
        # 使用比较器
        comparator = DataFrameComparator(df1, df2, key_columns=relative_path_id)
        df1_only=comparator.df1_only
        df_common=comparator.df_org_common
        if not df_empty(df_common):
            mask=df_common[comparator.df1_column_name(mod_time_id)] > df_common[comparator.df2_column_name(mod_time_id)]
            df_common=comparator.restore_common_columns(df_common[mask])
            
        return df1_only,df_common
    @exception_decorator(error_state=False)
    def backup_files(self, rel_path_lst:list, src_dir, dest_dir):
        
        if not rel_path_lst or not src_dir or not dest_dir:
            return
        
        """
        功能3: 根据文件列表拷贝文件，保留目录结构
        
        Args:
            file_list: 文件信息列表(list[dict])
            source_base: 源文件基础路径H
            target_base: 目标目录路径
        """
        try:
            self.logger.update_target(f"拷贝文件: 从 {src_dir} 到 {dest_dir}")
            
            src_dir = Path(src_dir)
            dest_dir = Path(dest_dir)
            
            # 确保目标目录存在[9](@ref)
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            copied_count = 0
            error_count = 0
            
            for rel_path in rel_path_lst:
                if not rel_path:
                    continue
                # 构建源文件和目标文件路径[9](@ref)
                source_file = src_dir / rel_path
                target_file = dest_dir / rel_path
                with self.logger.raii_target(detail=f"{source_file}->{target_file}") as logger:
                    try:
                        # 确保目标目录存在[9](@ref)
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        # 拷贝文件[10](@ref)
                        shutil.copy2(source_file, target_file)
                        copied_count += 1
                        
                        self.logger.trace(f"已拷贝: {rel_path}")
                        
                    except Exception as e:
                        error_count += 1
                        self.logger.error(f"失败",f"{e}")
                
            self.logger.info(f"拷贝完成: 成功 {copied_count} 个, 失败 {error_count} 个")
            
        except Exception as e:
            self.logger.error("失败",f"{e}")
            
            
    @exception_decorator(error_state=False)
    def merge_folders(self,rel_path_lst:list, src1_dir,src2_dir, dest_dir,key_columns:str|list[str]):
        if not rel_path_lst or not src1_dir or not src2_dir or not dest_dir:
            return
        src1_dir,src2_dir=Path(src1_dir),Path(src2_dir)
        
        
        for file in rel_path_lst:
            src1_file=src1_dir/file
            src2_file=src2_dir/file
            dest_file=dest_dir/file
        
            if not (src1_file.exists() and src2_file.exists()):
                continue
            with self.logger.raii_target("合并文件",f"{src1_file} 和 {src2_file} -> {dest_file}") as logger:
                cur_suffix=src1_file.suffix
                if cur_suffix==".xlsx":
                    dfs1=self.manager.read_dfs(src1_file)
                    dfs2=self.manager.read_dfs(src2_file)
                    if df_empty(dfs1) or df_empty(dfs2):
                        continue
                    
                    
                    column_names=list(dfs1.keys())
                    column_names.extend(list(dfs2.keys()))
                    column_names=unique(column_names)
                    
                    for column_name in column_names:
                        if column_name in dfs1 and column_name in dfs2:
                            df1=dfs1[column_name]
                            df2=dfs2[column_name]
                            compare= DataFrameComparator(df1,df2,key_columns)
                            df=concat_dfs([compare.df1,compare.df2,compare.df_common])
                            if not df_empty(df):
                                dfs1[column_name]=df
                        if column_name not in dfs1:
                            dfs1[column_name]=dfs2[column_name]
                    self.manager.save_dfs(dest_file,dfs1)
                    logger.info("完成",update_time_type=UpdateTimeType.STEP)
                else:
                    equal_first=path_equal(src1_file,dest_file)

                    infos=[f"类型{cur_suffix}未实现" ]
                    if not equal_first:
                        infos.append(f"直接拷贝文件：{src1_file}")
                    try:
                        logger.debug("忽略",",".join(infos),update_time_type=UpdateTimeType.STEP)
                        if not equal_first:
                            shutil.copy2(src1_file, dest_file)
                    except Exception as e:
                        logger.error("失败",f"{e}\n{except_stack()}")

        pass

@exception_decorator(error_state=False)
def export_dir_file_infos(root_dir,dest_xlsx_path:str=None)->pd.DataFrame:
    utily = FileSyncUtil()
    # 扫描目录并保存结果
    df = utily.scan_folder(
        folder=root_dir,
    )
    if dest_xlsx_path:
        utily.manager.save_df(dest_xlsx_path,df)

    return df


@exception_decorator(error_state=False)
def backup_files(df1,df2,src_dir,dest_dir,dest_xlsx_path:str=None):
    utily = FileSyncUtil()
    result=  utily.diff_results(df1,df2)
    if not result:
        return
    df1_only,df_common=result
    if dest_xlsx_path:
        utily.manager.save_dfs(dest_xlsx_path,{"df1_only":df1_only,"df_common":df_common})
    #拷贝文件
    if not df_empty(df1_only):
        utily.backup_files(df1_only[relative_path_id],
            src_dir=src_dir,
            dest_dir=dest_dir
        )

    #合并
    if not df_empty(df_common):
        utily.merge_folders(list(df_common[relative_path_id]),
            src1_dir=src_dir,
            src2_dir=dest_dir,
            dest_dir=dest_dir,
            key_columns=relative_path_id
        )
            
    
#返回差异文件信息 路径
@exception_decorator(error_state=False)
def diff_backup(src1_xlsx_path,src2_xlsx_path,src_dir,dest_dir,diff_xlsx_path):
    
    # 获取目录结构差异
    utily = FileSyncUtil()
    df1=utily.manager.get_df(src1_xlsx_path)
    df2=utily.manager.get_df(src2_xlsx_path)

    backup_files(df1,df2,src_dir,dest_dir,diff_xlsx_path)

#直接参考 json 文件，进行拷贝,顺便把最终结果输出到本地 cur_lst.json
def main(reference_xlsx_path,src_dir,dest_dir):
    utily = FileSyncUtil()
    df1=utily.manager.get_df(reference_xlsx_path)
    # 扫描目录并保存结果
    df2 = utily.scan_folder(
        folder=src_dir,
    )

    diff_xlsx_path=Path(reference_xlsx_path).with_stem("cur_lst")
    backup_files(df1,df2,src_dir,dest_dir,diff_xlsx_path)

    
    
    



        
if __name__ == "__main__":

    # # 创建使用示例对象
    local_dir=audio_root
    local_xlsx_path=local_dir/ f"{current_user()}_file_list.xlsx"
    outer_xlsx_path=local_dir/ "desktop_file_list.xlsx"
    dest_dir=local_dir.parent/"clone"
    diff_xlsx_path=local_xlsx_path.with_stem("diff_file_list")
    
    
    export_dir_file_infos(local_dir,local_xlsx_path)
    # exit()
    diff_backup(local_xlsx_path,outer_xlsx_path,local_dir,dest_dir,diff_xlsx_path)
    
