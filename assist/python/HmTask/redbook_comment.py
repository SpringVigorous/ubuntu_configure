import csv
import time
import requests


headers={

#  'accept':'application/json, text/plain, */*',
#  'accept-encoding':'gzip, deflate, br, zstd',
#  'accept-language':'zh-CN,zh;q=0.9',
 'cookie':'a1=19029c91c9erh6glnzwujndoez49q5pope7wjw49x00000858779; webId=04a7b350ba3ec00cc1ec563c2eca3319; gid=yj8JjSD22jU0yj8JjSjySdE4jdFxKk1IuE7VWjCIfldu4E88jA2UlV888Y2YWWj82i82D0fq; customer-sso-sid=68c517381709387753437817a2f255a13cd6a803; x-user-id-ark.xiaohongshu.com=5d593e3500000000010013c2; customerClientId=606764650847459; abRequestId=04a7b350ba3ec00cc1ec563c2eca3319; xsecappid=xhs-pc-web; webBuild=4.33.2; websectiga=f47eda31ec99545da40c2f731f0630efd2b0959e1dd10d5fedac3dce0bd1e04d; sec_poison_id=78475907-e22c-49bb-9467-982b862a5b47; acw_tc=1164e28419761d4369d4a6e87b80272fa19d91141086ab9b345b78a8c99bc382; web_session=040069b26ead56dc3c1feb03d5344bde4941cf; unread={%22ub%22:%2266c833af000000001d0196ac%22%2C%22ue%22:%2266dfd68600000000120136d1%22%2C%22uc%22:28}',
 'origin':'https://www.xiaohongshu.com',
 'priority':'u=1, i',
 'referer':'https://www.xiaohongshu.com/',
 'sec-ch-ua':'"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
 'sec-ch-ua-mobile':'?0',
 'sec-ch-ua-platform':'"Windows"',

 'sec-fetch-mode':'cors',
 'sec-fetch-site':'same-site',
 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
 'x-b3-traceid':'d4a80dd51e15382d',
 'x-s':'XYW_eyJzaWduU3ZuIjoiNTUiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6IjViM2U5NjdkZjM2MzVlMGQ5ZGUzYTRiNjZmOTNkN2JlOTc4MzAyZjMyNjEyMTJkMTg2NDcxNWZiY2JkYzYyNmFhNDU2YzBmNDNiNDgxNGNmMWMyNDEwMjMwMWM0NzhiNGU2OWZlM2Y2NmI5ZTljNmM4YWEyMjc5MmU5NGMzZjc1OWQ1YTUzZjYwYjY3NjQ5NWEyMWJjOTg4NGIwY2VlMDQ4ZDQwYmI2ZDc5NTdhN2Y1YWM2OTYxZjVhMWE4YzVmOWVhY2QzZDVkYzlmNTM0NjEyZjRjYzA1OTU1Mjc3YTNiMjIwYWRiNDU3MDFhZGNhNDJiZTNiYzcwZWU3NmFlM2IzNjljMjlmNWNmOWI3MTdiOGU4MDExYWU0ZjEwNDIyNDg0ODJkNmJkNTFlNGJjNzk2YWM0NjZhYmM3Y2Q5NTZiZTc2NGQ4NzdhODRkMWU1ODY5ZTdlM2M3ZmYxYTY4N2UxYTc1M2JlZDk0YmUyYjhmMzQ3NjY5ZmY2NDcxNWM0MjA4NWYwNGEyZDEyY2Y1NTk3ZGRlYWQyNWQxZWU3NTZkIn0=',
 'x-s-common':'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',
 }

# 请求头
headers1 ={
    
"referer":"https://www.xiaohongshu.com/",
"origin":"https://www.xiaohongshu.com",
'accept': "application/json, text/plain, */*",
'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
'cookie':"a1=19029c91c9erh6glnzwujndoez49q5pope7wjw49x00000858779; webId=04a7b350ba3ec00cc1ec563c2eca3319; gid=yj8JjSD22jU0yj8JjSjySdE4jdFxKk1IuE7VWjCIfldu4E88jA2UlV888Y2YWWj82i82D0fq; customer-sso-sid=68c517381709387753437817a2f255a13cd6a803; x-user-id-ark.xiaohongshu.com=5d593e3500000000010013c2; customerClientId=606764650847459; abRequestId=04a7b350ba3ec00cc1ec563c2eca3319; xsecappid=xhs-pc-web; webBuild=4.33.2; websectiga=3633fe24d49c7dd0eb923edc8205740f10fdb18b25d424d2a2322c6196d2a4ad; sec_poison_id=6f8c58ea-9c75-4e83-9731-34cf364b9aad; acw_tc=21eea7453b44551414ed053f1864bc21c0e7e3a8fd48e096073984d80d63cf13; web_session=040069b26ead56dc3c1ff655e9344ba3527c06; unread={%22ub%22:%2266dad6d1000000000c01afc8%22%2C%22ue%22:%2266d981560000000012011476%22%2C%22uc%22:28}",

'sec-ch-ua':'"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
'sec-ch-ua-mobile':'?0',
'sec-ch-ua-platform':'"Windows"',
'sec-fetch-dest':'empty',
'sec-fetch-mode':'cors',
'sec-fetch-site':'same-site',
'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
'x-b3-traceid':'8e90d5a6c24c43b5',
'x-s':'XYW_eyJzaWduU3ZuIjoiNTUiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6ImJjZDA0Nzg4YzM2OGEzNjk2MjNhNGFjMGYyOTRmMzBmMTE4YmUwY2M1MGQ4ZTVhZDk0YzAxYWE4N2Y3NzNiZDdlNzI1ZmNkNjlmYjI4YzA3OTBhMmJhNWQzNjE1OTYyMTcxNTgwYTBmZTkwM2MyMWM5MzFmYmQ2NDNiYjI0MDlhYmFiMTUzNzZmNTUzZjU3MTgxOGU1YmFmZTg1YzRmZDFkMWFlOTliZDJkODRmYjU4NGZjNGZmM2VhYzU5ZjgzYjdhZmRlNTI4MzhjMzBiMjBmN2EzZjIxZGYwOWIyYjQ3NGJlZmJhZDFhNDg0NjkzNjlmMmNmYTFlMmFiMTBlYmQ3NzZiYjI5MmI1ODk5MjFjM2I1ODFjYzMxZGZlYzdiYmE5YzRmN2I2OTYzNDc3YWI3MmFmNzIzNWI0ZTA2NGEwZDMyM2VkZGRiMDAyYjM4NWE5Y2RkYmQ1NGQ2YjNkYzkxY2IxOGI3NjY3Yjc2Y2ZlNmM4ZjMwMDVlNTBjMDdmYjIxMjIwMTcwN2JkOWE3YzJhYWUzZGI4NTRiZDIzZjMyIn0=',
'x-s-common':'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',







}

