import pandas as pd

# 定义正则表达式模式


from urllib.parse import urlparse, parse_qs, urlencode
from pathlib import Path

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
