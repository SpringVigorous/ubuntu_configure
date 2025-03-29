# 导入所需模块
import os
import shutil



# 定义函数：清空文件夹内容，但不删除当前文件夹
def clear_folder(folder_path):
    """
    注意事项：

    使用这个函数会删除指定文件夹下的所有文件和子文件夹，操作不可逆，请谨慎使用。
    如果要清空的文件夹中有重要文件，请提前备份。
    在使用这个函数之前，建议先检查要清空的文件夹路径是否正确，避免误删。
    """

    if not (os.path.exists(folder_path) or os.path.isdir(folder_path) ):
        return
    for file in os.listdir(folder_path):
        abs_path=os.path.join(folder_path, file)
        try:
            if os.path.isdir(abs_path):
                delete_directory(abs_path)
            else:
                os.remove(abs_path)
        except Exception as e:
            print(f"删除失败:{abs_path}-{e}")
            pass

def delete_directory(directory_path):
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


def delete_files(root_dir, exclude_dirs, file_patterns=None):
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # 排除指定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 遍历文件
        for file in files:
            file_path = os.path.join(root, file)
            if file_patterns is None or any(file.endswith(pattern) for pattern in file_patterns):
                print(f"删除文件: {file_path}")
                os.remove(file_path)  # 取消注释以实际删除文件
def check_dir(dir_path):
    if os.path.exists(dir_path):
        return
    os.makedirs(dir_path,exist_ok=True)        
                
if __name__ == '__main__':
    
    
    
    # 遍历删除debug.release文件夹
    # 设置根目录和排除目录
    root_directory = os.path.dirname(os.path.abspath(__file__))
    exclude_directories = ['.git']

    # 删除 Debug 文件夹中的所有文件
    delete_files(os.path.join(root_directory, 'Debug'), exclude_directories)

    # 删除 Release 文件夹中的所有文件
    delete_files(os.path.join(root_directory, 'Release'), exclude_directories)

    # 删除 .ich 文件
    delete_files(root_directory, exclude_directories, file_patterns=['.ich'])

    input("按任意键继续...")