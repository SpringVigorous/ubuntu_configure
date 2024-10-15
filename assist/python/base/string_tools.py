import path_tools as asp
import  re
from datetime import datetime

asp.add_sys_path(__file__)

from com_decorator import exception_decorator


#根据原始的大小写情况，替换成目标的大小写
def replace_pattern(match, replacement):
    original = match.group(0)
    if original.islower():
        return replacement.lower()
    elif original.isupper():
        return replacement.upper()
    else:
        # 如果是首字母大写的情况
        return replacement.capitalize()




#支持正则替换 内容为：[(origin_val, new_val,is_regex,is_ignore_case)]
@exception_decorator()
def replace_list_tuple_str(content:str,replace_list_tuple=None)->str:
    if not replace_list_tuple or len(replace_list_tuple)==0:
        return content
    for origin_val, new_val,*extra0 in replace_list_tuple:
        if len(origin_val)==0 : 
            continue
        extra_count=len(extra0)
        is_regex=extra_count>0 and extra0[0] 
        is_ignore_case =extra_count>1 and extra0[1] 
        if not is_regex:
            content = content.replace(origin_val, new_val)
        elif is_ignore_case:
            content= re.sub(origin_val, lambda m: replace_pattern(m, new_val), content,  flags=re.IGNORECASE) # 忽略大小写
        else:
            content = re.sub(origin_val, new_val, content)
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
    sanitized = re.sub(r'[\/:*?"<>| \.]', '_', filename)
    sanitized=sanitized.strip().replace(' ','_')
    # 限制文件名长度
    max_length = 255
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def date_flag():
    current_time = datetime.now()
    return current_time.strftime('%Y%m%d')

def datetime_flag():
    current_time = datetime.now()
    return current_time.strftime('%Y%m%d%H%M%S')

#获取当前exe所在目录
def cur_execute_path():
    import os
    import sys
    return os.path.dirname(sys.argv[0])


if __name__ == '__main__':
    print(sanitize_filename('痤疮痘跟风喝了一个月的金银花水..'))
    #替换连续重复字符，只保留一个
    list_tuple=[(r'(.)\1+',r"\1",True,False),
                ("He","Ki")]
    replace_list_tuple_str("Hello,Kitty",list_tuple)
    
    data={"replace_args":list_tuple}
    import json
    print(json.dumps(data,ensure_ascii=False,indent=4))