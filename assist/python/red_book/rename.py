import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog

import logging
import appdirs
import sys

import re

import __init__
from base.com_log import logger as logger
# print(sys.path)

#判断一个字符串是否满足Windows文件名的要求（仅文件名和后缀不能包含 父目录）
# 以下是不允许出现在Windows文件名中的字符：
# < 和 >
# : 和 |
# ", ', 和 ?
# \ 和 /
# 任何控制字符（ASCII值小于32的字符）
# 此外，文件名不能超过255个字符（对于大多数情况）。
def is_valid_windows_filename(filename):
    # 检查是否包含非法字符
    illegal_chars_pattern = r'[\\/:*?"<>|\r\n]+'
    if re.search(illegal_chars_pattern, filename):
        return False
    
    # 检查长度是否超过限制
    if len(filename) > 255:
        return False
    
    # 检查是否以句点或空格结尾
    if filename.endswith('.') or filename.endswith(' '):
        return False
    
    return True
# 判断是否为Windows系统文件路径
def is_valid_windows_path(path):
# 正则表达式，用于匹配Windows文件路径
    pattern = r'^[a-zA-Z]:\\(?:[^<>:"\/\\\|\?\*]+\\)*[^<>:"\/\\\|\?\*]+$'
    return bool(re.match(pattern, path.replace('/', '\\')))






# 获取当前运行的 exe 文件的完整路径
def get_cur_path():
    return os.path.abspath(sys.argv[0])

def get_cur_name():
    
    # 使用 os.path.splitext() 分离文件名和后缀
    file_name, extension = os.path.splitext(os.path.basename(get_cur_path()))
    return file_name

# 获取 exe 文件所在的目录
def get_cur_dir():
    return os.path.dirname(get_cur_path())

# 获取用户文档目录
def get_user_dir()->str:
    
    documents_dir = appdirs.user_data_dir(appname=None, appauthor=None)
    if documents_dir is None or len(documents_dir)==0:
        # 在Windows上，Documents目录可能在"My Documents"下
        if os.name == 'nt':
            documents_dir = os.path.join(os.getenv('USERPROFILE'), 'Documents')
    return documents_dir


def create_dir_recursive(path)->bool:
    if os.path.exists(path):
        logger.trace(f"Directory already exists: {path}")
        return True
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Directory created: {path}")
        return True
    except OSError as error:
        logger.error(f"Directory creation failed: {error}")
        return False
        
 
def is_xlsx(filename):
    return os.path.splitext(filename)[1].lower() == '.xlsx'

def error_message(prefix,message,postfix):
    logger.error(f"{prefix} {message} {postfix}")
    
def check_file_extension(curfilename,reference_file_path)->str:
    
    __, file_extension = os.path.splitext(curfilename)
    if(len(file_extension)==0):
        error_message("文件名","缺少后缀","，请重新输入！")
        curfilename+=os.path.splitext(reference_file_path)[1]
    
    return curfilename

def rename_files(file_path,sheetName):
    if not is_xlsx(file_path):
        logger.error("File is not an Excel file.")
        return
    
    
    
# 读取 Excel 文件的第一个工作表
    df = pd.read_excel(file_path, sheet_name=sheetName)
    logger.trace(f"Excel file read: {file_path}; data:\n{df}")
    
    # 使用fillna()函数将所有NaN替换为空字符串
    df.fillna("", inplace=True)
    
    # 遍历 DataFrame 的每一行

    for index, row in df.iterrows():
        # 获取原始文件路径和新的文件路径
        old_path =str(row[0]).strip()
        new_path = str(row[1]).strip()
        info_pre=f"第{index+1}行: "
        
        error_later=f"File renamed failed: {old_path} -> {new_path}"
        
        has_error=True
        if(len(old_path)==0):
            error_mid=f";reason: orginal path为 空"
        elif len(new_path)==0:
            error_mid=f";reason: new path为 空"
        elif os.path.exists(old_path) == False:
            error_mid=f";reason: orginal path {old_path} 不存在"
        elif old_path.lower() == new_path.lower():
            error_mid=f";reason: New file name is the same as the old file name"
        elif not is_valid_windows_path(old_path):
            error_mid=f";reason: {old_path} is not a valid Windows file path"
        else:
            has_error=False
        
        if has_error:
            error_message(info_pre,error_later,error_mid)
            continue
        
        
        # 确保新文件名为全路径
        if not os.path.isabs(new_path):
            new_path = os.path.join(os.path.dirname(old_path),new_path)
            create_dir_recursive(os.path.dirname(new_path))
        new_path=check_file_extension(new_path,old_path)
        
        
        # 使用 os.rename() 重命名文件
        try:
            os.rename(old_path, new_path)
            logger.info(f"{info_pre}File renamed: {old_path} -> {new_path}")
        except FileNotFoundError:
            logger.error(f"{info_pre}File not found: {old_path}")
        except FileExistsError:
            logger.error(f"{info_pre}New file already exists: {new_path}")
        except Exception as e:
            logger.error(f"{info_pre}An error occurred: {e}")
            
            


def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    # 将主窗口提升到最前面
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    file_path = filedialog.askopenfilename(
        title="选择修改文件名称的 Excel 文件",  # 弹出对话框的标题
        filetypes=(("Excel文件", "*.xlsx"),  # 文件类型过滤器
                   ("Excel文件", "*.xls")),
        initialdir=get_cur_dir())
    
    return file_path



            
if __name__ == '__main__':
    # 调用函数打开文件选择对话框
    file_path = open_file_dialog()
    logger.info(f"Selected file: {file_path}")
    
    sheetName = 0
    rename_files(file_path,sheetName)
    
    print("Script execution complete.")
    os.system("pause")
    
    # 打包说明：pyinstaller --onefile --distpath exe -p . --distpath .\exe rename.py
# 生成.\exe\ThemeCount.exe，运行即可
