from base import download_sync,xml_tools,xml_files,xml_files,read_from_txt_utf8_sig,exception_decorator,format_count
from pathlib import Path
from lxml import etree
import pandas as pd
import re


downloaded_id="downloaded"
href_id="href"
album_id="album"
name_id="name"
num_id="num"
url_id="url"
dest_path_id="dest_path"
album_name_id="专辑名称"
title_id="音频标题"
duration_id="时长"
view_coount_id="播放量"
release_time_id="发布时间"
local_path_id="local_path"
#喜马拉雅睡前故事
def download_mp3():
    headers = {
    'authority': 'a.xmcdn.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'range': 'bytes=0-',
    'referer': 'https://www.ximalaya.com/',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'audio',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',  
    }
    dest_dir=Path(r"F:\worm_practice\player\audio")
    # url="https://a.xmcdn.com/storages/268c-audiofreehighqps/45/12/GKwRIJIHQNpWACCcTAHGoowt-aacv2-48K.m4a?sign=9b9177ef3a2756b20dcad70aaf633604&buy_key=www2_a8c13baa-134401591:494220481&timestamp=1762851689194000&token=5747&duration=263"
    url="https://a.xmcdn.com/storages/268c-audiofreehighqps/45/12/GKwRIJIHQNpWACCcTAHGoowt-aacv2-48K.m4a?sign=9b9177ef3a2756b20dcad70aaf633604&buy_key=www2_a8c13baa-134401591:494220481"
    dest_path=dest_dir/"97_蚂蚁的力量.mp3"
    success= download_sync(url,dest_path,headers=headers)
    print(success)

def fetch_mp3_list_imp(xml_content)->list:
    # 2. 解析 XML/HTML
    tree = etree.HTML(xml_content)  # 用 etree.HTML 解析（兼容 HTML 格式）

    # 3. 定位所有音频项的根节点 <li class="_nO">
    audio_items = tree.xpath('//li[@class="_nO"]')

    # 4. 遍历每个音频项，提取目标数据
    result = []
    for item in audio_items:
        # 提取 <span class="num _nO"> 的文本（序号）
        num = item.xpath('.//span[@class="num _nO"]/text()')[0]  # .// 表示在当前 <li> 下查找
        
        # 提取 <div class="text _nO"> 下 <a> 标签的 href 属性
        href = item.xpath('.//div[@class="text _nO"]/a/@href')[0]
        
        # 提取 <span class="title _nO"> 的文本（音频标题）
        title = item.xpath('.//span[@class="title _nO"]/text()')[0]
        
        # 存入结果列表
        result.append({
            "序号": num,
            title_id: title,
            "href": href,
        })

    return result


def get_title_name(name:str):
    num_pattern=r"^\d+(.*)"
    match=re.search(num_pattern,name)
    if match:
        name=match.group(1).strip()
        
    prefix_pattern=r"^【.*?】(.*?)【.*】$"
    match=re.search(prefix_pattern,name)
    if match:
        name=match.group(1).strip()
        
    suffix_pattern=r"(.*)【.*】$"
    match=re.search(suffix_pattern,name)
    if match:
        name=match.group(1).strip()
    
    return name.replace(" ","").replace(".","").replace("讲|","")
    
def get_album_name(album_name:str):
    if not album_name:
        return ""
    pattern = r'[|｜]'
    
    lst=re.split(pattern, album_name)
    return lst[0].strip() if len(lst)>0 else album_name

@exception_decorator(error_state=False)
def get_audio_imp(root):
 # ---------------------- 提取第1组信息：o-hidden a_D 的文本 + 子元素href ----------------------
 
        target_root=root.xpath('.//div[@class="o-hidden a_D"]')[0]

        # 定位目标div（class="o-hidden a_D"），取其下的<a>标签
        target_div = target_root.xpath('./a')[0]
        # 文本内容（音频标题）
        o_hidden_text = target_div.xpath('text()')[0].strip()
        # a标签的href属性
        a_href = target_div.xpath('@href')[0].strip()
        #时间 <div class="fr gray-9 a_D">2019-04</div>
        date_val=target_root.xpath('.//div[@class="fr gray-9 a_D"]/text()')[0].strip()

        # ---------------------- 提取第2组信息：p-t-5 p-b-15 a_D 下的 gray-6 a_D 文本 ----------------------
        # 定位div，再找子级span（避免匹配其他span.gray-6）
        gray6_text = root.xpath(
            './/div[@class="p-t-5 p-b-15 a_D"]//span[@class="gray-6 a_D"]/text()'
        )[0].strip()

        # ---------------------- 提取第3组信息：fl a_D 下的 gray-9 a_D 文本（播放量） ----------------------
        # 关键：排除带 "p-r-20" class 的div（避免匹配时间"01:26"）
        gray9_text = root.xpath(
            './/div[@class="fl a_D" and not(@class="fl p-r-20 a_D")]//span[@class="gray-9 a_D"]/text()'
        )[0].strip()
        
        # ---------------------- 提取第43组信息：fl a_D 下的 gray-9 a_D 文本（播放量） ----------------------
        # 关键：排除带 "p-r-20" class 的div（避免匹配时间"01:26"）
        duration_text = root.xpath(
            './/div[@class="fl p-r-20 a_D"]//span[@class="gray-9 a_D"]/text()'
        )[0].strip()
        
        # 存入结果
        return {
            title_id: o_hidden_text,
            href_id: f"https://www.ximalaya.com{a_href}",
            album_name_id: gray6_text,
            duration_id:duration_text,
            view_coount_id: gray9_text,
            release_time_id:date_val,
        }
@exception_decorator(error_state=False)
def get_album_lst_from_content(html_content)->pd.DataFrame:
        # 2. 解析HTML
    tree = etree.HTML(html_content)

    # 3. 定位所有音频项的根节点（每个 <div class="o-hidden anchor-detail-track-info-border a_D"> 对应一个音频）
    audio_roots = tree.xpath('//div[@class="o-hidden anchor-detail-track-info-border a_D"]')

    # 4. 遍历每个音频项，提取目标信息
    results = []
    for root in audio_roots:
        
        if (result:=get_audio_imp(root)):
            results.append(result)

    # 5. 格式化输出结果
    df=pd.DataFrame(reversed( results))
    
    
    df[album_id]=df.apply(lambda x: get_album_name(x[album_name_id]),axis=1)
    groups=df.groupby(album_id,sort=True)
    df[num_id]=  groups.cumcount()+1
    count_dict={}
    for name,group in groups:
        count_dict[name]=format_count(len(group) )
    
    def real_name(x):
        zj_name=x[album_id]
        count=count_dict.get(zj_name,3)
        return f'{x[num_id]:0{str(count)}}_{get_title_name(x[title_id])}'
    
    df[name_id]=df.apply(real_name ,axis=1)

    df.sort_values(by=[album_id,name_id],inplace=True, ascending=True)
    # 重置索引（可选，让索引连续）
    df.reset_index(drop=True, inplace=True)
    return df

    



if __name__ == '__main__':

    cur_dir=Path(r"E:\旭尧\睡前故事")
    xml_path=cur_dir/r"晓北姐姐讲故事.xml"
    html_content=read_from_txt_utf8_sig(xml_path)
        
    get_album_lst_from_content(html_content,xml_path.with_suffix(".xlsx"))