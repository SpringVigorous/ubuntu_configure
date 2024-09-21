import csv
import time
#时间戳转换成日期
def get_time(ctime):

    timeArray =time.localtime(int(ctime /1000))
    otherstyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherstyleTime)

class NoteWriter:
    def __init__(self,file_path):
        self._f= open(file_path,"w",encoding="utf-8-sig", newline="")
        header =["user_id","user_name"
            ,"user_link","time","city",
            "thumb_count",
            "content","note_id"]
        self._writer =csv.DictWriter(self._f,header)
        self._writer.writeheader()
    def __destory__(self):
        self._f.close()
        
        
    def handle_comment(self,json_data):
        
        for comment in json_data['data']['comments']:
            self.sava_data(comment)
            for sub_comment in comment['sub_comments']:

                self.sava_data(sub_comment)
        


    def sava_data(self,comment):
        user_data=comment.get('user_info',{})
        data_dict ={
        "user_id":user_data.get('user_id',"").strip(),
        "user_name":user_data.get('nickname',"").strip(),
        "user_link":user_data.get('image',"").strip(),
        "time":  get_time(comment.get('create_time',"")),
        "city":comment.get('ip_location',""),
        "thumb_count":comment.get('like_count',""),
        "content":comment.get('content',"").strip().replace('\n',''),
        "note_id":comment.get('note_id',"").strip(),
        }

        self._writer.writerow(data_dict)
        
        
