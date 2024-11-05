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
        
        if os.path.isdir(abs_path):
            delete_directory(abs_path)
        else:
            os.remove(abs_path)

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


            