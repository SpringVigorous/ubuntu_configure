import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from base import logger_helper,audio_root,singleton,write_to_json_utf8_sig,read_from_json_utf8_sig,UpdateTimeType,exception_decorator,current_user

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
    
    @exception_decorator(error_state=False)
    def scan(self, folder)-> list[dict]:
        if not folder or not os.path.exists(folder):
            return []
        
        
        """
        功能1: 递归扫描文件夹，获取文件相对路径和修改时间
        
        Args:
            folder_path: 要扫描的文件夹路径
            output_json_path: JSON输出路径(可选)
            
        Returns:
            list[dict]: 文件信息列表
        """
        self.logger.update_time(UpdateTimeType.STAGE)
        self.logger.update_target(detail=f"扫描目录: {folder}")
        
        try:
            folder = Path(folder)           
            file_list = []
            # 使用os.walk递归遍历目录[1,2](@ref)
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = Path(root) / file
                    
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
                        self.logger.error("无法获取文件时间",f"当前文件{file_path}{e}")
                        continue
                    
                    file_info = {
                        "relative_path": str(relative_path),
                        "mod_time": mod_time,
                        "readable_time": readable_time
                    }
                    file_list.append(file_info)
            
            self.logger.info("扫描完成",f"找到 {len(file_list)} 个文件",update_time_type=UpdateTimeType.STAGE)
            return file_list
            
        except Exception as e:
            self.logger.error("错误",f"{e}")
            return []
    
    @exception_decorator(error_state=False)
    def fetch_diff_results(self, list_d, list_f)->list[str]:
        """
        功能2: 比较两个文件列表的差异
        
        Args:
            list_d: 第一个文件列表(list[dict])
            list_f: 第二个文件列表(list[dict])
            
        Returns:
            dict: 包含差异结果
        """
        self.logger.update_time(UpdateTimeType.STAGE)
        self.logger.update_target(detail="比较文件列表")
        try:
            
            # 创建路径到文件信息的映射[7](@ref)
            dict_d = {item["relative_path"]: item for item in list_d}
            dict_f = {item["relative_path"]: item for item in list_f}
            
            # 找出F中有而D中没有的文件[7,8](@ref)
            only_in_f = [dict_f[path] for path in dict_f if path not in dict_d]
            
            # 找出共有的且F的修改时间晚于D的文件[7,8](@ref)
            common_newer = []
            for path in dict_f:
                if path in dict_d:
                    if dict_f[path]["mod_time"] > dict_d[path]["mod_time"]:
                        common_newer.append(dict_f[path])
            
            # 合并结果[7](@ref)
            list_g = only_in_f + common_newer
            self.logger.info("成功",f"独有的文件 {len(only_in_f)} 个, 更新的文件 {len(common_newer)} 个")
            return [ str(i["relative_path"]) for i in  list_g]
            
        except Exception as e:
            self.logger.error("错误",f"{e}")
            return 
    @exception_decorator(error_state=False)
    def backup_files(self, rel_path_lst, src_dir, dest_dir):
        
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
def scan_export_file(root_dir,json_file_path)->list[dict]:
    utily = FileSyncUtil()
    
    # 扫描目录并保存结果
    fresh_list = utily.scan(
        folder=local_dir,
    )
    write_to_json_utf8_sig(json_file_path,fresh_list)
    return fresh_list

@exception_decorator(error_state=False)
def diff_backup(src1_json_path,src2_json_path,src_dir,dest_dir):
    
    # 获取目录结构差异
    lst1=read_from_json_utf8_sig(src1_json_path)
    lst2=read_from_json_utf8_sig(src2_json_path)
    
    utily = FileSyncUtil()
    diff_result = utily.fetch_diff_results(lst1,lst2)
    
    diff_file_path=Path(src1_json_path).with_stem("file_diff")
    write_to_json_utf8_sig(diff_file_path,diff_result)
    os.makedirs(dest_dir,exist_ok=True)
    
    #拷贝文件
    utily.backup_files(diff_result,
        src_dir=src_dir,
        dest_dir=dest_dir
    )


#直接参考 json 文件，进行拷贝,顺便把最终结果输出到本地 cur_lst.json
def main(local_json_path,src_dir,dest_dir):
    lst1=read_from_json_utf8_sig(local_json_path)
    utily = FileSyncUtil()
    # 扫描目录并保存结果
    lst2 = utily.scan(
        folder=src_dir,
    )
    diff_result = utily.fetch_diff_results(lst1,lst2)
    utily.backup_files(diff_result,
        src_dir=src_dir,
        dest_dir=dest_dir
    )
    path2=Path(local_json_path).with_stem("cur_lst")
    
    dest= utily.scan(
        folder=src_dir,
    )
    write_to_json_utf8_sig(path2,dest)
    
    


        
if __name__ == "__main__":
    # 创建使用示例对象

    
    local_dir=audio_root
    local_json_path=local_dir/ f"{current_user()}_file_list.json"
    scan_export_file(local_dir,local_json_path)
    
    outer_json_path=local_dir/ "file_list_1.json"
    
    local_lst=read_from_json_utf8_sig(local_dir/"file_list_1.json")
    
    # 获取目录结构差异
    dest_dir=local_dir.parent/"clone"
    diff_backup(local_json_path,outer_json_path,local_dir,dest_dir)
    
