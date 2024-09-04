from DrissionPage import WebPage
from DrissionPage.common import Actions
from pprint import pprint
import os
import time
import json
from requests.structures import CaseInsensitiveDict
import requests
import sys


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import __init__
from base.com_log import logger as logger
import base.setting as setting
from collections import namedtuple



            
def write_to_file( file_name):
    request_dic={
        "request_url":request_url,
        "request_headers":request_headers,
        "request_datas":request_datas,
        "request_cookies":request_cookies,
        "request_response":response.body,
    }
    cur_dir=setting.redbook_history_dir
    dest_path=os.path.join(cur_dir,
    f"page_{page_id}.json")
    os.makedirs(os.path.dirname(dest_path),exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(request_dic,
        f,indent=4,ensure_ascii=False)
            
        
import datetime

def convert_milliseconds_to_datetime(milliseconds):
    # 将毫秒时间戳转换为秒时间戳
    seconds = milliseconds / 1000.0
    
    # 将秒时间戳转换为 datetime 对象
    dt = datetime.datetime.fromtimestamp(seconds)
    
    # 格式化 datetime 对象为年月日时分秒格式
    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date

# def GetNotesbyThemeText(theme_text,root_dir,headers):
#     for note_key in GetNotesKey(theme_text):
#         url="https://edith.xiaohongshu.com/api/sns/web/v1/feed"
#         data={
#             "source_note_id": note_key.id,
#             "image_formats": ["jpg", "webp", "avif"],
#             "extra": {
#                 "need_body_topic": "1"
#             },
#             "xsec_source": "pc_search",
#             "xsec_token": note_key.xsec_token
#             }
#         note_respond=requests.post(url,headers=headers,data=data)
#         if note_respond.status_code!=200:
#             continue
#         note_respond.encoding="utf-8"
#         note_data=note_respond.json()["data"]
#         note_info=note_data["items"](0)
        
#         id=note_info["id"]
#         model_type=note_info["model_type"]
#         topics=[ tag["name"] for tag in note_info["note_card"]["tag_list"]] 
#         content=note_info["desc"]
#         user=note_info["user"]
#         user_id=user["user_id"]
#         user_name=user["nickname"]
#         user_icon=user["avatar_url"]
#         interact_info=note_info["interact_info"]
#         liked_count=interact_info["liked_count"]
#         collected_count=interact_info["collected_count"]
#         share_count=interact_info["share_count"]
#         comment_count=note_info["comment_count"]
#         image_urls=[item["url_default"]  for item in note_info["image_list"]]  
#         create_time=convert_milliseconds_to_datetime(note_info["time"])
#         last_update_time=convert_milliseconds_to_datetime(note_info["last_update_time"])
#         note_id=note_info["note_id"]
#         title=note_info["title"]
#         current_time=convert_milliseconds_to_datetime(note_data["current_time"])
        
        
#         dest_note_path=os.path.join(root_dir,"title",  f"{title}.txt")
#         dest_image_dir=os.path.join(root_dir,"images")
#         os.makedirs(os.path.dirname(dest_image_dir),exist_ok=True)
#         dest_image_lst=[os.path.join(dest_image_dir,f"{i+1}.jpg") for i in range(len(image_urls))]
#         os.makedirs(os.path.dirname(dest_note_path),exist_ok=True)
#         with open("dest_note_path","w",encoding="utf-8") as f:
#             lines=[
#                 f"{title}\n"
#                 f"id:{note_id}\n",
#                 f"当前时间：{current_time}\n",
#                 f"创建时间：{create_time}\n",
#                 f"更新时间：{last_update_time}\n",
#                 f"图集：{"\n".join(dest_image_lst)}\n",
#                 f"作者：{user_name}\n",
#                 f"点赞：{liked_count}\n",
#                 f"收藏：{collected_count}\n",
#                 f"分享：{share_count}\n",
#                 f"评论：{comment_count}\n",
#                 f"\n{content}\n"
#                 ]
#             f.writelines(lines)
        
#         for i in range(len(image_urls)):
#             url=image_urls[i]
#             dest_path=dest_image_lst[i]
#             responds=requests.get(url)
#             with open(dest_path,"wb") as f:
#                 f.write(responds.content)
#         break

Section= namedtuple('section',["sec","yVal","id","already"])

class SectionManager:
    def __init__(self,wp):
        self.wp=wp
        self.secs=[]
        self.update()
        
    def update(self):
        time.sleep(.5)
        org_secs=wp.eles("xpath://section")
        sorted(org_secs,key=lambda x:x.rect.midpoint.y)
        secs=[Section(sec,sec.rect.midpoint.y,sec.node_id,False)   for sec in org_secs]
        self.secs.extend(secs)
    
    def next(self):
        self.update()
        for sec in self.secs:
            if not sec.already:
                sec.already=True
                yield sec.sec
    
    def count(self):
        self.update()
        return sum([ 0 if sec.already else 1  for sec in self.secs ])

    
def update_secs(wp):
    secs=wp.eles("xpath://section")
    sorted(secs,key=lambda x:x.rect.midpoint.y)
    return 

            
           

if __name__ == '__main__':
    # theme= HandleTheme("四神汤")
    # theme.get_notes()
    num=0
    page_id=0


    info=[]
    request_url=""
    request_headers={}
    request_datas={}
    request_cookies=""

    wp=WebPage()
    ac=Actions(wp)
    
    
    wp.get('https://www.xiaohongshu.com/')
    search_input = wp.ele('xpath://input[@class="search-input"]')
    search_input.clear()
    search_input.input('四神汤\n')
    time.sleep(.4)
    seach_button=wp.ele('xpath://div[@class="search-icon"]')
    if not seach_button:
        sys.exit(0)
    wp.ele('xpath://div[@class="search-icon"]').click()
    wp.listen.start(['web/v1/search/notes',"api/sns/web/v1/feed"]) 

    packet = wp.listen.wait()
    request=packet.request

    request_url=request.url
    request_headers=dict(request.headers.items())
    request_datas=request.postData

    request_cookies=  "; ".join([f'{item["name"]}={item["value"]}'  for item in request.cookies]) 
    response=packet.response

    root_dir=os.path.join(os.getcwd(),"小红书")
    cur_dir=os.path.join(root_dir,"history")
    os.makedirs(cur_dir,exist_ok=True)
    # sections = wp.eles("xpath://section")
    max_y=0
    # 显式等待
    # wait = WebDriverWait(wp.driver, 10)  # 设置等待时间为 10 秒
    sec_i=0
    
    secManager=SectionManager(wp)
    while secManager.count()>0:
        # sections =wait.until(EC.presence_of_all_elements_located((By.XPATH, "//section")))
        time.sleep(.5)
        sections = update_secs(wp)
        print(sections)
        if not sections:
            break
        for i in range(len(sections)):
            index=f"{sec_i}-{i}"
            try :
                print(f"第{index}次：sec.len{len(sections)}")
                temp=sections[i]
                time.sleep(.1)
                ref_divs=temp.children('xpath://div/a[@href]')
                if not ref_divs:
                    continue
                ref=ref_divs[0].attr("href")
                if  ref  and ref not in info:
                    info.append(ref)
                    sec=update_secs[i]

                    print(f"cur:{num} corners:{sec.rect.corners}")
                    rect_y=max([ pos[1] for pos in sec.rect.corners ]) 
                    if max_y<rect_y:
                        print(f"max_y:{max_y},rect_y:{rect_y}")
                        max_y=rect_y
                        
                
                    sec.click()
                    pack=wp.listen.wait()
                    time.sleep(.1)
                    
                    with open(os.path.join(cur_dir,f"{index}.json"), "w", encoding="utf-8") as f:
                        json.dump(pack.response.body,f,indent=4,ensure_ascii=False)
                    # print(pack.response.body)
                    time.sleep(.1)
                    close_flag=wp.ele('xpath://div[@class="close close-mask-dark"]')
                    if close_flag:
                        close_flag.click()
                        sections = wp.eles("xpath://section")
                        time.sleep(.5)
                        
                    num+=1
                    # ac.down(1000)
            except:
                pass
            # sections = wp.eles("xpath://section")
            # time.sleep(.1)
            
        ac.scroll(delta_y=max_y) 
        sec_i+=1
        
        # break
    
    print(f"scroll:{max_y}")
    
    wp.listen.stop()
    # wp.listen.stop()
    
    wp.quit()