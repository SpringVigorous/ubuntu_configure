import os
import sys   
from pathlib import Path
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType


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
    root_path=r"F:\教程\短视频教程\抖音\21天课"


    import requests

    headers = {
        'authority': 'log.talk-fun.com',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'sec-ch-ua-mobile': '?1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
        'sec-ch-ua-platform': '"Android"',
        'accept': '*/*',
        'origin': 'https://e.qs6x.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://e.qs6x.com/',
        'accept-language': 'zh-CN,zh;q=0.9',
    }

    params = {
        'cid': '3882961',
        'xid': '1244693471',
        'rid': '1435927',
        'uid': '60231625',
        'pid': '62307',
        'pf': 'html',
        'type': 'waiting',
        'pl': '1',
        'pt': '2',
        'bn': '0',
        'ba': '0',
        'pn': '1',
        'ctype': '9',
        'playRate': '1',
        'curTime': '0',
        'host': 'v11.talk-fun.com',
        'srcUrl': 'https://v11.talk-fun.com/7/video/75/2e/a6/db516389f2b296d8766517572a/3f699c13_video.mp4?sign=1738837785-20250205182945-10193252107-ba15c8ed669364fef63d817d722d2ed6&auth_key=1738837785-0-0-5b3659eac8152abe8911e6c6b0d8952a&pid=62307&limit=145K&cdt=1735380355&part=1&from=tfvod',
        'ht_tstamp': '1738751330167',
    }




    # response = requests.get('https://log.talk-fun.com/stats/play.html', params=params, headers=headers)


   
    url='https://log.talk-fun.com/stats/play.html'


    file_name="08_直播带货常见误区.mp4"
    get_21Day(url,headers,params,os.path.join(root_path,file_name))  

