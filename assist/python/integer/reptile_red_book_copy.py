import requests
from bs4 import BeautifulSoup
import os
import json
import re

# bilibili视频列表
# <li class="">
# <a href="/video/BV1uN4y1W7Du?p=8" class="router-link-active" title="8.Http协议（下）">
#     <div class="clickitem">
#         <div class="link-content">
#             <img src="//i0.hdslb.com/bfs/static/jinkela/video/asserts/playing.gif" style="display: none;">
#                 <span class="page-num">P8</span>
#                 <span class="part">8.Http协议（下）</span>
#             </div>
#             <div class="duration">06:18</div>
#         </div>
#     </a>
# </li>
def get_title_ref():
    # F:\test\ubuntu_configure\assist\python\integer\test\test.xml
    file_path=os.path.join( os.path.dirname(__file__),"test","test.xml")
    with open(file_path, 'r', encoding='utf-8') as f:
        # soup = BeautifulSoup(f.read(), 'html.parser')
        rg= re.compile(r'href="(?P<ref>.*?)".*?title="(?P<title>.*?)"', re.S)
        context=f.read()
        # all_title_ref=rg.findall(context)
        for title_ref in  rg.finditer(context):
            print(title_ref.group("ref").strip(),"\t",title_ref.group("title").strip())
            # print("https://www.bilibili.com"+title_ref.group("ref"))
        
get_title_ref()



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
        'X-B3-Traceid': '9199187cbbb78c5f',
    }
    response = requests.get(url, headers=headers,verify=False,params=data)
    response.encoding="utf-8"
    response.raise_for_status()

    return response.text

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
    # base_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/filters"
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
    params={"keyword":search_keyword,  "search_id": "2dmsm1oarqbdibay6x7f7"}
    
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