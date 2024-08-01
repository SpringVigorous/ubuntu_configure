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
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)


            