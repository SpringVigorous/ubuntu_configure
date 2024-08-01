import path_tools as asp


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

def is_str_empty(str_value:str)->bool:
    if str_value is None:
        return True
    if len(str_value.strip())==0:
        return True
    return False    

#获取当前exe所在目录
def cur_execute_path():
    import os
    import sys
    return os.path.dirname(sys.argv[0])