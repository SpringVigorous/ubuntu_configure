import path_tools as asp
import  re
from datetime import datetime

asp.add_sys_path(__file__)

from com_decorator import exception_decorator






@exception_decorator
def replace_list_tuple_str(content:str,replace_list_tuple=None)->str:
    if not replace_list_tuple or len(replace_list_tuple)==0:
        return content
    for c, d in replace_list_tuple:
        if len(c)==0 : 
            continue
        content = content.replace(c, d)
    return content

def invalid(str_value:str)->bool:
    if str_value is None:
        return True
    if len(str_value.strip())==0:
        return True
    return False    

def equal_ignore_case(str1:str,str2:str)->bool:
    if invalid(str1) or invalid(str2):
        return False
    return str1.lower() == str2.lower()

#符合windows文件名命名规则
def sanitize_filename(filename:str):
    # 替换不允许的字符
    sanitized = re.sub(r'[\/:*?"<>| ]', '_', filename)
    sanitized=sanitized.strip().replace(' ','_')
    # 限制文件名长度
    max_length = 255
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def date_flag():
    current_time = datetime.now()
    return current_time.strftime('%Y%m%d')

#获取当前exe所在目录
def cur_execute_path():
    import os
    import sys
    return os.path.dirname(sys.argv[0])