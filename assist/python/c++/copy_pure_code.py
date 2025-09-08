import subprocess
import sys
import os
from datetime import datetime

import re
from pathlib import Path

import sys
__root_path__=Path(__file__).parent.parent.resolve()
sys.path.append(str(__root_path__ ))
sys.path.append( os.path.join(__root_path__,'base') )



from base import logger_helper,UpdateTimeType,copy_folder


import shutil


def create_ignore_function(exclude_dirs, exclude_files,ignored_lst:list=None):
    """
    创建一个忽略函数，用于 shutil.copytree。
    
    参数:
        exclude_dirs: 要排除的目录名列表 (例如 ['.git', '__pycache__'])
        exclude_files: 要排除的文件名列表 (例如 ['.DS_Store', '*.tmp'])
    
    返回:
        一个忽略函数，符合 shutil.copytree ignore 参数的要求。
    """
    def ignore_func(dir, names):
        # 初始化要忽略的列表
        ignored = set()
        
        for name in names:
            full_path = os.path.join(dir, name)
            # 检查是否是目录且在排除列表中
            if exclude_dirs and os.path.isdir(full_path) and name in exclude_dirs:
                    ignored.add(name)
            # 检查是否是文件且在排除列表中，或匹配通配符
            elif exclude_files :
                if os.path.isfile(full_path) and  name in exclude_files:
                    ignored.add(name)
                # 简单的通配符匹配（示例：匹配 .tmp 结尾的文件）
                elif any(name.endswith(pattern.strip('*')) for pattern in exclude_files if '*' in pattern):
                    ignored.add(name)
      
        if ignored_lst is not None:
            ignored_lst.extend([os.path.join(dir,item) for item in ignored])
        return ignored
    return ignore_func



def copy_pure_project_code(source_dir, destination_dir,exclude_dirs:list, exclude_files:list):

    logger=logger_helper("开始复制项目代码",f"{source_dir}->{destination_dir}")

    # 创建忽略函数实例
    ignored_lst=[]
    ignore_function = create_ignore_function(exclude_dirs, exclude_files,ignored_lst)

    # 执行复制，并应用过滤规则
    try:
        shutil.copytree(source_dir, destination_dir, ignore=ignore_function,dirs_exist_ok=True)
        logger.info("完成",f"排除了以下目录及文档\n{'\n'.join(ignored_lst)}\n",update_time_type=UpdateTimeType.ALL)
    except FileExistsError:
        logger.info("失败",f"目标目录 '{destination_dir}' 已存在。",update_time_type=UpdateTimeType.ALL)
    except Exception as e:
        logger.info("异常",f"{e}",update_time_type=UpdateTimeType.ALL)
        
    #可用以下替换
        
    # 示例：忽略所有 .tmp 临时文件和 __pycache__ 目录
    # temp:list=exclude_dirs.copy()
    # temp.extend(exclude_files)
    # ignore_patterns = shutil.ignore_patterns(*temp)
    # shutil.copytree(source_dir, destination_dir, ignore=ignore_patterns, dirs_exist_ok=True) # 可与 dirs_exist_ok 结合使用
            
if __name__ == "__main__":

    # 要排除的目录和文件列表
    exclude_dirs = ['.git', '3rd', 'build'] # 排除的目录名
    exclude_files = ['.gitignore']# 排除的文件名，支持简单通配符

    # 源目录和目标目录
    source_dir = r'F:\test\joy_project'
    destination_dir = r'F:\test\ubuntu_configure\joy_project'
    copy_pure_project_code(source_dir, destination_dir, exclude_dirs,exclude_files)