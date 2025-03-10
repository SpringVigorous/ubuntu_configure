

# 提供一个爬取网页内容的方法：
# 首先打开网址：https://www.nlxs.org/115/115666/，获取 /html/body/div[7]/ul/ 下的所有 /li 的 a节点的 href属性及/a节点的文本内容，保存到列表中（元素为tuple，即 （url,标题））
# 遍历上述列表，进行如下操作：
# 取出url，定义缓存列表，由于 可能会有分页内容，分页的地址是上述url的路径名除去 点和后缀名后，和数字 1、2、3……的拼接，如：115666.html、115666_2.html、115666_3.html，所以需要循环遍历，直到获取的网页为空为止。每次再根据拼接的url获取网页内容，根据xpath 获取 html 子节点下的 节点<div class="txt" id="txt">，取出 节点下 所有<b></b>节点的文本内容，保存到缓存列表中；最终将上述的缓存列表合并成一个字符串，并保存到本地 目录F:\worm_practice\storys\下，文件名为上述标题.txt，如：115666.txt

import os
import os.path
import requests
from lxml import html, etree



from pathlib import Path

import sys
import re

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import get_homepage_url,is_http_or_https,logger_helper,fetch_sync,UpdateTimeType,arabic_number_tuples,sanitize_filename,chinese_num
import pandas as pd 
import json

from base import as_normal,MultiThreadCoroutine,exception_decorator,except_stack,hash_text,ReturnState
import asyncio,aiohttp
import concurrent.futures
import random  
import math
cookies = {
    '___rl__test__cookies': '1740656330035',
    'Hm_lvt_a9251d29efa34bd37e0613ea0213c2bc': '1740653593',
    'HMACCOUNT': '03AD22591AF7EB0C',
    'Hm_lvt_a32589882f654dfeae472ff2a54ad2ce': '1740653593',
    'OUTFOX_SEARCH_USER_ID_NCOO': '302105423.4216834',
    'Hm_lpvt_a32589882f654dfeae472ff2a54ad2ce': '1740655235',
    'Hm_lpvt_a9251d29efa34bd37e0613ea0213c2bc': '1740655235',
}

headers = {
    'authority': 'www.nlxs.org',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    # 'cache-control': 'max-age=0',
    # Requests sorts cookies= alphabetically
    # 'cookie': '___rl__test__cookies=1740656330035; Hm_lvt_a9251d29efa34bd37e0613ea0213c2bc=1740653593; HMACCOUNT=03AD22591AF7EB0C; Hm_lvt_a32589882f654dfeae472ff2a54ad2ce=1740653593; OUTFOX_SEARCH_USER_ID_NCOO=302105423.4216834; Hm_lpvt_a32589882f654dfeae472ff2a54ad2ce=1740655235; Hm_lpvt_a9251d29efa34bd37e0613ea0213c2bc=1740655235',
    'if-none-match': 'W/"0c8c9030105bf140a4f91d7e7902b4e4"',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Mobile Safari/537.36',
    'cache-control': 'no-cache',  # 添加或修改缓存控制头
}
def dict_first_item(val:dict):
    if not dict:
        return
    
    key= next(iter(val))
    return key,val[key]
proxies = {
  'http': 'http://your_proxy_ip:your_proxy_port',
  'https': 'https://your_proxy_ip:your_proxy_port'
}

# response = requests.get('http://example.com', proxies=proxies)
# print(response.textdef classic_lst():

    #经典推荐
    
    # <ul class="txt-list txt-list-row3">
	# <li>
	# 	<span class="s1">[其他小说]</span>
	# 	<span class="s2">
	# 		<a href="/1/1475/">乡野风流</a>
	# 	</span>
	# 	<span class="s5">
	# 		<a href="/author/%E4%B9%A1%E9%87%8E%E9%A3%8E%E6%B5%81/">乡野风流</a>
	# 	</span>
	# </li>



def new_lst():
    #最新入库小说
    
    # <ul class="txt-list txt-list-row3">
	# <li>
	# 	<span class="s1">[都市言情]</span>
	# 	<span class="s2">
	# 		<a href="/163/163521/">陆颜夕傅衍川</a>
	# 	</span>
	# 	<span class="s5">
	# 		<a href="/author/%E9%99%86%E9%A2%9C%E5%A4%95%E5%82%85%E8%A1%8D%E5%B7%9D/">陆颜夕傅衍川</a>
	# 	</span>
	# </li>
    pass
