import re
import time
import requests
import execjs
import json
import csv

# 搜关键词：
# F12查找
# search_result?keyword=%25E7%25 换 cookies
cookies ={
"sec_poison_id":"92da0c59-440d-4942-9485-63d13bc6be61",
"gid":"yYsg4Ddg]fh2yYsq4DdJ0i3D48A1SA7M1vUxVx4ChvVJkD28k93jvu888y2j4YY8f40YWKis",
"a1":"18c34be2a40qlcquslyphxvjj2ggti9yvfjbzibh450000159488",
"websectiga":"10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467",
"webId":"f682f0b808cc24ca01712dc4812ad92f",
"web_session":"0400698c10b7e95654662e9158374b878e676e",
"xsecappid": "xhs-pc-web",
"webBuild": "3.18.3"


}
headers ={
"authority":"edith.xiaohongshu.com",
"accept":"application/json, text/plain, */*",
"accept-language":"zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-Us;q=0.6",
"content-type":"application/json;charset=UTF-8",
"origin":"https://www.xiaohongshu.com",
"referer":"https://www.xiaohongshu.com/",
"user-agent": "Mozilla/5.0 (windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Ge‘"
}



js = execjs.compile(open(r'info.js','r', encoding='utf-8').read())
note_count = 0
#向csv文件写入表头 笔记数据csv文件
header = ["笔记标题"，"用户ID"，"用户名","头像链接","IP属地"，"笔记发布时间","笔记收藏数量"，"笔记评论数量"，"笔记点赞数量"，"笔记转发数量"，"笔记内容"]
f = open(f"话题笔记数据.csv","w"，encoding="utf-8-sig",newline="")
writer =csv.DictWriter(f，header)
writer.writeheader()


# 时间戳转换成日期
def get_time(ctime):
    timeArray =time.localtime(int(ctime /1000))
    otherstyleTime =time.strftime("%Y.%m.%d",timeArray)
    return str(otherstyleTime)


# 保存笔记数据
def sava_data(note data):
    try:
        ip_location =note data['note card']['ip_location']
    except :
        ip_location ='未知'
        data_dict ={
        "笔记标题":note_data['note_card']['title'].strip(),
        "用户ID": note_data['note_card']['user']['user_id'].strip(),
        "用户名":note_data['note_card']['user']['nickname'].strip(),
        "头像链接": note_data['note card']['user']['avatar'].strip(),
        "IP属地":ip_location,
        "笔记发布时间":get_time(note_data['note_card']['time']),
        "笔记收藏数量": note data['note card']['interact info']['collected count'],
        "笔记评论数量": note_data['note _card']['interact_info']['comment_count'],
        "笔记点赞数量": note data['note_card']['interact info']['liked_count'],
        "笔记转发数量": note_ data['note_card']['interact_info']['share_count']",
        "笔记内容":note data['note_card']['desc'].strip().replace('\n'," "),
        }
        #笔记数量+1

        global note_count
        note_count += 1

        print(f"当前笔记数量:{note_count}\n",
        f"笔记标题:{data_dict['笔记标题']}\n",
        f"用户ID:{data_dict['用户ID']}\n",
        f"用户名:{data_dict['用户名']}\n",
        f"头像链接:{data_dict['头像链接']}\n"
        f"IP属地:{data_dict['IP属地']}\n",
        f"笔记发布时间:{data_dict!'笔记发布时间'}\n",
        f"笔记收藏数量:{data_dict['笔记收藏数量']}\n",
        f"笔记评论数量:{data_dict['笔记评论数量']}\n",
        f"笔记点赞数量:{data_dict['笔记点赞数量']}\n",
        f"笔记转发数量:{data_dict['笔记转发数量']}\n",
        f"笔记内容:{data_dict['笔记内容']}\n"
        )
        writer.writerow(data_dict)

def get_note_info(note_id):
    note_url = https://edith.xiaohongshu.com/api/sns/web/v1/feed
    data ={
    "source note_id": note_id,
    "image scenes":["CFD_PRV WEBP","CRD WM WEBP"]

    }

    data =json.dumps(data,separators=(',',':'))
    ret = js.call('get_xs','/api/sns/web/v1/feed', data, cookies['a1'])
    headers['x-s'], headers['x-t']= ret['X-s'], str(ret['X-t'])
    response = requests.post(note url, headers=headers, cookies=cookies, data=data)
    json_data =response.json()
    try:
        note_data = json_data['data']['items'][0]
    except :
        print(f'笔记 {note_id} 不允许查看')
        return
    sava_data(note data)
    
# F12  查找 notes
def keyword search(keyword):
    api ='/api/sns/web/v1/search/notes'
    search_url ="https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
    #排序方式 general:综合排序 popularity_descending:热门排序 time_descending:最新排序
    data ={
    "image scenes": "FD PRV WEBP,FD WM_WEBP",
    "keyword": "",
    "note _type": "θ",
    "page":"",
    "page size":"20",
    "search id":"2c7hu5b3kzoivkh848hp0",
    "sort": "general"
    }
    data =json.dumps(data, separators=(',',':'))
    data = re.sub(r'"keyword":".*?"',f'"keyword":"{keyword}"', data)
    page_count=20 #爬取的页数，一页有 20 条笔记
    for page in range(1, page_count):
        data = re.sub(r'"page":".*?",f'"page":"{page}"',data)
        ret = js.call('get_xs', api, data, cookies['a1'])
        headers['x-s'],headers['x-t']= ret['x-s'],str(ret['x-t'])

        response = requests.post(search_url, headers=headers, cookies=cookies, data=data.encode('utf-8'))
        json_data =response.json()
        try:
            notes = json_data['data']['items']
        except :
            print('==========爬取完华=========='.format(page))
            break
        for note in notes:
            note_id = note['id']
            if len(note_id)!= 24:
                continue
            #F12  查找feed
            get_note_info(note_id)
def main():
    keyword =''# 搜索的关键词
    keyword search(keyword)

if __name__ == "__main__":
    main()
