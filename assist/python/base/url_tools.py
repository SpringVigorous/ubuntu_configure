
from urllib.parse import urlparse
import re
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