def completed_lst():
    #已完结热门小说推荐
    #eg:https://www.nlxs.org/mybook.html
    # <div class="layout layout-col3">
    #     <div class="item">
    #         <div class="image">
    #             <a href="/29/29400/">
    #                 <img style="min-height:120px" src="/img/29400.jpg" onerror='this.src="/qs_theme/defaultimg.png"' alt="薄总，再倔，太太就要嫁人啦！">
    #                 </a>
    #             </div>
    #             <dl>
    #                 <dt>
    #                     <span>是朕啊</span>
    #                     <a href="/29/29400/">薄总，再倔，太太就要嫁人啦！</a>
    #                 </dt>
    #                 <dd style="height:90px">
    #                     <a href="/29/29400/" style="color:#555">裴景夏作为薄家太子爷的下堂妻，整个溪城的人都在等着看戏，看这位裴小姐会如何哭着闹着求薄纪渊复婚。但裴景夏却表示勿cue那狗男人，谁喜欢谁拿去，她不要了！薄纪渊，溪城薄家太子爷，薄氏集团现任总裁，钻石王老五中的王老五。却在四年前，...</a>
    #                 </dd>
    #             </dl>
    #         </div>

    pass

def new_flag():
    # <ul class="txt-list txt-list-row5">
    #     <a href="/biquge/1668212.html">心海的秘密基地位置</a>&nbsp;&nbsp;
    #     <a href="/biquge/1668023.html">许逸阳顾思佳</a>&nbsp;&nbsp;
    
    pass
#封面推荐
def recommend_lst():
    #封面推荐-在下面网页中，每个类目的首页
    # <div class="rec-focus">
    #     <dl class="rec-focus-book">
    #         <dt class="book-img">
    #             <a href="/86/86705/">
    #                 <img height="100" width="80" src="/img/86705.jpg" onerror='this.src="/qs_theme/defaultimg.png"' alt="七零宠婚，娇气包勾得科研大佬日日沦陷">
    #                 </a>
    #             </dt>
    #             <dd class="book-info">
    #                 <h2>
    #                     <a href="/86/86705/">七零宠婚，娇气包勾得科研大佬日日沦陷</a>
    #                 </h2>
    #                 <p>作者：甜菜瓜</p>
    #                 <p>娇气包科研天才爹系母女双穿甜宠日常母上大人搞钱我躺平周芸芸跟母上大人齐齐穿越到一部短剧里，在还没...</p>
    #             </dd>
    #         </dl>

    pass

def sh():
    # <div class="layout layout-col2">
    #     <div class="item">
    #         <div class="image">
    #             <a href="/59/59822/">
    #                 <img style="min-height:120px" src="/img/59822.jpg" onerror='this.src="/qs_theme/defaultimg.png"' alt="嚣妃，强个王爷玩">
    #                 </a>
    #             </div>
    #             <dl>
    #                 <dt>
    #                     <span>夜香暗袭</span>
    #                     <a href="/59/59822/">嚣妃，强个王爷玩</a>
    #                 </dt>
    #                 <dd style="height:90px">
    #                     <a href="/59/59822/" style="color:#555">推荐暗暗的完结文嚣妃，你狠要命，点上面其他作品即可进。女强男强，强强联手。野心女PK腹黑男YY剧场他将她禁锢在水里，手狠狠地撕落她身上的衣裳，在她来不及惊呼的时候，...</a>
    #                 </dd>
    #             </dl>
    #         </div>
    pass

