
from urllib.parse import urlparse, parse_qs, urlencode,urljoin
import re
import requests
from lxml import html
import pandas as pd
from pathlib import Path
from itertools import chain
from xml_tools import pretty_tree
from collect_tools import unique
from urllib.parse import urlparse

def url_valid(url:str):
    parsed_url = urlparse(url)
    return parsed_url.netloc
def fix_url(url: str, base_scheme: str = "https:") -> str:
    if not url or not isinstance(url,str):  # 如果url为空，则返回None
        return url
    parsed_url = urlparse(url)
    if not parsed_url.scheme in ["http", "https"]:
        return urljoin(base_scheme, url)
    return url
    # """将不完整的URL（如 //example.com）转换为完整URL（如 https://example.com）"""
    # if url.startswith(("http://", "https://")):
    #     return url  # 已经是合法URL，直接返回
    # return urljoin(base_scheme, url)  # 拼接协议

def get_homepage_url(url):
    """
    从给定的网址中提取主页地址。

    :param url: 要处理的网址
    :return: 提取的主页地址
    """
    # 解析 URL
    parsed_url = urlparse(url)
    
    # 构建主页地址
    homepage_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    return homepage_url


def is_http_or_https(url):
    """
    判断字符串是否以 http 或 https 开头。

    :param url: 要检查的字符串
    :return: 如果字符串以 http 或 https 开头，返回 True；否则返回 False
    """
    # 定义正则表达式模式
    pattern = r'^https?://'
    
    # 使用 re.match 检查字符串是否匹配模式
    match = re.match(pattern, url)
    
    # 返回匹配结果
    return bool(match)

def fill_url(url,domain):
    if not is_http_or_https(url):
        return f"{domain}{url}"
    return url

def get_url(str_val:str):
    pattern = r'https?://[^\s]+'
    urls = re.findall(pattern, str_val)
    return urls


#读取url,返回文档树对象（None)
def content_tree(url,logger=None,**kargs):
    content=""
    try:
        response = requests.get(url, **kargs)
        if response.status_code != 200:
            if logger:
                logger.warn("失败")
            return
        content=response.content
    except:
        if logger:
            logger.warn("失败")
        return
    tree = html.fromstring(content)
    return tree

def postfix(url):
        # 解析 URL
    parsed_url = urlparse(url)

    # 提取网址部分
    cur_path=Path(parsed_url.path)
    return cur_path.suffix

def split_url(url):

    # 解析 URL
    parsed_url = urlparse(url)

    # 提取网址部分
    base_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

    # 提取查询参数部分
    query_params = parsed_url.query

    # 将查询参数转换为字典
    query_dict = parse_qs(query_params)
    for key, value in query_dict.items():
        query_dict[key] = value[0] if len(value) == 1 else value
    data={"base_url":base_url}
    data.update(query_dict)
    return data
    # 将字典转换为查询参数字符串
    # query_string = urlencode(query_dict)


def merge_url(df,keys:list):
    # print(df)
    url=df["base_url"]
    query_dict={key:df[key] for key in keys }
    return f"{url}?{urlencode(query_dict)}"




def arrange_urls(url_list:list)->list[dict]:
    if not url_list: return []
    lst=[]
    for duration,url in url_list:
        item={"duration":float(duration)}
        item.update(split_url(url))
        lst.append(item)
    
    keys_param= [key  for key in lst[0].keys() if key not in ["base_url","start","end","duration"]]
    if not keys_param:
        return [ {"url":item["base_url"] ,"duration":item['duration']}  for item in lst]
    
    def unique_same_url(df):
        # print(df)
        duration=df["duration"].agg("sum")
        df_unique = df.drop_duplicates(subset=keys_param)
        # print(df_unique)
        df_unique.loc[:,"duration"]=duration
        return df_unique

    df=pd.json_normalize(lst)
    group_df= df.groupby("base_url",sort=False).apply(unique_same_url, include_groups=False).reset_index()
    group_df["url"]=group_df.apply(lambda row: merge_url(row,keys_param),axis=1)
    return group_df[["url","duration"]].to_dict(orient="records",index=True)



def remove_html_entity(text):
    # 使用正则表达式替换HTML实体
    import re
    
    
    # text = re.sub(r'&nbsp;', ' ', text)
    # text = re.sub(r'&amp;', '&', text)
    # text = re.sub(r'&lt;', '<', text)
    # text = re.sub(r'&gt;', '>', text)
    # text = re.sub(r'&quot;', '"', text)
    # text = re.sub(r'&apos;', "'", text)

    text = re.sub('\xa0', '', text)
    
    
    return text

def get_node_text(node):
    if node is None:
        return ""
    if not isinstance(node,(list|tuple)):
        node=[node]
    return [ remove_html_entity(''.join(item.itertext())).strip()  for item in node if item is not None]


# 递归函数提取指定属性的值
def __extract_attribute(node, attribute):
    values = []
    # 检查当前节点是否有指定属性
    if node.get(attribute):
        values.append(node.get(attribute))
    # 递归检查子节点
    for child in node:
        values.extend(__extract_attribute(child, attribute))
    return values






 
def get_node_attr(node,attr):
    
    if node is None:
        return ""
    if not isinstance(node,(list|tuple)):
        node=[node]
    lst= [__extract_attribute(item,attr) for item in node if item is not None]
    return [item for item in chain.from_iterable(lst) if item]
    
        
def get_node_sub_hrefs(tree,cur_xpath,sub_xpath,href_flag="href",domain=None,flag_info=None,logger=None):
    lis_all = tree.xpath(cur_xpath)
    log_info=f"获取{flag_info}失败"
    if not lis_all :
        if logger:
            logger.warn(log_info,f"\n{pretty_tree(tree)}\n")
        return []
    # for div in lis_all:
    #     print(html.tostring(div, pretty_print=True, encoding='unicode'))
    
    div=lis_all[0]
    hrefs=unique(map(lambda x: fill_url(x,domain), get_node_attr(div.xpath(sub_xpath),href_flag)))
    if not hrefs and  logger:
        logger.warn(log_info,f"\n{pretty_tree(div)}\n")
    return hrefs 

def get_param_from_url(url:str,key:str):
    if not url or not key:
        return None
    
    
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get(key, [None])[0]




