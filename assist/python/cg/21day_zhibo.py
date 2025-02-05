import os
import sys   
from pathlib import Path
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path,UpdateTimeType


import requests
import json
def get_21Day(url,headers,params,dest_path):

    logger=logger_helper("下载","21天课")
    info={"url":url,"headers":headers,"params":params,"dest_path":dest_path}
    logger.info("开始",f"\n{json.dumps(info,ensure_ascii=False,indent=4 )}")

    response = requests.get(url, params=params, headers=headers)
    # if response.status_code != 200:
    #     exit(0)
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    logger.info("成功",update_time_type=UpdateTimeType.ALL)

if __name__=="__main__":
    root_path=r"D:\Project\教程\21天课"


    import requests

    headers = {
        'authority': 'v11.talk-fun.com',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'video',
        'referer': 'https://e.qs6x.com/',
        'accept-language': 'zh-CN,zh;q=0.9',
        'range': 'bytes=0-',
    }

    params = {
        'sign': '1737900508-20250125220828-18212612955-e7225d7b8aeef09ff48a8537c6f0d296',
        'auth_key': '1737900508-0-0-323ff2466179becc1dc045d0e4e21835',
        'pid': '62307',
        'limit': '125K',
        'cdt': '1734605837',
        'part': '1',
        'from': 'tfvod',
    }

    # response = requests.get('https://v11.talk-fun.com/7/video/50/69/24/ae3e829a7bd367b1504d74fe79/93cfb7ce_video.mp4', params=params, headers=headers)


   
    url='https://v11.talk-fun.com/7/video/50/69/24/ae3e829a7bd367b1504d74fe79/93cfb7ce_video.mp4'


    file_name="03_二次剪辑实操技巧.mp4"
    get_21Day(url,headers,params,os.path.join(root_path,file_name))  