def get_story_lst():
    #更新列表
    #最近更新小说列表
    
    chapters = []
    
    base_url = 'https://www.nlxs.org/list/' #5-6.html
    domain=get_homepage_url(base_url)
    
    # 正则表达式模式
    chapter_pattern = re.compile(r'\[(.*)\]')
    
    category_index=1
    
    logger=logger_helper(f"catelogy:{category_index}")
    try:
        while True:
            page=1
            
            valid_count=len(chapters)
            while True:
                cur_url=f"{base_url}{category_index}-{page}.html"
                logger.update_target(cur_url)
                logger.update_time(UpdateTimeType.ALL)
                
                page+=1
                response = requests.get(cur_url, cookies=cookies, headers=headers)
                if response.status_code != 200:
                    logger.warn("失败")

                    break

                tree = html.fromstring(response.content)
                #最近更新小说列表
                lis_all = tree.xpath('//ul[@class="txt-list txt-list-row5"]')
                if not lis_all:
                    lis_all = tree.xpath('//ul[@class="sort_list"]')
                    if not lis_all:
                        break
                
                lis = lis_all[0].xpath('./li')
                if not lis:
                    break
                
                for li in lis:
                    catelog=li.xpath('.//span[@class="s1"]')[0].xpath('text()')[0].strip()
                    info=li.xpath('.//span[@class="s2"]/a')[0]
                    
                    url=info.xpath('@href')[0]
                    title=info.xpath('text()')[0].strip()
                    author=li.xpath('.//span[@class="s4"]')[0].xpath('text()')[0].strip()
                    date=li.xpath('.//span[@class="s5"]')[0].xpath('text()')[0].strip()
                    
        
                    if not is_http_or_https(url):
                        url = domain + url
                    # 使用正则表达式提取章节编号和标题
                    match = chapter_pattern.match(catelog)
                    if match:
                        catelog = match.group(1)

                    chapters.append({"catelog":catelog,"title":title,"author":author,"date":date,"url":url}) 
                    
                logger.info("成功",update_time_type=UpdateTimeType.ALL)     
            category_index+=1 
            if valid_count==len(chapters):
                break
    except Exception as e:
        logger.error(e)
    return chapters



def extract_after_colon(text):
    # 正则表达式匹配第一个冒号之后的内容
    match = re.search(r'：\s*(.*)', text)
    if match:
        return match.group(1).strip()
    else:
        return None
    
# <div class="bookname">混沌龙帝</div>
    
# <h2 class="layout-tit xs-hidden">
# 	<a href="/">纳兰小说</a>&gt;
# 	<a href="/4/4436/">混沌龙帝</a> &gt; 第1章（第1页）
# </h2>
def title_form_detail(url):
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return

    tree = html.fromstring(response.content)
    title=tree.xpath('//div[@class="bookname"]/text()')
    if title:
        return title[0]
    
    titles = tree.xpath('//h2[@class="layout-tit xs-hidden"]/a/text()')
    return titles[1] if titles and len(titles)>1 else ""
    
# <div class="info">
# 	<div class="top">
# 		<h1>剧情扭曲之后</h1>
# 		<div class="fix">
# 			<p>作&nbsp;&nbsp;者：南辿星</p>
# 			<p class="xs-show">类&nbsp;&nbsp;别：玄幻魔法</p>
# 			<p class="xs-show">状&nbsp;&nbsp;态：连载中</p>
# 			<p class="opt">
# 				<span class="xs-hidden">动&nbsp;&nbsp;作：</span>
# 				<a rel="nofollow" href="javascript:addbookcase('http://www.nlxs.org/22/22494/','22494');">加入书架</a>
# 				<i class="xs-hidden">、</i>
# 				<a href="/22/22494/1/">章节目录</a>
# 				<i class="xs-hidden">、</i>
# 				<a href="/22/22494/7520452.html">开始阅读</a>
# 			</p>
# 			<p>最后更新：2025-03-01 15:18:40</p>
# 			<p>最新章节：
# 				<a href="/22/22494/34683053.html">第120章</a>
# 			</p>
# 		</div>
# 	</div>
    
    

# <div class="book-info">
# 	<div class="bookname">
# 		<h1>混沌龙帝</h1>
# 		<span class="author">三诫 著</span>
# 	</div>
# 	<p class="tag">
# 		<span class="blue">玄幻魔法</span>
# 		<span class="green">连载中</span>
# 	</p>
# 	<p class="update">
# 		<span>最近更新：</span>
# 		<a href="http://www.nlxs.org/4/4436/34813892.html">第3809章</a>
# 	</p>
# 	<p class="time">
# 		<span>更新时间：</span>2025-03-03 00:05:47
# 	</p>
# </div>

def info_from_lst(url):
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return
       
    tree = html.fromstring(response.content)

    infos = tree.xpath('//div[@class="info"]')
    if not infos:
        infos = tree.xpath('//div[@class="book-info"]')
        if not infos:
            return
    org_info=infos[0]
    title=org_info.xpath('.//h1/text()')[0]
    info=org_info.xpath('.//p')
    info_txt=org_info.xpath('.//p/text()')
    if len(info_txt)<3:
        return title,None

    author=extract_after_colon(info_txt[0])
    catelog=extract_after_colon(info_txt[1])
    date=extract_after_colon(info_txt[-2])
    
    
    last=arabic_number_tuples(info[-1].xpath('./a')[-1].xpath('text()')[0])[0][1]
    
    
    return title,author,catelog,date,last

