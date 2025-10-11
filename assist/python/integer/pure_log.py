import re

import sys
import os



# 使用绝对导入
from base.clipboard import to_clipboard, from_clipboard



def pure_log(input_str):
    # 定义正则表达式模式
    remove_code = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{1,}).*?Thread ID: \d+'
    
    # 使用正则表达式进行替换
    result = re.sub(remove_code, r'\1', input_str, flags=re.DOTALL)

    split_pre=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{1,})-(.*?)(详情.*?)(?:(耗时.*?))?\n'
    # 使用正则表达式进行匹配
    matches = re.findall(split_pre, result, re.DOTALL)
    # 输出匹配结果
    # 拼接匹配结果

    results ="\n".join( ["\t".join([item for item in match if str(item)])   for match in matches])
    # print(results)
    return results


def main():
    org_str=from_clipboard()
    if org_str[-1]!="\n":
        org_str+="\n"
    result=pure_log(org_str.replace("\r",""))

    # print(result)
    to_clipboard(result)

    
if __name__ == "__main__":
    # 示例输入字符串
    input_str = """
    2024-09-26 17:35:05,292-【异步写入文件,mode:wb,encoding:None】-【开始】详情：F:/worm_practice/red_book/notes/健脾养胃/脾胃正确调理顺序_按这四步走🔥/images/5.webp
    2024-09-26 17:35:05,292-redbook_threads-TRACE- com_log.py:15 -trace()-TRACE-Thread ID: 4952-【异步写入文件,mode:wb,encoding:None】-【开始】详情：F:/worm_practice/red_book/notes/健脾养胃/脾胃正确调理顺序_按这四步走🔥/images/5.webp
    """
    main()
