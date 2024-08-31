import requests
from bs4 import BeautifulSoup
import os
import json
import warnings
from datetime import datetime
import hashlib

warnings.filterwarnings("ignore")
domain="https://edith.xiaohongshu.com"
headers={
    # "Host":"edith.xiaohongshu.com",
    # "Connection":"keep-alive",
"X-S-Common":"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",
"X-s":"XYW_eyJzaWduU3ZuIjoiNTQiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6ImI4NjI1ODM1ZWE3YjQ3MGMwMDM3OGNkZjVhYTE5ODVmYWQ3MzZhNzc4ODlhZjZkNjI0N2ExYzJmNWVjMDIwYWExMGQyODRiZTNlZWQwYTJjODBkYTcwM2MyY2Q3NDUyY2IzNzRmMGM1OTNhMTY4ODU2NWRlYThkMTIyOWY2YjZiOGZiYmZkMzEwZGUzMjI1MzgwZjc3ZTI1MWU0Njk1NTZlNjA5NjJiYzhiYzE0NDJmNDg0ZTBiMWQ1YTdiZTQ3ZmM4ZTNiNTk3Y2FmZWZhYzdmYTZhZjY2YTA2ZDA3OTBmOTU4NDBkYTAzZDFlMWJhMWYzMWUzZjYwYmU0NjBmY2I5M2JlMjg5NWI3MTk1MmVkYzBlNjBhZGQyZDhhMTZjYzY3NTIzMGRhNWVhNmI1ODE0YmEyMjBhMjQwMTA2NTZmZWViODYyNmU0OWQzYTRhZDUzY2Y0ZjFlMTc3OGY3YzY3MGYwMzA2MjY5NmRlOWIwYjE5NzkxMWY5YzQxNGFkOTcxZjNhNDVmYjAzNDg2MWU2ZjIyYjBhMDJhOWE1ZmNlIn0=",
"sec-ch-ua-platform":"Windows",

    
    
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Origin":"https://www.xiaohongshu.com",
    "Referer":"https://www.xiaohongshu.com/",
    "Cookie":"a1=19029c91c9erh6glnzwujndoez49q5pope7wjw49x00000858779; webId=04a7b350ba3ec00cc1ec563c2eca3319; gid=yj8JjSD22jU0yj8JjSjySdE4jdFxKk1IuE7VWjCIfldu4E88jA2UlV888Y2YWWj82i82D0fq; customer-sso-sid=68c517381709387753437817a2f255a13cd6a803; x-user-id-ark.xiaohongshu.com=5d593e3500000000010013c2; customerClientId=606764650847459; abRequestId=04a7b350ba3ec00cc1ec563c2eca3319; xsecappid=xhs-pc-web; webBuild=4.31.5; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=066dde38-c30a-4247-9c3e-427b2f9a183b; acw_tc=6f95f13a722b6d7b298df5821dc8b1140f013f209d3229ee41c1c0b6eec80981; unread={%22ub%22:%22647b4e33000000001203cd61%22%2C%22ue%22:%2264bd73ed000000001700cd10%22%2C%22uc%22:15};",
}
def  md5_str(s:str)->str:
        # 创建 MD5 哈希对象
    hash_object = hashlib.md5(s.encode())
    
    # 获取哈希值
    hash_hex = hash_object.hexdigest()
    
    return hash_hex
def time_flag():
    now = datetime.now()

    # 格式化为字符串
    formatted_now = now.strftime("%Y%m%d_%H:%M:%S")
    return formatted_now

def history_dir():
    return os.path.join(os.getcwd(),"history").strip()
def write_text(html,dir_name,file_name):
    cur_dir=os.path.join(history_dir(),dir_name)
    if not os.path.exists(cur_dir):
        os.makedirs(cur_dir)
    file_path= os.path.join(history_dir(),dir_name,f"{time_flag()}_{file_name}.html")  
        
    if os.path.exists(file_path):
        return
    with open(file_path,"w",encoding="utf-8") as f:
        f.write(html)
        
        
def get_sort_type(type:int):
    if type==0: 
        return "general"
    elif type==1:
        return "time_descending"
    else:
        return "popularity_descending"
