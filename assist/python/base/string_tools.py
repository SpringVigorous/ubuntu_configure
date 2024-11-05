# import path_tools as asp
import  re
from datetime import datetime
from bs4 import BeautifulSoup
# asp.add_sys_path(__file__)

from com_decorator import exception_decorator
import hashlib

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
def sanitize_filename(filename:str,limit_length=80):
    # 替换不允许的字符
    sanitized = re.sub(r'[\/:*?"<>| \.]', '_', filename)
    sanitized=sanitized.strip().replace(' ','_')
    # 限制文件名长度

    if len(sanitized) > limit_length:
        sanitized = sanitized[:limit_length]
    
    return sanitized


def date_flag():
    current_time = datetime.now()
    return current_time.strftime('%Y%m%d')

def datetime_flag():
    current_time = datetime.now()
    return current_time.strftime('%Y%m%d%H%M%S')

#获取当前exe所在目录
def exe_dir(exe_path:str=None):
    import os
    import sys
    return os.path.dirname(sys.argv[0] if not exe_path  else exe_path)

#字符串转换为 html 表格，每行用换行符分割，每列用制表符分割
def convert_to_html_table(table_str,row_split="\n",col_split="\t"):
    # 按行分割字符串
    lines = table_str.strip().split(row_split)
    
    # 创建 HTML 表格的开头和结尾标签
    html_table = '<table border="1">\n'
    
    # 遍历每一行
    for line in lines:
        # 按制表符分割行
        columns = line.split(col_split)
        
        # 创建表格行标签
        html_table += '  <tr>\n'
        
        # 遍历每一列
        for column in columns:
            # 创建表格单元格标签
            html_table += f'    <td>{column}</td>\n'
        
        # 结束表格行标签
        html_table += '  </tr>\n'
    
    # 结束 HTML 表格标签
    html_table += '</table>'
    
    return html_table

# html 表格 转换为 字符串，每行用换行符分割，每列用制表符分割
def html_table_to_str(html_table,row_split="\n",col_split="\t"):
    # 使用 BeautifulSoup 解析 HTML 表格
    soup = BeautifulSoup(html_table, 'html.parser')
    
    # 提取表头
    header_row = soup.find('thead').find('tr')
    datas = [[th.get_text() for th in header_row.find_all('th')]]
    
    # 提取表格数据
    data_rows = soup.find('tbody').find_all('tr')

    for row in data_rows:
        datas.append([td.get_text() for td in row.find_all('td')])
    
    # 将表头和数据转换为以 \n 和 \t 分割的字符串

    
    return  "\n".join(['\t'.join(row) for row in datas])
    

# md5
# sha1
# sha224
# sha256
# sha384
# sha512
# blake2b
# blake2s
# sha3_224
# sha3_256
# sha3_384
# sha3_512
# shake_128
# shake_256
def hash_text(text, algorithm='sha256',max_length=8):
    """
    计算文本的哈希值并返回字符串形式的哈希值。

    :param text: 要哈希的文本
    :param algorithm: 哈希算法，可选值有 'md5', 'sha1', 'sha256' 等
    :return: 字符串形式的哈希值
    """
    # 创建哈希对象
    hash_object = hashlib.new(algorithm)
    
    # 更新哈希对象的数据
    hash_object.update(text.encode('utf-8'))
    
    # 获取哈希值的十六进制表示
    hex_dig = hash_object.hexdigest()
    
    return hex_dig[:max_length]

    
    

if __name__ == '__main__':
    print(sanitize_filename('痤疮痘跟风喝了一个月的金银花水..'))
    #替换连续重复字符，只保留一个
    list_tuple=[(r'(.)\1+',r"\1",True,False),
                ("He","Ki")]
    replace_list_tuple_str("Hello,Kitty",list_tuple)
    
    data={"replace_args":list_tuple}
    import json
    print(json.dumps(data,ensure_ascii=False,indent=4))