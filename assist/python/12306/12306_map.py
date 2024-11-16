


import pandas as pd
import requests
import json
# 由于火车站使用三字码，所以我们需要先获取站点对应的三字码
def station_names():
    code_url = r"https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
    
    
    response = requests.get(code_url)
    response.encoding = 'utf-8'
    code_data = response.text
    # 处理每个匹配项，按 | 分割
    ls=code_data.split("@")[1:]
    # 处理每个匹配项，按 | 分割
    result = [match.split('|') for match in ls if match]
    return result

    
def all_to_excel(filepath):
        # 将结果输出到Excel文件
    df = pd.DataFrame(station_names())
    header=['简拼','站名','编码','全拼','缩称','站编号','城市编码','城市','国家拼音','国家','英文']
    df.to_excel(filepath, index=False, header=header)
    
def names_to_json(filepath):
    datas=station_names()
    dic=zip_dic(datas)
    with open(filepath,'w',encoding='utf-8') as f:
        json.dump(dic,f,ensure_ascii=False,indent=4)
# 处理获得的字符串，返回字典类型
def zip_dic(result:list):

    print(result)
    dic={}
    for item in result:
        dic[item[1]] = item[2]
    return dic

if __name__ == '__main__':
    # all_to_file('station_names.xlsx')
    names_to_json("city.json")