# "time_descending" popularity_descending  general
def search_theme(name,sort_type:int=0):
    url=f"{domain}/api/sns/web/v1/search/notes"
    
    data={
	"keyword": name,
	"page": 1,
	"page_size": 100,
	"search_id": md5_str(name),
	"sort": get_sort_type(sort_type),
	"note_type": 0,
	"ext_flags": [],
	"image_formats": ["jpg", "webp", "avif"]
    }
    
    response=requests.post(url,headers=headers,data=data,verify=False)
    if response.status_code!=200:
        return None
    response.encoding='utf-8'
    content=response.text
    write_text(content,"search_theme",name)
    
    result=json.loads(content)
    items=result["data"]["items"]
    notes_info=[]
    for item in items:
        note_card=item["note_card"]
        user=note_card["user"]
        info={
            "note_id":item["id"],
            "xsec_token":item["xsec_token"],
            "note_title":note_card["display_title"],
            "user_id":user["user_id"],
            "user_name":user["nickname"]
        }
        
        notes_info.append(info)
    return  notes_info  
    
search_theme("薏米茶",0)

def search_note(theme_name,note_id,sec_token):
    url= 'https://edith.xiaohongshu.com/api/sns/web/v1/feed'
    # data={"source_note_id":"66b6ff4d0000000025030474","image_formats":["jpg","webp","avif"],"extra":{"need_body_topic":"1"},"xsec_source":"pc_search","xsec_token":"ABDdIhfVRQ94F88ukz7YQ3V_5y1tkEmUwPynyOnWGCLfc="}
    data={
    "source_note_id": note_id,
    "image_formats": [
        "jpg",
        "webp",
        "avif"
    ],
    "extra": {
        "need_body_topic": "1"
    },
    "xsec_source": "pc_search",
    "xsec_token": sec_token
}
    
    response=requests.post(url,headers=headers,data=data)
    if response.status_code!=200:
        return None

    response.encoding='utf-8'  
    content=response.text
    
    write_text(content,"search_note",theme_name)
       
    result=json.loads(content)
    
    card=result["data"]["items"]["note_card"]
    desc=card["desc"]
    
    images=[image["url_default"] for image in card["image_list"] ]
    tags=[image["name"] for image in card["tag_list"] ]
    title=card["title"]
    user=card["user"]
    user_id=user["user_id"]
    user_name=user["nickname"]
    
    
    os.makedirs(f"f:\\test\\{user_name}\\{title}\\images\\" ,exist_ok=True)
    
    # 保存文档
    with open(f"f:\\test\\{user_name}\\{title}\\info.txt","w",encoding="utf-8") as f:
        f.write(f"标题：{title}\n")
        f.write(f"作者：{user_name}\n")
        f.write(f"内容：{desc}\n")
        f.write(f"标签：{','.join(tags)}\n")
    
    #下载图片
    for index,url in enumerate(images):
        response=requests.get(url,headers=headers,verify=False)
        if response.status_code!=200:
            continue
        with open(f"f:\\test\\{user_name}\\{title}\\{index}.jpg","wb") as f:
            f.write(response.content)
    
    

print( search_note("66b6ff4d0000000025030474","ABDdIhfVRQ94F88ukz7YQ3V_5y1tkEmUwPynyOnWGCLfc="))

