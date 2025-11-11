from base import download_sync,xml_tools,xml_files,xml_files,read_from_txt_utf8_sig,exception_decorator
from pathlib import Path
from lxml import etree
import pandas as pd
import re
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

def fetch_mp3_list_imp(xml_content)->dict:
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
            "音频标题": title,
            "href": href,
        })

    return result


def get_name(name:str):
    pattern=r"\d+(.*)"
    match=re.search(pattern,name)
    if match:
        name=match.group(1)
        
        
    return name.replace(" ","").replace(".","").replace("讲|","")
    
    pass

@exception_decorator(error_state=False)
def get_audio_imp(root):
 # ---------------------- 提取第1组信息：o-hidden a_D 的文本 + 子元素href ----------------------
        # 定位目标div（class="o-hidden a_D"），取其下的<a>标签
        target_div = root.xpath('.//div[@class="o-hidden a_D"]/a')[0]
        # 文本内容（音频标题）
        o_hidden_text = target_div.xpath('text()')[0].strip()
        # a标签的href属性
        a_href = target_div.xpath('@href')[0].strip()


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
            "音频标题": o_hidden_text,
            "href": a_href,
            "专辑名称": gray6_text,
            "时长":duration_text,
            "播放量": gray9_text,
        }


def get_album_lst():
    
    
    
    cur_dir=Path(r"E:\旭尧\睡前故事")
    xml_path=cur_dir/r"晓北姐姐讲故事.xml"
    html_content=read_from_txt_utf8_sig(xml_path)
        
        
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
    
    df["num"]=  df.groupby("专辑名称",sorted=True).cumcount()+1
    df["name"]=df.apply(lambda x:   f'{x["num"]:02}_{get_name(x["音频标题"])}',axis=1)
    
    df.to_excel(xml_path.with_suffix(".xlsx"),sheet_name="audio",index=False)
    
def fetch_mp3_list():
    
    results=[]
    cur_dir=Path(r"F:\worm_practice\player\audio")
    for xml_file_path in xml_files(cur_dir):
        xml_content = read_from_txt_utf8_sig(xml_file_path)
        result=fetch_mp3_list_imp(xml_content)
        if result:
            results.extend(result)
            
    if not results:
        return
    df=pd.DataFrame(results)
    
    df["name"]=df.apply(lambda x:f'{x["序号"].zfill(3)}_{get_name(x["音频标题"])}',axis=1)
    
    # df["name"]=df["序号"]+"_"+get_name(df["音频标题"])
    df.to_excel(cur_dir/"audio.xlsx",sheet_name="audio",index=False)


if __name__ == '__main__':
    # fetch_mp3_list()
    get_album_lst()