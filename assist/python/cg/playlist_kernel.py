from base import download_async,download_sync,move_file,get_homepage_url,is_http_or_https,hash_text,delete_directory,merge_video,convert_video_to_mp4_from_src_dir,convert_video_to_mp4,get_all_files_pathlib,move_file,hash_text
from base import exception_decorator,logger_helper,except_stack,normal_path,fetch_sync,decrypt_aes_128_from_key,get_folder_path_by_rel,UpdateTimeType
from base import arrange_urls,postfix
from base import exception_decorator,base64_utf8_to_bytes,bytes_to_base64_utf8,ThreadPool,AES_128
from base import read_from_txt_utf8_sig,write_to_txt_utf8_sig,read_from_bin
from base import TinyFetch,TinyCache
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
#去掉 -hash值
def title(path_stem:str):
    pattern=r"(.*)-[0-9a-z]{8}(.*)"
    match=re.match(pattern,path_stem)
    if match:
        return f"{match.group(1)}{match.group(2)}"

class video_info:
    def __init__(self,m3u8_url,m3u8_path) -> None:
        self.m3u8_url=m3u8_url
        self.logger=logger_helper("解析m3u8",f"{self.m3u8_url}")
        self.method=None
        self.uri=None
        self.iv=None
        self._m3u8_path=m3u8_path
        self.playlist=None
        self.org_playlist=None
        self._key:TinyFetch=None
        
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
            response=requests.get(m3u8_url, headers=headers,verify=False)
            self.logger=logger_helper("解析m3u8",f"{self.m3u8_url}")
            content=response.text
            
        # handle_data=video_info.handle_m3u8_data(url,content)    
        if "#EXT-X-STREAM-INF" in content:
            rows=[data for data in content.split("\n") if data]
            data=rows[-1]
            m3u8_url=get_real_url(data.strip(),m3u8_url)
            self.m3u8_url=m3u8_url
            response=requests.get(m3u8_url, headers=headers,verify=False)
            self.logger=logger_helper("解析m3u8",f"{self.m3u8_url}")
            content=response.text
            has_already=False
            
        #写入文件
        if not has_already and content:
            open(m3u8_path,"w",encoding="utf-8-sig").write(content)
            
            
        self._m3u8=content
        try:
            header=content.split('#EXTINF:')[0].replace(",","\n")

            self.logger.debug("内容头",f"\n{header}\n")
        except:
            pass
        # print(content)
        # 正则表达式模式
        self._init_urls(content)
        self._init_keys(content)
        
    @property
    def key_valid(self)->bool:
        return bool(self.key)== bool(self.iv)
    
    
    @staticmethod
    def handle_m3u8_data(raw_m3u8_data,m3u8_url):
        if "#EXT-X-STREAM-INF" in raw_m3u8_data:
            rows=[data for data in raw_m3u8_data.split("\n") if data]
            data=rows[-1]
            rows[-1]=get_real_url(data.strip(),m3u8_url)
            return "\n".join(rows)
        return raw_m3u8_data
    @property
    def m3u8(self)->str:
        if not self._m3u8:
            self._m3u8=self._m3u8_path
        return self._m3u8
    @property
    def m3u8_hash(self)->str:
        return hash_text(self.m3u8,max_length=128)
    @exception_decorator(error_state=False)
    def _init_urls(self,content):
        pattern = re.compile(r'#EXTINF:(.*?),\s*(\S+)\s')

        matches = pattern.findall(content)
        if not matches:
            return
        playlist=[]
        for val in matches :
            duration, ts_file =val
            playlist.append([float(duration),get_real_url(ts_file,self.m3u8_url)])
        
        arrage_lst= arrange_urls(playlist)   
            
        dest_list=[[index,seg["duration"],seg["url"]]    for index,seg in enumerate(arrage_lst) if seg["valid"]]
        
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
    def key(self)->bytes:
        if not self.uri:
            return None
        if self._key and self._key.data_valid:
            return self._key.data
        #二进制文件
        self._key=TinyFetch(local_path=self.key_temp_path)
        data=self._key.data
        if self._key.data_valid:
            return data
        
        #utf-8-sig文件 
        self._key.set_read_func(read_from_txt_utf8_sig)
        self._key.set_write_func(write_to_txt_utf8_sig)
        self._key.set_local_path(self.key_path)

        #通过url下载
        url=self.uri
        if not is_http_or_https(url):
            org_path=Path(self.m3u8_url)
            name=org_path.name
            url=self.m3u8_url.replace(name,self.uri)
        self._key.set_url(url)
        data=self._key.data
        if self._key.data_valid:
            return data
            

        
        
        
        return 

    @property
    def domain(self):
        return get_homepage_url(self.m3u8_url)
    @property
    def suffix(self)->str:
        if self.playlist:
            return postfix(self.playlist[0][2])
        return ".ts"

    @property
    def key_path(self)->str:
        raw_path=Path( self._m3u8_path)
        cur_path=raw_path.parent.parent/"key"/f"{raw_path.stem}_enc.key"
        return str(cur_path)

    @property
    def key_temp_path(self)->str:
        raw_path=Path( self.key_path)
        cur_path=raw_path.parent.parent/"keys"/title(raw_path.name)
        return str(cur_path)

@exception_decorator(error_state=False)
def load_url_data(url_json_path)->dict:
    if  not os.path.exists(url_json_path):
        return
    with open(url_json_path,"r",encoding="utf-8-sig") as f:
        data=json.load(f)
        return data
    return None
    
@exception_decorator(error_state=False)
def save_url_data(url_json_path,data):
    with open(url_json_path,"w",encoding="utf-8-sig") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

def save_m3u8_data(m3u8_path,data):
    with open(m3u8_path,"w",encoding="utf-8-sig") as f:
        f.write(data)


def load_m3u8_data(m3u8_path):
    with open(m3u8_path,"r",encoding="utf-8-sig") as f:
        return f.read()

@exception_decorator(error_state=False)
def get_url_data(url,url_json_path,m3u8_path)->dict:
    info=get_url_info(url,url_json_path,m3u8_path)

    try:    
        key=info.get("key","")
        iv=info.get("iv","")
        if key:
            key=base64_utf8_to_bytes(key)
        if iv:
            iv=base64_utf8_to_bytes(iv)
        # return None,None,info.get("playlist",[]),info.get("total_len",0)
        return key,iv,info.get("playlist",[]),info.get("total_len",0),info.get("re_decode",False)
    except:
        return None,None,info.get("playlist",[]),info.get("total_len",0),False
        
@exception_decorator(error_state=False)
def get_url_info(url,url_json_path,m3u8_path)->dict:
    info=load_url_data(url_json_path)
    info_valid=info and( bool(info.get("key")) == bool( info.get("iv")))
    if not info or not info_valid:
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
        
        info["re_decode"]=True if not info_valid else False
        
        
        #保存
        save_url_data(url_json_path,info)

    return info
    
if __name__ == "__main__":
    url="https://vv.jisuzyv.com/play/nelLE2ge/index.m3u8"

    from base import worm_root
    url_json_path=worm_root/r"player\urls\宝宝巴士之神奇简笔画_01-97db3c6d.json"
    m3u8_path=worm_root/r"player\m3u8\宝宝巴士之神奇简笔画_01-97db3c6d.m3u8"
    data=get_url_data(url,url_json_path,m3u8_path)
    print(data)