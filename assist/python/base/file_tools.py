import string_tools as st
import com_decorator as cd 
from com_log import logger as global_logger

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
                if global_logger:
                    global_logger.info(f"{source_path}:内容未被修改,保留原始内容")
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




if __name__ == '__main__':

    replace_tuples=[
    ('法撒', 'A'),
    ('潍坊', 'CDE')
    ]



    replace_content_same_encode(r'F:\test_data\gbk.cpp',r'F:\test_data_output\gbk.cpp', "utf-8-sig", replace_tuples)