def real_title(num,title):
    num=int(num)
    return f"{num:05}_{title}" if title else f"{num:04}"

def get_chapter_list(base_url):
    chapters = {}
    page=0
    domain=get_homepage_url(base_url)
    book_info=info_from_lst(base_url)
    
    theme=book_info[0] if  book_info else ""
    logger=logger_helper(theme,base_url)
    logger.info("开始获取章节列表")
    # 正则表达式模式
    chapter_pattern = re.compile(r'\S([0-9'+ chinese_num + r']+)\S\s*(\S*)')
    
    indexes={}
    while True:
        
        cur_url=f"{base_url}{page}/" if page > 0 else base_url
        page+=1
        response=None
        try:
            response = requests.get(cur_url, cookies=cookies, headers=headers, timeout=10)
        except:
            logger.error("异常",except_stack(),update_time_type=UpdateTimeType.ALL)
            return 
        if response.status_code != 200:
            break

        logger.update_target(detail=cur_url)
        tree = html.fromstring(response.content)
        # if not theme:
        #     theme=title_form_detail(cur_url)
        #     try:
        #         theme = tree.xpath('//h2[@class="layout-tit xs-hidden"]/a/text()')[1]
        #         if theme:
        #             logger.update_target(target=theme)
        #     except:
        #         pass
            
        lis_all = tree.xpath('//ul[@class="chapter-list"]')
        if not lis_all:
            lis_all = tree.xpath('//ul[@class="fix section-list"]')
            if not lis_all:
                break
        lis = lis_all[-1].xpath('./li')
        if not lis:
            break

        valid_count=len(chapters)
        
        for li in lis:
            a_tag = li.xpath('.//a')[0]
            url = a_tag.xpath('@href')[0]
            if not is_http_or_https(url):
                url = domain + url
            if not url:
                continue
            
            titles=a_tag.xpath('text()')
            
            title = titles[0].strip() if titles else hash_text(url,strict_no_num=True)
            org_title=title
            # 使用正则表达式提取章节编号和标题
            match = chapter_pattern.match(title)
            if match:
                chapter_number =arabic_number_tuples( match.group(1))[0][-1]
                chapter_title = match.group(2)             
                logger_fun=logger.trace if chapter_title else logger.warn
                title=real_title(chapter_number,chapter_title)
                logger_fun(f"匹配标题:{org_title}->{title}",update_time_type=UpdateTimeType.STEP)  
            else:
                # 如果不匹配，可以选择记录日志或跳过
                logger.warn(f"未匹配标题: {org_title}",update_time_type=UpdateTimeType.STEP)  
            if chapters.get(url):  # 如果url已经存在，则跳过
                continue  
            chapters[url]=title
            
            indexes[len(chapters)-1]=bool(match)
            
        add_count=len(chapters)-valid_count
        logger.info("完成",f"本次添加{add_count}个",update_time_type=UpdateTimeType.STAGE)
        if add_count<1:
            break   
            # chapters.append((url, title))
    logger.update_target(detail=base_url)
    logger.info("完成",f"共{len(chapters)}个",update_time_type=UpdateTimeType.ALL)
    
    
    
    if not all( item[1]==index+1  for index,item in chapters.items() ):  # 如果所有章节标题都匹配成功，则跳出循环
        
        
        keys=list(chapters.keys())
        chapters={key:(val if indexes[keys.index(key)] else real_title(keys.index(key)+1,val) ) for key,val in chapters.items()}

    chapters={val:key for key,val in chapters.items()} 
    return reset_dict_num(chapters)

