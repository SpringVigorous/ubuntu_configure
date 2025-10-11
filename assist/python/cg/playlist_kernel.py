from base import download_async,download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,delete_directory,merge_video,convert_video_to_mp4_from_src_dir,convert_video_to_mp4,get_all_files_pathlib,move_file
from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType
from base import arrange_urls,postfix
from base import exception_decorator,base64_utf8_to_bytes,bytes_to_base64_utf8,ThreadPool,AES_128
from pathlib import Path
import requests
import os
import re
import json

def get_real_url(url:str,url_page):
    if is_http_or_https(url) :
        return url
    if url[:1]==r'/':
        return   f"{get_homepage_url(url_page) }{url}"
    else:
        org_path=Path(url_page)
        name=org_path.name
        return url_page.replace(name,url)


class video_info:
    def __init__(self,url,m3u8_path) -> None:
        self.url=url
        self.logger=logger_helper("解析m3u8",f"{self.url}")
        self.method=None
        self.uri=None
        self.iv=None
        
        self.playlist=None
        self.org_playlist=None
        
        # https://live80976.vod.bjmantis.net/cb9fc2e3vodsh1500015158/b78d41a31397757896585883263/playlist_eof.m3u8?t=67882F57&us=6658sy3vu3&sign=86f52ae9c6bd64c87db0ac9937096df9
        headers = {
            'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
            'Referer': 'https://www.baidu.com/',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
            'sec-ch-ua-platform': '"Windows"',
        }
        content=None
        has_already=False
        try:
            flag=True
            if flag:
                content=load_m3u8_data(m3u8_path)
                if content:
                    has_already=True
        except:
            pass
        if not content:
            response=requests.get(url, headers=headers,verify=False)
            self.logger=logger_helper("解析m3u8",f"{self.url}")
            content=response.text
            
        if "#EXT-X-STREAM-INF" in content:
            rows=[data for data in content.split("\n") if data]
            data=rows[-1]
            url=get_real_url(data.strip(),url)
            self.url=url
            response=requests.get(url, headers=headers,verify=False)
            self.logger=logger_helper("解析m3u8",f"{self.url}")
            content=response.text
            has_already=False
            
        #写入文件
        if not has_already and content:
            open(m3u8_path,"w",encoding="utf-8-sig").write(content)
            
            
        self.m3u8=content
        try:
            header=content.split('#EXTINF:')[0].replace(",","\n")

            self.logger.debug("内容头",f"\n{header}\n")
        except:
            pass
        # print(content)
        # 正则表达式模式
        self._init_urls(content)
        self._init_keys(content)

    @exception_decorator(error_state=False)
    def _init_urls(self,content):
        pattern = re.compile(r'#EXTINF:(.*?),\s*(\S+)\s')

        matches = pattern.findall(content)
        if not matches:
            return
        playlist=[]
        for val in matches :
            duration, ts_file =val
            playlist.append([float(duration),get_real_url(ts_file,self.url)])
        
        arrage_lst= arrange_urls(playlist)   
            
        dest_list=[[index,seg["duration"],seg["url"]]    for index,seg in enumerate(arrage_lst)]
        
        self.playlist=dest_list
        self.org_playlist=[[index,*seg]   for index,seg in enumerate(playlist)  ]
        
    @property
    def has_raw_list(self):
        return len(self.org_playlist)>len(self.playlist)
        
    def _init_keys(self,content):
               
        """
        从给定的字符串中提取 METHOD、URI 和 IV 的值。
      
        :param line: 要处理的字符串
        :return: 包含 METHOD、URI 和 IV 的字典
        """
        # 定义正则表达式模式
        pattern = r'#EXT-X-KEY:METHOD=(?P<method>[^,]+),URI="(?P<uri>[^"]+)",IV=(?P<iv>0x[0-9a-fA-F]+)'
        
        # 使用 re.search 检查字符串是否匹配模式
        match = re.search(pattern, content)
        

        
        # 返回匹配结果
        if match:
            self.method=match.group('method')
            self.uri=match.group('uri')
            iv=match.group('iv')
            self.iv=bytes.fromhex(iv.replace('0x',''))


            
    @property
    def key(self):
        if not self.uri:
            return None
        url=self.uri
        if not is_http_or_https(url):
            org_path=Path(self.url)
            name=org_path.name
            url=self.url.replace(name,self.uri)
        key=fetch_sync(url)
        self.logger.debug("加密信息",f"\nmethod:{self.method},\nuri:{self.uri},\niv:{self.iv},\nkey:{key}")
        # print(len(self.iv))
        # print(len(key))
        return key

    @property
    def domain(self):
        return get_homepage_url(self.url)
    @property
    def suffix(self)->str:
        if self.playlist:
            return postfix(self.playlist[0][2])
        return ".ts"


@exception_decorator()
def load_url_data(url_json_path):
    if  not os.path.exists(url_json_path):
        return
    with open(url_json_path,"r",encoding="utf-8-sig") as f:
        data=json.load(f)
        return data
    return None
    
@exception_decorator()
def save_url_data(url_json_path,data):
    with open(url_json_path,"w",encoding="utf-8-sig") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

def save_m3u8_data(m3u8_path,data):
    with open(m3u8_path,"w",encoding="utf-8-sig") as f:
        f.write(data)


def load_m3u8_data(m3u8_path):
    with open(m3u8_path,"r",encoding="utf-8-sig") as f:
        return f.read()

@exception_decorator()
def get_url_data(url,url_json_path,m3u8_path):
    info=load_url_data(url_json_path)
    if not info:
        video=video_info(url,m3u8_path)
        key= video.key
        iv=video.iv

        if key :
            key= bytes_to_base64_utf8(key)
        if iv :
            iv= bytes_to_base64_utf8(iv)


        info_list=video.playlist
        if not info_list:
            return
        total_len= [float(item[1])   for item in info_list]
        temp=os.path.basename(url_json_path)
        
        dest_name,dest_hash=temp.split(".")[0].split("-")
        info={"url":url,"name":dest_name,"hash":dest_hash,"total_len":sum(total_len),"key":key,"iv":iv ,"playlist":info_list}
        if video.has_raw_list:
            info["org_playlist"]=video.org_playlist
        
        
        #保存
        save_url_data(url_json_path,info)

    try:    
        key=info.get("key","")
        iv=info.get("iv","")
        if key:
            key=base64_utf8_to_bytes(key)
        if iv:
            iv=base64_utf8_to_bytes(iv)
        # return None,None,info.get("playlist",[]),info.get("total_len",0)
        return key,iv,info.get("playlist",[]),info.get("total_len",0)
    except:
        return None,None,info.get("playlist",[]),info.get("total_len",0)
        
    