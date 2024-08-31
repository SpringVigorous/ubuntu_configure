from DrissionPage import WebPage
from DrissionPage.common import Actions
from pprint import pprint
import os
import time
import json
from requests.structures import CaseInsensitiveDict
import requests
import sys
num=0
page_id=0


info=[]
request_url=""
request_headers={}
request_datas={}
request_cookies=""

class NoteKey:
    def __init__(self,id,token) -> None:
        # self.url=""
        # self.title=""
        self.xsec_token=token
        # self.type=""
        self.id=id

class HandleNote:
    def __init__(slef):
        pass



class AttemptThemeInfo:
    def __init__(self, theme):
        self.theme=theme
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
        


        wp.listen.start(['web/v1/search/notes']) #,"api/sns/web/v1/feed"
        
        packet = wp.listen.wait()
        request=packet.request
        
        self.request_url=request.url
        self.request_headers=dict(request.headers.items())
        self.request_datas=request.postData

        self.request_cookies=  "; ".join([f'{item["name"]}={item["value"]}'  for item in request.cookies]) 
        self.response=packet.response
        wp.listen.stop()
        
        
    def search_notes():
        pass
            
    def write_to_file(self, file_name):
        request_dic={
            "request_url":self.request_url,
            "request_headers":self.request_headers,
            "request_datas":self.request_datas,
            "request_cookies":self.request_cookies,
            "request_response":self.response.body,
        }
        cur_dir=os.path.join(os.getcwd(),"history")
        dest_path=os.path.join(cur_dir,
        f"page_{page_id}.json")
        os.makedirs(os.path.dirname(dest_path),exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(request_dic,
            f,indent=4,ensure_ascii=False)
            
    @property
    def success(self)->bool:
        return self.response is not None and hasattr(self.response,"success") and self.response["success"]
    
    def headers(self):
         headers= self.request_headers.copy()
         headers["Cookie"]=self.request_cookies
         return headers
    def datas(self,i:int):
        data= self.request_datas.copy()
        data["page"]=i
        return data
    #返回一个生成器
    @property
    def notes(self):
        if  not self.success:
            return 
        try:
            
            notes= self.response["data"]["items"]
            for note in notes:
                card=note["note_card"]
                yield  NoteKey(card["id"],card["xsec_token"])
            
        except:
            return None


    def PageNext(self,num):
        pass
def  GetNotesKey(respond_text):

    try:
        notes= respond_text["data"]["items"]
        for note in notes:
            # card=note["note_card"]
            yield  NoteKey(note["id"],note["xsec_token"])
    except:
        return None

class HandleNote:
    def __init__(self,theme):
        self.model_type=""
        self.topics=[]
        
import datetime

def convert_milliseconds_to_datetime(milliseconds):
    # 将毫秒时间戳转换为秒时间戳
    seconds = milliseconds / 1000.0
    
    # 将秒时间戳转换为 datetime 对象
    dt = datetime.datetime.fromtimestamp(seconds)
    
    # 格式化 datetime 对象为年月日时分秒格式
    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date

def GetNotesbyThemeText(theme_text,root_dir,headers):
    for note_key in GetNotesKey(theme_text):
        url="https://edith.xiaohongshu.com/api/sns/web/v1/feed"
        data={
            "source_note_id": note_key.id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {
                "need_body_topic": "1"
            },
            "xsec_source": "pc_search",
            "xsec_token": note_key.xsec_token
            }
        note_respond=requests.post(url,headers=headers,data=data)
        if note_respond.status_code!=200:
            continue
        note_respond.encoding="utf-8"
        note_data=note_respond.json()["data"]
        note_info=note_data["items"](0)
        
        id=note_info["id"]
        model_type=note_info["model_type"]
        topics=[ tag["name"] for tag in note_info["note_card"]["tag_list"]] 
        content=note_info["desc"]
        user=note_info["user"]
        user_id=user["user_id"]
        user_name=user["nickname"]
        user_icon=user["avatar_url"]
        interact_info=note_info["interact_info"]
        liked_count=interact_info["liked_count"]
        collected_count=interact_info["collected_count"]
        share_count=interact_info["share_count"]
        comment_count=note_info["comment_count"]
        image_urls=[item["url_default"]  for item in note_info["image_list"]]  
        create_time=convert_milliseconds_to_datetime(note_info["time"])
        last_update_time=convert_milliseconds_to_datetime(note_info["last_update_time"])
        note_id=note_info["note_id"]
        title=note_info["title"]
        current_time=convert_milliseconds_to_datetime(note_data["current_time"])
        
        
        dest_note_path=os.path.join(root_dir,"title",  f"{title}.txt")
        dest_image_dir=os.path.join(root_dir,"images")
        os.makedirs(os.path.dirname(dest_image_dir),exist_ok=True)
        dest_image_lst=[os.path.join(dest_image_dir,f"{i+1}.jpg") for i in range(len(image_urls))]
        os.makedirs(os.path.dirname(dest_note_path),exist_ok=True)
        with open("dest_note_path","w",encoding="utf-8") as f:
            lines=[
                f"{title}\n"
                f"id:{note_id}\n",
                f"当前时间：{current_time}\n",
                f"创建时间：{create_time}\n",
                f"更新时间：{last_update_time}\n",
                f"图集：{"\n".join(dest_image_lst)}\n",
                f"作者：{user_name}\n",
                f"点赞：{liked_count}\n",
                f"收藏：{collected_count}\n",
                f"分享：{share_count}\n",
                f"评论：{comment_count}\n",
                f"\n{content}\n"
                ]
            f.writelines(lines)
        
        for i in range(len(image_urls)):
            url=image_urls[i]
            dest_path=dest_image_lst[i]
            responds=requests.get(url)
            with open(dest_path,"wb") as f:
                f.write(responds.content)
        break


class HandleTheme:
    def __init__(self,theme):
        self.info=AttemptThemeInfo(theme)
    def get_notes(self):
        page=0
        root_dir=os.path.join(os.getcwd(),"小红书")
        while True:
            page+=1
            if page==1 :
                GetNotesbyThemeText(self.info.response.body,root_dir,self.info.headers())

            else:
                responds=requests.post(self.info.request_url,headers=self.info.headers(),data=self.info.datas(page))
                if responds.status_code!=200:
                    continue
                responds.encoding="utf-8"
                GetNotesbyThemeText(responds.text,root_dir,self.info.headers(),self.info.datas(page))
            
           

if __name__ == '__main__':
    theme= HandleTheme("四神汤")
    theme.get_notes()
    # sections = wp.eles("xpath://section")
    # for i in range(len(sections)):
    #     temp=wp.eles("xpath://section")[i]
    #     ref=temp.attr("href")
    #     if not ref and ref not in info:
    #         info.append(ref)
    #         temp.click() 
    #         pack=wp.listen.wait()
            
            
    #         with open(os.path.join(cur_dir,
# f"section_{num}.json"), "w", encoding="utf-8") as f:
#     #             json.dump(pack.response.body,
# f,indent=4,ensure_ascii=False)
#     #         #     f.write(pack.response.body)
    #         # print(pack.response.body)
    #         wp.ele('xpath://div[@class="close close-mask-dark"]').click()
    #         # time.sleep(1)
    #         num+=1
    #         # ac.down(1000)
    #         pass
    # ac.scroll(delta_y=1500)
    # # wp.listen.stop()