def process_chapters(chapters,base_temp_dir):
    
    
    for title ,url in chapters.items():

        cur_dir=os.path.join(base_temp_dir, title)
        os.makedirs(base_temp_dir, exist_ok=True)

        save_path = os.path.join(cur_dir, f"{title}.txt")
        if os.path.exists(save_path):  # 如果文件已经存在，则跳过
            continue

        logger=logger_helper(url,save_path)
        
        base_url = url.rsplit('.', 1)[0]  # 移除扩展名

        
        content = []
        page = 0
        success_count=0
        while True:
            page_url = f"{base_url}_{page}.html" if page > 0 else url
            page += 1
            
            # cur_content=fetch_sync(page_url,max_retries=3,timeout=5, cookies=cookies, headers=headers)
            # if not cur_content:
            #     break
            response = requests.get(page_url, cookies=cookies, headers=headers)
            if response.status_code != 200 or response.url != page_url:
                # logger.warn(f"{page} is not found")
                if page>1:
                    break
                else:
                    # pass
                    continue
                
            cur_content=response.content
            tree = html.fromstring(cur_content)
            txt_div = tree.xpath('//div[@class="txt" and @id="txt"]')
            # print(etree.tostring(txt_div, pretty_print=True, method='html', encoding='unicode'))
            if not txt_div:
                txt_div = tree.xpath('//div[@class="word_read"]')
                if not txt_div:
                    logger.warn(f"{page_url} 内容为空")
                    continue
            
            
            b_tags = txt_div[0].xpath('.//p/text()')
            
            content.extend(b_tags)
            success_count+=1
        if not content:
            continue
        try:
            logger.trace("保存成功",f"个数:{success_count}")
            with open(save_path, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(content))
        except Exception as e:
            print(f"Error occurred while writing to file: {e}")
@exception_decorator()
async def get_chapters_data(semaphore,args:list|tuple):
        async with semaphore:
            title,url,keys=args
            if title in keys:  # 如果文件已经存在，则跳过
                return

            logger=logger_helper(url,title)
            
            base_url = url.rsplit('.', 1)[0]  # 移除扩展名

            content = []
            page = 0
            success_count=0
            
            # await asyncio.sleep( random.uniform(0.005, 0.8))
            
            async with aiohttp.ClientSession() as session:
                while True:
                    page_url = f"{base_url}_{page}.html" if page > 0 else url
                    page += 1
                    
                    async with session.get(page_url, cookies=cookies, headers=headers) as response:
                        if response.status != 200 or str(response.url) != page_url:
                            # logger.warn(f"{page} is not found")
                            if page>1:
                                break
                            else :
                                # pass
                                continue
                            
                        cur_content=await response.read()
                        tree = html.fromstring(cur_content)
                        txt_div = tree.xpath('//div[@class="txt" and @id="txt"]')
                        # print(etree.tostring(txt_div, pretty_print=True, method='html', encoding='unicode'))
                        if not txt_div:
                            txt_div = tree.xpath('//div[@class="word_read"]')
                            if not txt_div:
                                logger.warn(f"{page_url} 内容为空")
                                continue
                        
                        
                        b_tags = txt_div[0].xpath('.//p/text()')
                        
                        content.extend(b_tags)
                        success_count+=1
                if not content:
                    return
                try:
                    logger.trace("保存成功",f"个数:{success_count}",update_time_type=UpdateTimeType.ALL)
                    return (title,'\n'.join(content))
                except Exception as e:
                    print(f"Error occurred while writing to file: {e}")
@exception_decorator()
def mutithread_chapters_data(chapters,datas:dict=None):

    keys=datas.keys() if datas else []
    if not datas:
        datas={}
        
    first_url= dict_first_item(chapters)[1] if chapters else None
    theme=title_form_detail(first_url) if first_url else ""
    playlist_logger=logger_helper(f"{theme}-下载",f"共{len(chapters)}章")
    
    params=[(key,url,keys)  for key,url in chapters.items() if key not in keys]
    if not params:
        playlist_logger.info("完成",f"已下载{len(datas)}章",update_time_type=UpdateTimeType.ALL)
        return datas
    
    multi_thread_coroutine = MultiThreadCoroutine(get_chapters_data,params,threads_count=10, concurrent_task_count=10,semaphore_count=50)
    try:
        asyncio.run(multi_thread_coroutine.run_tasks()) 
        success=multi_thread_coroutine.success
        if not success:
            info=[multi_thread_coroutine.fail_infos,except_stack()]
            info_str="\n".join(info)
            playlist_logger.error("异常",f"\n{info_str}\n",update_time_type=UpdateTimeType.ALL)
        for items in multi_thread_coroutine.result :
            if items:
                for item in items:
                    if item:
                        title,data=item
                        datas[title]=data
                
                
        playlist_logger.info("完成",f"已下载{len(datas)}章",update_time_type=UpdateTimeType.ALL)
    except Exception as e:
        playlist_logger.error("下载异常",f"已下载{len(datas)}章\n{except_stack()}",update_time_type=UpdateTimeType.ALL)
    finally:
        return reset_dict_num(dict(sorted(datas.items())))
    
