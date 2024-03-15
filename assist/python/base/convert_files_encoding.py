# 导入所需模块
import os
import codecs

import check_file_encode as ce
import fold_tools as fs
import file_tools as fc
from com_log import logger as global_logger
# 定义函数：将文件内容从源编码转换为目标编码
def convert_file_encoding(file_path, dest_path, source_encoding, dest_encoding):
    """
    该函数用于读取指定路径的文件，根据给定的源编码进行解码，
    然后以目标编码写入到新的文件路径中。
    
    参数：
    file_path (str): 源文件路径
    dest_path (str): 目标文件路径
    source_encoding (str): 源文件的字符编码
    dest_encoding (str): 目标文件的字符编码
    """
    # # 使用codecs模块打开源文件以读取指定编码（如GBK）
    # with codecs.open(file_path, 'r', encoding=source_encoding) as input_file:
    #     content = input_file.read()
        
    # # 可选步骤：根据需要调整换行符（注释掉了此部分代码）
    # # if content.find('\r\n') == -1:
    # #     content = content.replace('\n', '\r\n')
    
    # # 使用目标编码写入到新文件
    # with codecs.open(dest_path, 'w', encoding=dest_encoding) as output_file:
    #     output_file.write(content)

    fc.convert_encode(file_path,dest_path,source_encoding,dest_encoding)

# 定义辅助函数：自动检测源文件编码并转换为指定的目标编码
def convert_file_to_dest_encoding(file_path, dest_path, dest_encoding):
    """
    此函数调用 `convert_file_encoding` 函数，并利用 `check_file_encode` 模块自动检测源文件的编码。

    参数：
    file_path (str): 源文件路径
    dest_path (str): 目标文件路径
    dest_encoding (str): 目标文件的字符编码
    """
    source_encoding =ce.detect_encoding(file_path)
    if global_logger:
        global_logger.debug(file_path, "源编码:", source_encoding, "目标编码:", dest_encoding)
    if source_encoding!= dest_encoding:
        convert_file_encoding(file_path, dest_path, source_encoding, dest_encoding)

# 定义函数：递归遍历目录，将符合条件的文本文件转换为目标编码
def convert_folder_dest_encoding(input_folder, file_filter, dest_folder, dest_encoding):
    """
    遍历指定输入文件夹中的所有子目录和文件，
    对于符合文件过滤条件的文本文件，将其转换为指定的目标编码，并保存在指定的输出目录结构下。

    参数：
    input_folder (str): 输入文件夹路径
    file_filter (list): 文本文件筛选规则（这里假设是文件扩展名为 .txt 的文件）
    dest_folder (str): 输出文件夹路径
    dest_encoding (str): 目标文件的字符编码
    """
    filters_tuple=tuple(file_filter)
    for root, dirs, files in os.walk(input_folder):
        # 构建输出文件路径
        relative_path = os.path.relpath(root, input_folder)
        dest_dir_path = os.path.join(dest_folder, relative_path)
        for file_name in files:
            # 判断当前文件是否满足文本文件筛选条件
            # file_extension=os.path.splitext(file_name)[1].lower()
            # if  not file_filter  or  file_extension in [ext.lower() for ext in file_filter]:
            if  not file_filter  or  file_name.endswith(filters_tuple):
                org_file_path = os.path.join(root, file_name)

                # 计算输出文件的目录路径，并创建不存在的目录
                # dest_dir_path = root.replace(input_folder, dest_folder)
                os.makedirs(dest_dir_path, exist_ok=True)

                # 计算输出文件的完整路径
                dest_path = os.path.join(dest_dir_path, file_name)
                
                # 调用转换文件编码的函数
                convert_file_to_dest_encoding(org_file_path, dest_path, dest_encoding)

# 定义封装函数：根据输入参数自动创建输出文件夹并调用转换目录内文本文件编码的函数
def convert_folder_encoding(input_folder, file_filter, dest_encoding):
    """
    创建一个与输入文件夹同名但带有 "_output" 后缀的新文件夹作为输出目录，
    并调用 `convert_folder_dest_encoding` 函数将符合条件的文本文件编码转换为指定的目标编码。

    参数：
    input_folder (str): 输入文件夹路径
    file_filter (list): 文本文件筛选规则（这里假设是文件扩展名为 .txt 的文件）
    dest_encoding (str): 目标文件的字符编码
    """
    # dest_folder = os.path.join(os.path.dirname(input_folder), 
    #                            os.path.basename(input_folder) + "_output")
    dest_folder = input_folder+"_output"
    fs.clear_folder(dest_folder)
    # os.makedirs(dest_folder, exist_ok=True)
    convert_folder_dest_encoding(input_folder, file_filter, dest_folder, dest_encoding.lower())



if __name__ == "__main__":
    # 使用示例：将 "F:\test_data" 文件夹下所有 .txt 文件编码转换为 utf-8-sig
        #gbk，gb2312,ascii,utf8,utf-8-sig
    convert_folder_encoding(r"F:\test_data", [".txt"], 'utf-8-sig')