def fetch_data(url,data):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Origin': 'https://www.xiaohongshu.com',
        'Referer': 'https://www.xiaohongshu.com/',
        'Sec-Ch-Ua': '"Not A Brand";v="99", "Chromium";v="94"',
        'Sec-Ch-Ua-Mobile': '?1',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
        "Cookie": "abRequestId=d4e3ca0f-c055-5360-a3d4-4f1407cdb66f; a1=18cfcea02d3a9tl7cr9d1z7lwn9b2ca2ity09gq3r50000192651; webId=c91e9fb43ca5894ddb8e6a61ac1cb4fe; gid=yYSiSd0yWD3KyYSiSd08J9kAfq0j91WSFjfyvqFuW1EIj828DJS0Jj888yjJK2y8204d8yWj; customer-sso-sid=68c51738170911287553017032a01a7b52341276; x-user-id-ark.xiaohongshu.com=5d593e3500000000010013c2; customerClientId=148704461015132; OUTFOX_SEARCH_USER_ID_NCOO=338827736.2369468; xsecappid=xhs-pc-web; webBuild=4.31.5; websectiga=2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d; sec_poison_id=9f8755c9-459a-4cb4-bec6-ae07bdaf5e53; acw_tc=3956d42914c9752770e770110fa9465a8b66c1cfdb3a9dadf2357b6832462ace; web_session=040069b26ead56dc3c1f46d0fc344bfaf143ca; unread={%22ub%22:%2266c858d2000000001d03a749%22%2C%22ue%22:%2266b0a27d000000000d032d26%22%2C%22uc%22:33}",

    }
    response = requests.post(url, headers=headers,verify=False,data=data)
    response.encoding="utf-8"
    # response.raise_for_status()

    return response.text


    """
POST https://edith.xiaohongshu.com/api/sns/web/v1/feed HTTP/1.1
Host: edith.xiaohongshu.com
Connection: keep-alive
Content-Length: 203
sec-ch-ua: ";Not A Brand";v="99", "Chromium";v="94"
X-t: 1724488253954
x-b3-traceid: c38f263c6e6f10a0
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0
Content-Type: application/json;charset=UTF-8
Accept: application/json, text/plain, */*
X-S-Common: 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
X-s: XYW_eyJzaWduU3ZuIjoiNTQiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6Ijc1N2RhM2JhNjUzOGRmNWMxNDBlOTA1ZDg4NGY3MDJkZjdmNjY3YWU0NmI4OTY5NjA4YzkzOTQzNWVlYmNlY2Y4MzBhY2ZjMGIyOTY1Yjg5MGU0NGVkNjM2NDBhOTJiMzE3ZDhiYmEzYzBkY2JhNGE5OTA1YjI5NDBiMjJmZmE5YjRjZTU2N2RlNWYyYzgzZWQwNjNiYWZjM2VkNjMwMjZmMTA2N2NmZjc3NDE5M2E2ZTllODM5ZmMyMGViZGFjYWZhZDFhMzI3MzFhMGYwNzM5OTIwODlhODk4MzBhMzIwMzI5YjVhN2Q1YmUxMDJhODJlNWVmNzRhZmRhOWM2ZTdhNjA5OWVhNGI5YjdmNTVhMzZmODAwYzNhY2E4ZTA0ZDgzNDYyNmIxYWViMGFiNzhhZWRhMjkzMzU0ZTJkYzE5OGIyOTlkYjg1NmYzNGY5MTE5ZjlkMTA5YmZmMzFlZTQxMGExMWViZGQxOWE0YjlkNTU2YTlmZTQ3ZjkyZTQ2MzgwYjVjZDg0Mjc1MWY1NGM2MTg5Y2VkYjQyZWJiYTRmIn0=
sec-ch-ua-platform: "Windows"
Origin: https://www.xiaohongshu.com
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.xiaohongshu.com/
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: abRequestId=d4e3ca0f-c055-5360-a3d4-4f1407cdb66f; a1=18cfcea02d3a9tl7cr9d1z7lwn9b2ca2ity09gq3r50000192651; webId=c91e9fb43ca5894ddb8e6a61ac1cb4fe; gid=yYSiSd0yWD3KyYSiSd08J9kAfq0j91WSFjfyvqFuW1EIj828DJS0Jj888yjJK2y8204d8yWj; customer-sso-sid=68c51738170911287553017032a01a7b52341276; x-user-id-ark.xiaohongshu.com=5d593e3500000000010013c2; customerClientId=148704461015132; OUTFOX_SEARCH_USER_ID_NCOO=338827736.2369468; xsecappid=xhs-pc-web; webBuild=4.31.5; acw_tc=3956d42914c9752770e770110fa9465a8b66c1cfdb3a9dadf2357b6832462ace; web_session=040069b26ead56dc3c1f46d0fc344bfaf143ca; unread={%22ub%22:%2266c858d2000000001d03a749%22%2C%22ue%22:%2266b0a27d000000000d032d26%22%2C%22uc%22:33}; websectiga=2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d; sec_poison_id=5e02fb18-91b6-470d-be60-d593399d828a

{"source_note_id":"66b6ff4d0000000025030474","image_formats":["jpg","webp","avif"],"extra":{"need_body_topic":"1"},"xsec_source":"pc_search","xsec_token":"ABDdIhfVRQ94F88ukz7YQ3V_5y1tkEmUwPynyOnWGCLfc="} 
    
    
    """
