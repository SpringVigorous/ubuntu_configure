import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from base import logger_helper,audio_root,singleton,write_to_json_utf8_sig,read_from_json_utf8_sig

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
        self.logger = logger_helper()
    
    def scan_directory(self, folder_path, output_json_path=None):
        """
        功能1: 递归扫描文件夹，获取文件相对路径和修改时间
        
        Args:
            folder_path: 要扫描的文件夹路径
            output_json_path: JSON输出路径(可选)
            
        Returns:
            list[dict]: 文件信息列表
        """
        try:
            self.logger.trace(f"开始扫描目录: {folder_path}")
            folder_path = Path(folder_path)
            
            if not folder_path.exists():
                self.logger.error(f"目录不存在: {folder_path}")
                return []
            
            file_list = []
            
            # 使用os.walk递归遍历目录[1,2](@ref)
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    
                    # 获取相对路径[1](@ref)
                    try:
                        relative_path = file_path.relative_to(folder_path)
                    except ValueError:
                        # 处理路径计算异常
                        continue
                    
                    # 获取文件修改时间[3,5](@ref)
                    try:
                        mod_time = os.path.getmtime(file_path)
                        # 转换为可读格式（可选）
                        readable_time = datetime.fromtimestamp(mod_time).isoformat()
                    except OSError as e:
                        self.logger.error(f"无法获取文件时间 {file_path}: {e}")
                        continue
                    
                    file_info = {
                        "relative_path": str(relative_path),
                        "mod_time": mod_time,
                        "readable_time": readable_time
                    }
                    file_list.append(file_info)
            
            self.logger.info(f"扫描完成，找到 {len(file_list)} 个文件")
            
            # 输出到JSON文件[1](@ref)
            if output_json_path:
                try:
                    with open(output_json_path, 'w', encoding='utf-8') as f:
                        json.dump(file_list, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"文件列表已保存到: {output_json_path}")
                except Exception as e:
                    self.logger.error(f"保存JSON文件失败: {e}")
            
            return file_list
            
        except Exception as e:
            self.logger.error(f"扫描目录时发生错误: {e}")
            return []
    
    def compare_file_lists(self, list_d, list_f):
        """
        功能2: 比较两个文件列表的差异
        
        Args:
            list_d: 第一个文件列表(list[dict])
            list_f: 第二个文件列表(list[dict])
            
        Returns:
            dict: 包含差异结果
        """
        try:
            self.logger.trace("开始比较文件列表")
            
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
            
            self.logger.info(f"比较完成: F中独有的文件 {len(only_in_f)} 个, 更新的文件 {len(common_newer)} 个")
            
            return {
                "only_in_f": only_in_f,
                "common_newer": common_newer,
                "merged_list": list_g
            }
            
        except Exception as e:
            self.logger.error(f"比较文件列表时发生错误: {e}")
            return {"only_in_f": [], "common_newer": [], "merged_list": []}
    
    def copy_files_with_structure(self, file_list, source_base, target_base):
        """
        功能3: 根据文件列表拷贝文件，保留目录结构
        
        Args:
            file_list: 文件信息列表(list[dict])
            source_base: 源文件基础路径H
            target_base: 目标目录路径
        """
        try:
            self.logger.trace(f"开始拷贝文件: 从 {source_base} 到 {target_base}")
            
            source_base = Path(source_base)
            target_base = Path(target_base)
            
            # 确保目标目录存在[9](@ref)
            target_base.mkdir(parents=True, exist_ok=True)
            
            copied_count = 0
            error_count = 0
            
            for file_info in file_list:
                try:
                    rel_path = Path(file_info["relative_path"])
                    
                    # 构建源文件和目标文件路径[9](@ref)
                    source_file = source_base / rel_path
                    target_file = target_base / rel_path
                    
                    # 确保目标目录存在[9](@ref)
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 拷贝文件[10](@ref)
                    shutil.copy2(source_file, target_file)
                    copied_count += 1
                    
                    self.logger.trace(f"已拷贝: {rel_path}")
                    
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"拷贝文件失败 {file_info['relative_path']}: {e}")
            
            self.logger.info(f"拷贝完成: 成功 {copied_count} 个, 失败 {error_count} 个")
            
        except Exception as e:
            self.logger.error(f"拷贝文件时发生错误: {e}")

# 使用示例
@singleton
class FolderUsage:
    """
    使用示例类
    """
    def __init__(self):
        self.sync_util = FileSyncUtil()
    
    def scan_folder(self,folder_path,output_json_path):
        """功能1使用示例"""
        # 扫描目录并保存结果
        file_list = self.sync_util.scan_directory(
            folder_path=folder_path,
            output_json_path=output_json_path
        )
        return file_list
    
    def info_diffs(self,list_d,list_f,json_path):
        """功能2使用示例"""

        result = self.sync_util.compare_file_lists(list_d, list_f)
        
        # 保存结果G到JSON
        with open(json_path, 'w') as f:
            json.dump(result["merged_list"], f, indent=2)
        
        return result
    
    def clone_files(self,list_g,root_dir,dest_dir):
        """功能3使用示例"""
        # 假设已经从JSON文件加载了list_g
        list_g = [...]  # 从JSON加载
        
        self.sync_util.copy_files_with_structure(
            file_list=list_g,
            source_base=root_dir,
            target_base=dest_dir
        )
        
        
        
if __name__ == "__main__":
    # 创建使用示例对象
    usage = FolderUsage()
    
    target_dir=audio_root
    fresh_json_path=target_dir/ "file_list.json"
    
    
    # 扫描目录并保存结果
    fresh_list = usage.scan_folder(
        folder_path=target_dir,
        output_json_path=fresh_json_path
    )
    
    local_lst=read_from_json_utf8_sig(target_dir/"file_list_1.json")
    
    
    diff_json_path=target_dir/"file_list_diff.json"
    
    # 获取目录结构差异
    result = usage.info_diffs(local_lst,fresh_list,diff_json_path)
    print(result)
    
    
    
    dest_dir=target_dir.parent/"clone"
    os.makedirs(dest_dir,exist_ok=True)
    
    #拷贝文件
    usage.clone_files(
        list_g=result,
        root_dir=target_dir,
        dest_dir=dest_dir
    )