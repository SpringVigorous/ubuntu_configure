import os





from pathlib import Path

import sys
import pandas as pd




from base import find_all,arabic_numbers

def get_unmatched_info(input_string):
    # 正则表达式模式
    pattern = r'【([^】]+)】-【未匹配标题: ([^】]+)】详情：([^,]+)'
    keys=["title","chapter","url"]
    results=find_all(input_string,pattern,keys)
    return results

def get_unmatched_info_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        input_string = file.read()
    results=get_unmatched_info(input_string)
    return pd.DataFrame(results)
def get_unmatched_info_from_dir(dir_path):
    results=[]
    for root, _, files in os.walk(dir_path):
        for file in files:
            if not (file.endswith('.log') and "trace" in file):
                continue
            file_path = os.path.join(root, file)
            df=get_unmatched_info_from_file(file_path)
            if df.shape[0]>0:
                results.append(get_unmatched_info_from_file(file_path))
    
    
    df=pd.concat(results, axis=0).drop_duplicates(subset='url',ignore_index=True)
    return df
 
if __name__ == "__main__":

    df=get_unmatched_info_from_dir(r"F:\worm_practice\logs\story")
    
    
    
    df["num"]=df["chapter"].apply(lambda x: arabic_numbers(x)[0] if arabic_numbers(x) else 0)
    
    df.to_excel(r"F:\worm_practice\logs\story\unmatched_info.xlsx",index=True)
    
    exit(0)
    
    # 输入字符串
    input_string = """2025-03-04 14:26:44,791-WARNING-Thread ID: 9580-【我在乱世娶妻长生】-【未匹配标题: 第两百一十七章 婉】详情：https://www.nlxs.org/104/104522/2/,耗时：0.000秒
    2025-03-04 14:26:44,791-WARNING-Thread ID: 9580-【我在乱世娶妻长生】-【未匹配标题: 第两百十七章 婉】详情：https://www.nlxs.org/104/104522/2/,耗时：0.000秒
    2025-03-04 14:26:44,791-WARNING-Thread ID: 9580-【我在乱世娶妻长生】-【未匹配标题: 第两百二十七章 婉】详情：https://www.nlxs.org/104/104522/2/,耗时：0.000秒
    """
    results=get_unmatched_info(input_string)
    print(results)
