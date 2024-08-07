﻿import string_tools as st
import com_decorator as cd 
from com_log import logger as logger
import chardet

# 使用chardet模块检测文件的编码
def detect_encoding(file_path)->str:
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    logger.trace(f" {file_path} 检测到文件编码：{result}")
    # 返回检测到的编码
    return result['encoding'].lower()

# 获取文件路径
# file_path = r'F:\test_data\gbk.txt'

# 检测编码
# encoding = detect_encoding(file_path)

# # 使用检测到的编码打开文件
# with open(file_path, 'r', encoding=encoding) as f:
#     content = f.read()

# logger.info(content)



#读入文件
@cd.exception_decorator
def read_content_by_encode(source_path,source_encoding):
        with open(source_path, 'r',encoding=source_encoding) as file:
            content = file.read()
            return content
        return None
    
# 写到文件
@cd.exception_decorator
def write_content_by_encode(dest_path,dest_encoding,content):
        with open(dest_path, 'w',encoding=dest_encoding) as file:
            file.write(content)


# @cd.details_decorator
# @cd.timer_decorator
@cd.exception_decorator
def  operate_content_diff_encode( source_path,dest_path,source_encoding,dest_encoding="",operate_fun=None):
        content=read_content_by_encode(source_path,source_encoding)
        if content is None:
            return 
        
        is_same=True
        if operate_fun:
            result_content=operate_fun(content)
            if result_content ==content:
                if logger:
                    logger.trace(f"{source_path}:内容未被修改,保留原始内容")
            else:
                is_same=False
                content=result_content

        if dest_encoding=="":
            dest_encoding=source_encoding
        # 将处理后的content保存到B.txt文件中
        write_content_by_encode(dest_path,dest_encoding,content)

def replace_content_diff_encode( source_path,dest_path,source_encoding, dest_encoding="",replace_list_tuple=None):

    def replace_content(content:str)->str:
        return st.replace_list_tuple_str(content,replace_list_tuple)
    if dest_encoding=="":
        dest_encoding=source_encoding 
    operate_content_diff_encode(source_path, dest_path,source_encoding,dest_encoding,replace_content)

def operate_content_same_encode( source_path,dest_path,encoding, operate_fun):
    operate_content_diff_encode(source_path, dest_path,encoding, encoding,operate_fun)

def replace_content_same_encode( source_path,dest_path,encoding, replace_list_tuple):
    replace_content_diff_encode(source_path, dest_path,encoding,encoding,replace_list_tuple)


def convert_encode(source_path,dest_path,source_encoding,dest_encoding):
    operate_content_diff_encode(source_path, dest_path,source_encoding,dest_encoding,None)

#按推断的编码读入文件
def read_content(source_path):
    source_encoding = detect_encoding(source_path)
    with open(source_path, 'r',encoding=source_encoding) as file:
        content = file.read()
        return content
    return None


if __name__ == '__main__':

    replace_tuples=[
    ('法撒', 'A'),
    ('潍坊', 'CDE')
    ]



    replace_content_same_encode(r'F:\test_data\gbk.cpp',r'F:\test_data_output\gbk.cpp', "utf-8-sig", replace_tuples)
