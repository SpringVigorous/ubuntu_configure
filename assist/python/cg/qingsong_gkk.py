import os
import sys   
from pathlib import Path
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType


import requests
import json
def get_gkk(url,headers,params,dest_path):

    logger=logger_helper("下载","公开课")
    info={"url":url,"headers":headers,"params":params,"dest_path":dest_path}
    logger.info("开始",f"\n{json.dumps(info,ensure_ascii=False,indent=4 )}")

    response = requests.get(url, params=params, headers=headers)
    # if response.status_code != 200:
    #     exit(0)
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    logger.info("成功",update_time_type=UpdateTimeType.ALL)

if __name__=="__main__":
    root_path=r"D:\Project\教程\轻松学堂\公开课-2025.1.23"


    headers = {
        'authority': 'v11.talk-fun.com',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'video',
        'accept-language': 'zh-CN,zh;q=0.9',
        'range': 'bytes=0-',
    }

    params = {
        'sign': '1737964607-20250127095647-223917610-cfa9ecdea9236595a346a5077dfb8376',
        'auth_key': '1737964607-0-0-a5c4e3a3e2d37af41926446fe88a5522',
        'pid': '63563',
        'limit': '82K',
    }




    url='https://v11.talk-fun.com/4/live/7/784547/ndk4njawnw/1737900244_video-client-1.mp4'


    file_name = "4_如何利用免费的AI工具制作书单号.mp4"
    get_gkk(url,headers,params,os.path.join(root_path,file_name))  

