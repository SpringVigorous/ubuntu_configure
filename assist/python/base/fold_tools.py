# 导入所需模块
import os
import shutil
from remove_special_fold import recycle_bin,is_empty_folder
from com_log import logger_helper,UpdateTimeType

# 定义函数：清空文件夹内容，但不删除当前文件夹
def clear_folder(folder_path):
    """
    注意事项：

    使用这个函数会删除指定文件夹下的所有文件和子文件夹，操作不可逆，请谨慎使用。
    如果要清空的文件夹中有重要文件，请提前备份。
    在使用这个函数之前，建议先检查要清空的文件夹路径是否正确，避免误删。
    """

    if is_empty_folder(folder_path):
        return
    for file in os.listdir(folder_path):
        abs_path=os.path.join(folder_path, file)
        try:
            delete_directory(abs_path)
            # if os.path.isdir(abs_path):
            # else:
            #     os.remove(abs_path)
        except Exception as e:
            print(f"删除失败:{abs_path}-{e}")
            pass

def delete_directory(directory_path):
    
    recycle_bin(directory_path)
    return
    
    """
    删除指定目录及其子目录和文件。

    :param directory_path: 要删除的目录路径
    """
    try:
        # 检查目录是否存在
        if os.path.exists(directory_path):
            # 删除目录及其子目录和文件
            shutil.rmtree(directory_path)
            print(f"Directory {directory_path} and its contents have been deleted.")
        else:
            print(f"Directory {directory_path} does not exist.")
    except OSError as e:
        print(f"Error: {e.strerror}")


def delete_files(root_dir, exclude_dirs=None, file_patterns=None):
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # 排除指定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 遍历文件
        for file in files:
            file_path = os.path.join(root, file)
            if file_patterns is None or any(file.endswith(pattern) for pattern in file_patterns):
                print(f"删除文件: {file_path}")
                # os.remove(file_path)  # 取消注释以实际删除文件
                recycle_bin(file_path)
def check_dir(dir_path):
    if os.path.exists(dir_path):
        return
    os.makedirs(dir_path,exist_ok=True)     
       
# 获取文件夹大小
def get_folder_size(folder_path):
    logger=logger_helper("获取文件夹大小",folder_path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                # 获取文件大小并累加到总大小
                total_size += os.path.getsize(file_path)
            except (OSError, PermissionError) as e:
                logger.error("失败",f"无法访问 {file_path}: {e}")
    logger.trace(f"成功",f"总大小为{.0+total_size/(2**20):.2f}MB")
    return total_size

# 格式化字节大小
def format_size(size_bytes):
    """将字节数转换为更易读的格式"""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
    return f"{size_bytes:.2f} {units[unit_index]}"




#获取文件夹及各个子目录的 大小
def get_directory_sizes(start_path):
    """
    递归获取目录及其子文件/子目录的大小，结果存储为字典：
    - 键：文件或目录的绝对路径
    - 值：对应文件/目录的大小（单位：字节）
    """
    size_dict = {}
    logger=logger_helper("获取目录及各个子目录的大小",start_path)
    def calculate_size(path):
        total_size = 0
        try:
            for entry in os.scandir(path):
                entry_path = entry.path  # 获取绝对路径
                try:
                    if entry.is_file(follow_symlinks=False):
                        # 记录文件大小
                        file_size = entry.stat(follow_symlinks=False).st_size
                        size_dict[entry_path] = file_size
                        total_size += file_size
                    elif entry.is_dir(follow_symlinks=False):
                        # 递归计算子目录大小
                        dir_size = calculate_size(entry_path)
                        size_dict[entry_path] = dir_size
                        total_size += dir_size
                except (PermissionError, FileNotFoundError) as e:
                    logger.error("失败",f"跳过无权限条目: {entry_path} ({e})")
                    continue
        except (PermissionError, FileNotFoundError) as e:
            logger.error("失败",f"无法访问目录: {path} ({e})")
            return 0
        # 记录当前目录总大小
        size_dict[path] = total_size
        return total_size
    
    # 从起始路径开始计算
    calculate_size(os.path.abspath(start_path))
    logger.trace(f"成功",f"一共获取了{len(size_dict)}个目录及文件大小")
    return size_dict 



if __name__ == '__main__':
    
    

    results=get_directory_sizes(r"C:\Users\Administrator\AppData")
    
    import pandas as pd
    df=pd.DataFrame([{"cur_path":key,"size":val} for key,val in  results.items() if os.path.isdir(key)])
    df.to_excel("result.xlsx",index=False)
    
    
    
    # # 遍历删除debug.release文件夹
    # # 设置根目录和排除目录
    # root_directory = os.path.dirname(os.path.abspath(__file__))
    # exclude_directories = ['.git']

    # # 删除 Debug 文件夹中的所有文件
    # delete_files(os.path.join(root_directory, 'Debug'), exclude_directories)

    # # 删除 Release 文件夹中的所有文件
    # delete_files(os.path.join(root_directory, 'Release'), exclude_directories)

    # # 删除 .ich 文件
    # delete_files(root_directory, exclude_directories, file_patterns=['.ich'])

    # input("按任意键继续...")