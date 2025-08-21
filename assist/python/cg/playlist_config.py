import os
from base import hash_text,normal_path
import re


root_path=r"F:\worm_practice/player/"
root_temp_dir= os.path.join(root_path,"temp")
video_dir= os.path.join(root_path,"video")
url_dir= os.path.join(root_path,"urls")
m3u8_dir= os.path.join(root_path,"m3u8")
video_xlsx= os.path.join(root_path,"video.xlsx")


os.makedirs(root_temp_dir,exist_ok=True)
os.makedirs(video_dir,exist_ok=True)
os.makedirs(url_dir,exist_ok=True)
os.makedirs(m3u8_dir,exist_ok=True)

def video_hash_name(video_name:str):
    return hash_text(video_name)
def dest_video_path(video_name:str):
    return  os.path.join(video_dir,f"{video_name}.mp4")
def temp_video_dir(video_name:str):
    cur_dir=os.path.join(root_temp_dir,video_hash_name(video_name))
    os.makedirs(cur_dir,exist_ok=True)
    return  cur_dir


def url_json_path(vieo_name:str):
    return os.path.join(url_dir,f"{cache_name(vieo_name)}.json")

def m3u8_path(vieo_name:str):
    return os.path.join(m3u8_dir,f"{cache_name(vieo_name)}.m3u8")

def cache_name(video_name:str):
    return f"{video_name}-{video_hash_name(video_name)}"

listent_shop_api=["hls/index.m3u8","hls/mixed.m3u8","index.m3u8","master.m3u8","*/master.m3u8*"]
# 
# listent_shop_api=["*/index.m3u8"]

url_id="url"
m3u8_url_id="m3u8_url"
video_title_id="title"
video_name_id=video_title_id
hash_id="hash"
download_status_id="download"

video_sheet_name="video"