def process_chapters_data(chapters,datas:dict=None):

    keys=datas.keys() if datas else []
    if not datas:
        datas={}
        
        
        
    for title ,url in chapters.items():
        if title in keys:  # 如果文件已经存在，则跳过
            continue

        logger=logger_helper(url,title)
        
        base_url = url.rsplit('.', 1)[0]  # 移除扩展名

        
        content = []
        page = 0
        success_count=0
        while True:
            page_url = f"{base_url}_{page}.html" if page > 0 else url
            page += 1
            
            # cur_content=fetch_sync(page_url,max_retries=3,timeout=5, cookies=cookies, headers=headers)
            # if not cur_content:
            #     break
            response = requests.get(page_url, cookies=cookies, headers=headers)
            if response.status_code != 200 or response.url != page_url:
                # logger.warn(f"{page} is not found")
                if page>1:
                    break
                else:
                    # pass
                    continue
                
            cur_content=response.content
            tree = html.fromstring(cur_content)
            txt_div = tree.xpath('//div[@class="txt" and @id="txt"]')
            # print(etree.tostring(txt_div, pretty_print=True, method='html', encoding='unicode'))
            if not txt_div:
                txt_div = tree.xpath('//div[@class="word_read"]')
                if not txt_div:
                    logger.warn(f"{page_url} 内容为空")
                    continue
            
            
            b_tags = txt_div[0].xpath('.//p/text()')
            
            content.extend(b_tags)
            success_count+=1
        if not content:
            continue
        try:
            logger.info("提取内容成功",f"个数:{success_count}",update_time_type=UpdateTimeType.ALL)
            datas[title]='\n'.join(content)
        except Exception as e:
            print(f"Error occurred while writing to file: {e}")
            
    return dict(sorted(datas.items()))

    


def format_filename(filename, width=40, fillchar=' '):
    """
    格式化文件名，使其居中并用 fillchar 填充到指定宽度
    """
    filename = os.path.splitext(os.path.basename(filename))[0]  # 去掉扩展名
    formatted_name = filename.center(width, fillchar)
    return formatted_name

def merge_txt_files(source_dir, target_file):
    """
    合并指定目录中的所有 .txt 文件到目标文件中
    """
    # 确保目标文件路径存在
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    
    with open(target_file, 'w', encoding='utf-8-sig') as outfile:
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    formatted_name = format_filename(file)
                    
                    # 写入格式化后的文件名
                    outfile.write(formatted_name + '\n\n')
                    
                    # 读取并写入文件内容
                    with open(file_path, 'r', encoding='utf-8-sig') as infile:
                        outfile.write(infile.read())
                    
                    # 写入分隔符
                    outfile.write("\n\n")

def export_datas(datas:dict, target_file):
    
    """
    合并指定目录中的所有 .txt 文件到目标文件中
    """
    # 确保目标文件路径存在
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    
    with open(target_file, 'w', encoding='utf-8-sig') as outfile:
        for title,data in sorted(datas.items()):
            outfile.write(title.center(40, " ")+'\n\n')
            outfile.write(data)
            # 写入分隔符
            outfile.write("\n\n")
            

def reset_dict_num(dict_data:dict)->dict:
    if not dict_data:
        return
    
    first_key=dict_first_item(dict_data)[0]
    
    num_len=len(first_key.split("_")[0])
    count=len(dict_data)
    if (count<pow(10,num_len)and count>=pow(10,num_len-1)):
        return dict_data
    num_len=math.ceil(math.log10(count))
    logger=logger_helper(f"重置编号,eg:{first_key}",f"{count}->{num_len}")
    dest_datas={}
    for key,val in dict_data.items():
        titles=key.split("_")
        
        new_key=key
        if titles :
            num=int(titles[0])
            titles[0]=f"{num:0{num_len}}"
            new_key="_".join(titles)

        dest_datas[new_key]=val
    # return dict_data 
    logger.info("完成",update_time_type=UpdateTimeType.ALL)
    # dest_datas={f"{int(key):0{num_len}}":val   for key,val in dict_data.items()}
    return dict(sorted(dest_datas.items()))


