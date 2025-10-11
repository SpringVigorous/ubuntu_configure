import os
import sys   
from pathlib import Path





from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType


import requests
import json
def get_kejian(url,headers,params,dest_path):

    logger=logger_helper("php",f"url:{url}")
    info={"url":url,"headers":headers,"params":params,"dest_path":dest_path}
    logger.info("参数",json.dumps(info,ensure_ascii=False,indent=4 ))

    response = requests.get(url, params=params, headers=headers)
    # if response.status_code != 200:
    #     exit(0)
    response.encoding = 'utf-8'
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    logger.info("结果",response.text)
    

if __name__=="__main__":
    root_path=r"D:\Project\教程"


    headers = {
    'authority': 'open.talk-fun.com',
    'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 SE 2.X MetaSr 1.0',
    'sec-ch-ua-platform': '"Windows"',
    'accept': '*/*',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-dest': 'script',
    'referer': 'https://e.qs6x.com/',
    'accept-language': 'zh-CN,zh;q=0.9',
    }

    params = {
        'callback': 'vodCallback',
        'access_token': 'QO5gDM1czNmRDMykzN3QmNzEmYxcTYmNWNlNWZhJTOkxHf81nI58VNzkjM4gzMfdjM5UzM0EjI6ISZtFmbyJCLxojIhJCLiAjI6ICZpdmIs01W6Iic0RXYiwCO4YTNwczNzcTM6ISZtlGdnVmciwiIxcDNzkjN0QjMxIiOiQWa4JCL3AzMyYjOiQWawJCLiYXTpF2cn1mSodWaJNTWqBlI6IyclR2bjJCL1MTOygDOzojIkl2XlNnc192YiwiIiojIyFGdhZXYiwCM6IiclRmbldmIsgDOykDM3czM3EjOiUmcpBHelJCL3ITO1MDNxojIklWbv9mciwiIzY2N3UHX3U2N5UHX5YWY3UHXyImM1UHXiojIl1WYut2Yp5mIsIiclNXdiojIlx2byJCLiUjM2EzMyAjNiojIklWdiwyNwMjM2ojIkl2XyVmb0JXYwJye',
    }
    url='https://open.talk-fun.com/live/playback.php'
    file_name="php_url.json"


    get_kejian(url,headers,params,os.path.join(root_path,file_name))  


