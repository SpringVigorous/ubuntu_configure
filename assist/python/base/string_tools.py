﻿# import path_tools as asp
import  re
from datetime import datetime
from bs4 import BeautifulSoup
# asp.add_sys_path(__file__)

from com_decorator import exception_decorator
import hashlib
import os
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
def hash_text(text, algorithm='sha256',max_length=8,strict_no_num=False):
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
    result=hex_dig[:max_length]
    if strict_no_num :
        for item in set(re.findall(r'\d',result)):
            new_val=chr(ord('A')+ord(item)-ord('0')) 
            result=result.replace(item,new_val)

    
    
    return result

# 秒时间戳
def convert_seconds_to_datetime(seconds:int):
    # 将秒时间戳转换为 datetime 对象
    dt = datetime.fromtimestamp(seconds)
    
    # 格式化 datetime 对象为年月日时分秒格式
    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date
    

def replace_punctuation_with_newline(text):
    # 使用正则表达式匹配一个或多个连续的标点符号
    result = re.sub(r'[^\w\s]', '\n', text)
    # 使用正则表达式将多个连续的换行符替换为一个换行符
    result = re.sub(r'\n+', '\n', result)
    return result
    



def rename_files_with_pattern(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 使用正则表达式匹配文件名中含有“~”后跟数字的情况
            match = re.match(r'(.*)~(\d+)(.*)', file)
            if match:
                original_path = os.path.join(root, file)
                new_name = f"{match.group(1)}{match.group(3)}"
                new_path = os.path.join(root, new_name)
                
                # 如果新路径的文件存在，则先删除它
                if os.path.exists(new_path):
                    print(f'File {new_path} already exists. Deleting it...')
                    # continue
                    os.remove(new_path)
                
                # continue
                # 将原始文件重命名为新路径
                os.rename(original_path, new_path)
                print(f'Renamed: {original_path} -> {new_path}')




# 正则表达式匹配大写数字
chinese_num = r'零一二三四五六七八九十百千万亿壹贰叁肆伍陆柒捌玖拾佰兆'
chinese_num_pattern = re.compile(f'[{chinese_num}]+')

# 大写数字到阿拉伯数字的映射
chinese_to_arabic = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000,
    '壹':1,'贰':2,'叁':3,'肆':4,'伍':5,'陆':6,'柒':7,'捌':8,'玖':9,'拾':10,'佰':100,'仟':1000,'兆':1000000000,
    "两":2,
}

def extract_chinese_numbers(text):
    """
    提取字符串中的大写数字部分。

    :param text: 输入字符串
    :return: 包含所有大写数字部分的列表
    """
    matches = chinese_num_pattern.findall(text)
    return matches


def chinese_to_arabic_number(chinese_num):
   
    if not chinese_num_pattern.match(chinese_num):
        raise ValueError("输入不是有效的中文数字")
    

    unit = 1
    num = 0
    count=len(chinese_num)
    for index,char in enumerate(reversed(chinese_num)):
        if char in chinese_to_arabic:
            cur_val=chinese_to_arabic[char]
            
            if cur_val >= 10:
                unit = cur_val
                if index+1==count:
                     num += 1 * unit
            else:
                num += cur_val * unit
        else:
            raise ValueError(f"未知字符: {char}")
    

    return num

def arabic_number_tuples(str_val):
    org=extract_chinese_numbers(str_val)
    vals=list(map(chinese_to_arabic_number,  org))

    # 提取数字
    num_org=re.findall(r'\d+',str_val)
    if num_org:
        org.extend(num_org)
        vals.extend(map(int,num_org))
    return list(zip(org,vals)) if vals else []

def arabic_numbers(str_val):
    items=arabic_number_tuples(str_val)
    return [item[-1] for item in items if item] if items else []

if __name__ == '__main__':

    # 测试
    print(chinese_to_arabic_number("二百零三"))  # 输出: 203
    

    exit(0)
    org_str="朋友们，今天带来北京旅游攻略！首先是天安门，宏伟壮观。一定要早起去看升旗仪式，热血沸腾。接着前往圆明园，在残垣断壁中感受历史的厚重。北京之行，这几个地方必去，快来感受京城的独特魅力！"
    
    print(replace_punctuation_with_newline(org_str))
    exit(0)
    print(convert_seconds_to_datetime(1736778814092))
    exit(0)
    print(sanitize_filename('痤疮痘跟风喝了一个月的金银花水..'))
    #替换连续重复字符，只保留一个
    list_tuple=[(r'(.)\1+',r"\1",True,False),
                ("He","Ki")]
    replace_list_tuple_str("Hello,Kitty",list_tuple)
    
    data={"replace_args":list_tuple}
    import json
    print(json.dumps(data,ensure_ascii=False,indent=4))