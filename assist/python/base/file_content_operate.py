import base.string_tools as st

def  operate_content_diff_encode( source_path,dest_path,source_encoding,dest_encoding="",operate_fun=None):
    # 打开并读取A.txt文件内容到字符串content中
    with open(source_path, 'r',encoding=source_encoding) as file:
        content = file.read()

    if operate_fun:
        content=operate_fun(content)

    if dest_encoding=="":
        dest_encoding=source_encoding
    # 将处理后的content保存到B.txt文件中
    with open(dest_path, 'w',encoding=dest_encoding) as file:
        file.write(content)

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