params={
'note_id':'66c7e3d9000000001d016176',
'cursor':'',
'top_comment_id':'',
'image_formats':'jpg,webp,avif',
}

#发送爬取请求
def spider(url):
    response =requests.get(url,headers=headers,verify=False)
    response.encoding ='utf-8'
    if response.status_code ==200:
        return response.json()
    else:
        print('请求失败')


#时间戳转换成日期
def get_time(ctime):

    timeArray =time.localtime(int(ctime /1000))
    otherstyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherstyleTime)


def sava_data(comment):
    data_dict ={
    "用户ID":comment['user_info']['user_id'].strip(),
    "用户名":comment['user_info']['nickname'].strip(),
    "头像链接":comment['user_info']['image'].strip(),
    "评论时间":  get_time(comment['create time']),
    "IP属地":comment['ip_location'],
    "点赞数量":comment['like_count'],
    "评论内容":comment['content'].strip().replace('\n','')
    }
    # 评论数量+1
    global comment_count
    comment_count +=1

    print(f"当前评论数:{comment_count}\n",
    f"用户ID:{data_dict['用户ID']}\n",
    f"用户名:{data_dict['用户名']}\n",
    
    f"头像链接:{data_dict['头像链接']}\n", 
    f"评论时间:{data_dict['评论时间']}\n",
    f"IP属地:{data_dict['IP属地']}\n",
    
    f"点赞数量:{data_dict['点赞数量']}\n",
    f"评论内容:{data_dict['评论内容']}\n",
    )
    
    writer.writerow(data_dict)



def get_sub_comments(note_id, root_comment_id, sub_comment_cursor):
    while True:
        url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor={sub_comment_cursor}&top_comment_id={root_comment_id}&image_formats=jpg,webp,avif'
        # 爬一次就睡1秒
        time.sleep(1)
        sub_comment_data=spider(url)


        for sub_comment in sub_comment_data['data']['comments']:
            sava_data(sub_comment)
        if not sub_comment_data['data']['has_more']:
            break
        #下一页评论的地址
        sub_comment_cursor =sub_comment_data['data']['cursor']



def get_comments(note_id):
    cursor=""
    page = 0
    while True:
        #https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id=66b6ff4d0000000025030474&cursor=&top_comment_id=&image_formats=jpg,webp,avif

        # url = f'https://edith.xiaohongshu.com/apisns/web/v2/comment/page?note_id={note_id}&cursor=&top_comment_id=&image_scenes=FD_WM_WEBP,CRD_WM_WEBP'
        url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor=&top_comment_id=&mage_formats=jpg,webp,avif'
        #爬一次就睡1秒
        time.sleep(1)
        json_data= spider(url)
        if not json_data:
            break
        
        for comment in json_data['data']['comments']:
            sava_data(comment)
            #是否爬取子评论,不爬取子评论将其改成False
            is_sub_comments =False
            if is_sub_comments:
                # 爬取子评论:
                get_sub_comments(note_id, comment['id'], comment['sub_comment_cursor'])
        if not json_data['data']['has_more']:
                    break  
        
        #下一页评论的地址
        cursor = json_data['data']['cursor']
        #每爬完一页,页数加1
        page = page + 1
        print('===========爬取Page{}完华===='.format(page))



if __name__== "__main__":
    comment_count =0

    # 小红书文章的note_id
    note_id_list =['66c7e3d9000000001d016176',   ]
    #向csv文件写入表头
    
    header =["用户ID","用户名"
    ,"头像链接","评论时间","IP属地"
    "点赞数量",
    "评论内容"]
    f = open(f"评论.csv","w",encoding="utf-8-sig", newline="")
    writer =csv.DictWriter(f,header)
    writer.writeheader()
    for note_id in note_id_list:
        get_comments(note_id)
        print(f'\n====={note_id}的文章评论爬取完毕======\n')
    print("\n=====爬取完华esess=sss2===-\n")