def parse_notes(html):
    
    soup = BeautifulSoup(html, 'html.parser')
    notes = []
    
    # 假设笔记列表在 class 为 "note-list" 的 div 中
    note_list = soup.find('div', {'class': 'note-list'})
    if note_list:
        for note in note_list.find_all('div', {'class': 'note'}, limit=50):
            title = note.find('h2', {'class': 'title'}).text.strip()
            content = note.find('div', {'class': 'content'}).text.strip()
            images = [img['src'] for img in note.find_all('img')]
            videos = [video['src'] for video in note.find_all('video')]
            
            notes.append({
                'title': title,
                'content': content,
                'images': images,
                'videos': videos
            })
    
    return notes

def download_media(media_urls, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    media_files = []
    for url in media_urls:
        filename = os.path.join(directory, os.path.basename(url))
        if not os.path.exists(filename):
            response = requests.get(url)
            response.raise_for_status()
            with open(filename, 'wb') as file:
                file.write(response.content)
        media_files.append(filename)
    
    return media_files

import urllib.parse
def url_encode(s):
    encoded = urllib.parse.quote(s)
    return encoded
    # return encoded.replace("%", "%25")



def main(search_keyword:str):
    # base_url = f"https://www.xiaohongshu.com/search?keyword={url_encode(search_keyword)}&source=web_explore_feed&type=51"
    # base_url = f"https://www.xiaohongshu.com/search_result/"
    base_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
    
#    请求网址: https://edith.xiaohongshu.com/api/sns/web/v1/search/notes
# 请求方法: POST
# 状态代码: 200 
# 远程地址: [2402:4e00:1410::9890:edfe:f13a]:443
# 引荐来源网址政策: strict-origin-when-cross-origin
    
    
    
#     referer: https://www.xiaohongshu.com/
# sec-ch-ua: ";Not A Brand";v="99", "Chromium";v="94"
# sec-ch-ua-mobile: ?1
# sec-ch-ua-platform: "Android"
# sec-fetch-dest: empty
# sec-fetch-mode: cors
# sec-fetch-site: same-site
# user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36
    
    
    # params={"keyword": url_encode(search_keyword), "source": "web_explore_feed", "type": "51"}
    # params={"keyword":search_keyword,  "search_id": "2dmsm1oarqbdibay6x7f7"}
    params={"keyword":search_keyword,"page":1,"page_size":20,"search_id":"2do57j6diqpjlwgtp8okd"}
    # https://www.xiaohongshu.com/search_result?keyword=%25E5%259B%259B%25E7%25A5%259E%25E6%25B1%25A4&source=web_explore_feed
    
    html = fetch_data(base_url,params)
    with open(search_keyword + ".html", 'w', encoding='utf-8') as file:
        file.write(html)
        
    notes = parse_notes(html)
    
    output_dir = "xiaohongshu_notes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for idx, note in enumerate(notes, start=1):
        note_dir = os.path.join(output_dir, f"note_{idx}")
        os.makedirs(note_dir, exist_ok=True)
        
        # 保存笔记内容
        with open(os.path.join(note_dir, "note_content.txt"), 'w', encoding='utf-8') as file:
            file.write(f"Title: {note['title']}\nContent: {note['content']}\n")
        
        # 下载并保存图片
        image_files = download_media(note['images'], os.path.join(note_dir, "images"))
        
        # 下载并保存视频
        video_files = download_media(note['videos'], os.path.join(note_dir, "videos"))
        
        # 保存笔记数据
        with open(os.path.join(note_dir, "note_data.json"), 'w', encoding='utf-8') as file:
            json.dump(note, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main("四神汤")