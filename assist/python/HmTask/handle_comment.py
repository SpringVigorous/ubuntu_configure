
import csv
import time
from bs4 import BeautifulSoup
import os
#时间戳转换成日期
def get_time(ctime):

    timeArray =time.localtime(int(ctime /1000))
    otherstyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherstyleTime)
def get_val(org_str,del_str:str)->int:
    if type(org_str)==str:
        dest_str=org_str.replace(del_str,"").strip()
        try:
            return int(dest_str) if len(dest_str)>0 else 0
        except:
            return 0
    return org_str

class NoteWriter:
    def __init__(self,file_path):
        self._f= open(file_path,"w",encoding="utf-8-sig", newline="")
        header =["user_id","user_name"
            ,"user_link","time","city",
            "thumb_count","reply_count",
            "content","note_id"]
        self._writer =csv.DictWriter(self._f,header)
        self._writer.writeheader()

        
    def __destory__(self):
        self._f.close()
        
        
    def handle_comment(self,html_data,note_id:str="",note_title:str=""):
        
        soup=BeautifulSoup(html_data,"lxml")
        items=soup.find_all('div',{'class':"comment-inner-container"})

        for item in items:
            #用户信息
            author=item.find('a',{'class': 'name'})
            name=author.text
            id=author.get("data-user-id")
            ref=author.get("href")
            
            #内容
            comment=item.find('div',{'class':"content"}).text
            
            #日期 位置
            date_pos=item.find('div', {'class': 'date'}).find_all('span')
            date=date_pos[0].text.strip()
            pos=date_pos[1].text.strip()

            #点赞数 回复数
            like_info=item.find('div',{'class':"interactions"})
            like_spans=like_info.find_all('span',{"class":"count"})
            like_count=get_val(like_spans[0].text,"赞")
            reply_count=get_val(like_spans[1].text,"回复")
            
            data_dict ={
            "user_id":id.strip(),
            "user_name":name.strip(),
            "user_link":ref.strip(),
            "time":  date,
            "city":pos,
            "thumb_count":like_count,
            "reply_count":reply_count,
            "content":comment.strip().replace('\n',''),
            "note_id":note_id
            }
            self._writer.writerow(data_dict)
            

    



        
if __name__ == "__main__":
    dir_path=r"F:\worm_practice\red_book\notes\健脾养胃"
    html_path=os.path.join(dir_path,"pack_0.html")
    with open(html_path,"r",encoding="utf-8-sig") as f:
        html_data=f.read()
        writer= NoteWriter(os.path.join(dir_path,"评论.csv"))
        writer.handle_comment(html_data)
    
    pass