def reset_json_order(json_path):
    if not os.path.exists(json_path):
        return
    logger=logger_helper("读取已有文件",json_path)
    datas=json.load(open(json_path,'r',encoding='utf-8-sig'))
    dest_datas=reset_dict_num(datas)
    changed= datas.keys()!=dest_datas.keys()
    if changed:
        logger.info("重置顺序，并保存",update_time_type=UpdateTimeType.STEP)
        json.dump(dest_datas, open(json_path,'w',encoding='utf-8-sig'),ensure_ascii=False,indent=4)
    logger.info("读取完成",update_time_type=UpdateTimeType.ALL)
    return dest_datas



if __name__ == "__main__":
     

    root_dir = r'F:\worm_practice\storys'
    dest_dir=os.path.join(root_dir,'dest')
    temp_dir=os.path.join(root_dir,'temp')

    os.makedirs(dest_dir,exist_ok=True)
    os.makedirs(temp_dir,exist_ok=True)
    #获取小说列表
    base_url_xlsx=os.path.join(temp_dir,'urls.xlsx')
    df=None
    if os.path.exists(base_url_xlsx):
        df=pd.read_excel(base_url_xlsx)
    else:
        lst=get_story_lst()
        df=pd.DataFrame(lst)
        df["last"]=0
        df.drop_duplicates(subset='url',inplace=True)
        df.to_excel(base_url_xlsx, index=False)
    
    for index,row in df.iterrows():
        if index<756:
            continue
        
        url=row["url"]
        title=row["title"]
        author=row["author"]
        date=row["date"]
        last=row["last"]
        
        info=info_from_lst(url)
        if info and len(info)>2:
            detail_title,detail_author,detail_catelog,detail_date,detail_last=info
            #修正值
            title=detail_title if detail_title else title
            author=detail_author if detail_author else author
            date=detail_date if detail_date else date
            last=detail_last if detail_last else last
            
        logger=logger_helper(f"第{index+1}个_{title}",url)

        file_title=sanitize_filename(title,limit_length=80)
        
        cur_temp_dir=os.path.join(temp_dir,file_title)
        os.makedirs(cur_temp_dir,exist_ok=True)
        logger.info("开始","获取章节URL",update_time_type=UpdateTimeType.STAGE)
        
        #各个章节的地址
        base_url_json=os.path.join(cur_temp_dir,f"{file_title}_url.json")
        
        if os.path.exists(base_url_json):
            # chapters=json.load(open(base_url_json,'r',encoding='utf-8-sig'))
            
            #重新编号
            chapters=reset_json_order(base_url_json)
            
        else:
            chapters = get_chapter_list(url)
            if not chapters:
                logger.error("失败",update_time_type=UpdateTimeType.STAGE)
                continue
            
            json.dump(chapters, open(base_url_json,'w',encoding='utf-8-sig'),ensure_ascii=False,indent=4)
            
        #各个章节的内容
        base_data_json=os.path.join(cur_temp_dir,f"{file_title}_data.json")
        datas={}
        if os.path.exists(base_data_json):
            # datas=json.load(open(base_data_json,'r',encoding='utf-8-sig'))
            #重新编号
            datas=reset_json_order(base_data_json)
        org_len=len(datas)
        
        logger.info("完成","获取章节URL",update_time_type=UpdateTimeType.STAGE)
        logger.info("开始","获取章节内容")
               
        dest_datas=mutithread_chapters_data(chapters,datas)
        if isinstance(dest_datas,ReturnState) and not dest_datas.is_success():
            logger.error("失败",update_time_type=UpdateTimeType.STAGE)
            continue
        logger.info("完成","获取章节内容",update_time_type=UpdateTimeType.STAGE)
        changed=len(dest_datas)>org_len or datas.keys()!=dest_datas.keys()
        if changed:
            json.dump(dest_datas, open(base_data_json,'w',encoding='utf-8-sig'),ensure_ascii=False,indent=4)
            
        #最终文件
        target_file = os.path.join(dest_dir,f"{file_title}.txt")
        if dest_datas and changed:
            export_datas(dest_datas, target_file)
        count=len(dest_datas)

        df.loc[index,"title"]=title
        df.loc[index,"last"]= last if (last and last > count ) else count
        df.loc[index,"author"]=author
        df.loc[index,"date"]=date
        
        logger.info("完成",update_time_type=UpdateTimeType.ALL)
        # if index>100:
        #     break
    
    #重新保存
    df.to_excel(base_url_xlsx, index=False)

    os.system("shutdown /s /t 60")
    exit(0)
    

    

    

