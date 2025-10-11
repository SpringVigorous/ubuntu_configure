import os

import requests
from lxml import html
from pathlib import Path
import sys
import re
import pandas as pd
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import random
import math





from base import (
    get_homepage_url, is_http_or_https, logger_helper, fetch_sync, UpdateTimeType,
    arabic_number_tuples, sanitize_filename, chinese_num, exception_decorator,
    except_stack, hash_text, MultiThreadCoroutine,ReturnState,content_tree,
    remove_html_entity,get_node_text,split_flag_to_dict,dict_val,get_node_attr,fill_url,
    pretty_tree, unique,priority_read_excel_by_pandas,priority_read_json,get_node_sub_hrefs,write_dataframe_excel
)

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
    'cache-control': 'no-cache',
}

"""数据库信息
小说信息：catelog,title,author,date,url,last
章节url: index,title,url,update_time
章节内容：index,title,content
"""



tab_catelog_pattern = re.compile(r'\[(.*)\]')





#eg:https://www.nlxs.org/biquge/46608/1/
#获取关联的所有相同的链接
# <div class="desc xs-hidden">《神通不朽》的简介：神通不敌天数？那是神通不够多，不够强！当洪荒世界的先天灵宝、先天至宝成为种种大神通，张乾在羲皇世界掀起了神通狂潮！于羲皇成道，于大千登顶，于洪荒永生！本书书友群：137484968
# 	<a href="/biquge/1106609.html">神通不朽百度百科女主&nbsp;&nbsp;</a>
def refer_story_from_first_catalog(tree,domain,logger):
    if tree is None:
        return None
    lis_all = tree.xpath('.//div[@class="desc xs-hidden"]/a')
    ref_dict={}
    for li in lis_all:
        url = li.xpath('@href')[0]
        if not url:
            continue
        if not is_http_or_https(url):
            url = domain + url

        title = remove_html_entity(li.xpath('text()')[0]).strip()
        if not ref_dict.get(url):
            continue
        ref_dict[url]=title
        logger.trace(f"找到关联小说信息:{title}<->{url}")
    return ref_dict

def extract_after_colon( text,pre_str):
    match = re.search(f'{pre_str}(.*)', text)
    return match.group(1).strip() if match else text


#根据目录列表的第一个目录信息中获取小说信息
def info_from_first_catalog(tree,domain,logger):
    infos = tree.xpath('//div[@class="info"]')
    if not infos:
        infos = tree.xpath('//div[@class="book-info"]')
    if not infos:
        logger.warn("未找到小说信息",f"\n{pretty_tree(tree)}\n" ,update_time_type=UpdateTimeType.STEP)
        return
    
    org_info = infos[0]
    # logger.warn("未找到小说信息",f"\n{pretty_tree(org_info)}\n" ,update_time_type=UpdateTimeType.STEP)
    
    title = org_info.xpath('.//h1/text()')[0]
    
    org_text= get_node_text(org_info.xpath('.//p'))
    info_dict =split_flag_to_dict(org_text,"：")
    author = dict_val(info_dict,"作者") 
    catelog =dict_val(info_dict,"类别")
    
    date =dict_val(info_dict,"最后更新")
    if not date:
        date =dict_val(info_dict,"更新时间")
    
    last_title =dict_val(info_dict,"最新章节")
    if not last_title:
        last_title = dict_val(info_dict,"最近更新")

    if not all([author,catelog,date,last_title]):
        logger.warn("未找到小说信息",f"\n{pretty_tree(org_info)}\n" ,update_time_type=UpdateTimeType.STEP)
    
    results={"title":title,"author":author,"catelog":catelog,"date":date,"last_title":last_title,"refers":refer_story_from_first_catalog(org_info,domain,logger)}

    
    return {key:val for key,val in results.items() if val}


#从具体一页（html）中获取章节列表
# 返回{"url": "title"}
def handle_chapter_lst(tree,domain,logger)->bool:
    chapters:dict={}
    chapter_pattern = re.compile(r'\S([0-9' + chinese_num + r']+)\S\s*(\S*)')
    lis_all = tree.xpath('//ul[@class="chapter-list"]')
    if not lis_all:
        lis_all = tree.xpath('//ul[@class="fix section-list"]')
    if not lis_all:
        lis_all = tree.xpath('//ul[@class="section-list fix ycxsid"]')
    if not lis_all:
        logger.warn("未找到章节列表",f"\n{pretty_tree(tree)}\n" ,update_time_type=UpdateTimeType.STEP)
        
        
        return chapters
    lis = lis_all[-1].xpath('./li')
    if not lis:
        return chapters
    for li in lis:
        a_tag = li.xpath('.//a')[0]
        url = a_tag.xpath('@href')[0]
        if not is_http_or_https(url):
            url = domain + url
        if not url:
            continue
        titles = a_tag.xpath('text()')
        org_title = titles[0].strip() if titles else hash_text(url, strict_no_num=True)
        
        title = org_title

        match = chapter_pattern.match(org_title)                    
        if match:

            title = match.group(2)
            logger_fun = logger.trace if title else logger.warn
            logger_fun(f"匹配标题:{org_title}->{title}", update_time_type=UpdateTimeType.STEP)
        else:
            logger.warn(f"未匹配标题: {org_title}", update_time_type=UpdateTimeType.STEP)
        if not url in chapters:
            chapters[url] = title
        
    logger.info("完成", f"本次获取{len(chapters)}个", update_time_type=UpdateTimeType.STAGE)
    return chapters

def info_from_from_tab(tree,domain,logger):

    if  tree is None:
        return
    spans=tree.xpath('.//span')
    try:
        txt_lst=get_node_text(spans)
        hrefs=list(map(lambda x: fill_url(x,domain), get_node_attr(spans,"href")))
        catelog,title,last_title,author,date,url,last_url=(None,)*7
        
        if len(txt_lst)>4:
            catelog,title,last_title,author,date,*others=txt_lst
        elif len(txt_lst)==4:
            catelog,title,author,date=txt_lst
            
            
        if len(hrefs)>1:
            url,last_url,*other_urls=hrefs
        elif len(hrefs)==1:
            url,*other_urls=hrefs
            
        match = tab_catelog_pattern.match(catelog)
        if match:
            catelog = match.group(1)
            
            
        result={"catelog": catelog, "title": title, "author": author, "date": date, "url": url,"last_url":last_url,"last_title":last_title}
        logger.trace("解析成功",f"\n{result}\n", update_time_type=UpdateTimeType.STEP)
        return result
    except:
        # 使用 tostring 函数将 Element 对象转换为格式化的字符串
        logger.error("解析失败",f"\n{pretty_tree(spans)}\n", update_time_type=UpdateTimeType.STEP)
        return None


def infos_from_tab(tree,domain,logger):
    chapters=[]
    lis_all = tree.xpath('//ul[@class="txt-list txt-list-row5"]')
    if not lis_all:
        lis_all = tree.xpath('//ul[@class="sort_list"]')
        if not lis_all:
            logger.error("解析失败",f"\n{pretty_tree(tree)}\n", update_time_type=UpdateTimeType.STEP)
            return []
            
    lis = lis_all[0].xpath('./li')
    if not lis:
        logger.error("解析失败",f"\n{pretty_tree(lis_all[0])}\n", update_time_type=UpdateTimeType.STEP)
        return []
    for li in lis:
        result=info_from_from_tab(li,domain,logger)
        if not result:
            continue
        chapters.append(result)
    return chapters

# <div class="row sort_page_num">
# 	<a class="prev_off" href="/list/0-1.html">首 页</a>
# 	<a class="page_on" href="/list/0-1.html">&nbsp;1&nbsp;</a>
# 	<a href="/list/0-2.html">&nbsp;2&nbsp;</a>
def get_catelog_page_lst(tree,domain,logger):
    return get_node_sub_hrefs(tree,'//div[@class="row sort_page_num"]','./a',"href",domain,"类别页数",logger)


# <select onchange="self.location.href=options[selectedIndex].value">
# 	<option value="/165/165849/">第1-100章</option>
# 	<option value="/165/165849/1/">第101-200章</option>
# 	<option selected="selected" value="/165/165849/2/">第201-212章</option>
# </select>
def get_chapter_page_lst(tree,domain,logger):
    return get_node_sub_hrefs(tree,'//select[@onchange="self.location.href=options[selectedIndex].value"]','./option',"value",domain,"章节页数",logger)


class StoryScraper:
    def __init__(self, root_dir=r'F:\worm_practice\storys'):
        self.root_dir = Path(root_dir)
        self.dest_dir = self.root_dir / 'dest'
        self.temp_dir = self.root_dir / 'temp'
        self.base_url_xlsx = self.temp_dir / 'story_infos.xlsx'
        self.cookies = cookies
        self.headers = headers
        os.makedirs(self.dest_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_story_infos(self):
        chapters = []
        base_url = 'https://www.nlxs.org/list/'
        domain = get_homepage_url(base_url)
        category_index = 0
        
        try:
            while True:
                logger = logger_helper(f"catelogy:{category_index}")
                page = 1
                chapter_count=len(chapters)
                
                first_url= f"{base_url}{category_index}-1.html"
                logger.update_target(detail= first_url)
                logger.update_time(UpdateTimeType.ALL)
                tree= content_tree(first_url, logger=logger, cookies=self.cookies, headers=self.headers)
                if tree is None:
                    break
                for cur_url in get_catelog_page_lst(tree, domain, logger):
                    logger.update_target(detail= cur_url)
                    logger.update_time(UpdateTimeType.ALL)
                    page += 1
                    if cur_url !=first_url:
                        tree = content_tree(cur_url, logger=logger, cookies=self.cookies, headers=self.headers)
                    if tree is None:
                        continue

                    cur_chapters =infos_from_tab(tree,domain,logger)
                    chapters.extend(cur_chapters)

                    logger.info("成功",f"添加{len(cur_chapters)}个", update_time_type=UpdateTimeType.ALL)
                category_index += 1
                # break
                if chapter_count==len(chapters):
                    break
        except Exception as e:
            logger.error(e)
        return chapters






    def real_title(self, num, title):
        num = int(num)
        return f"{num:05}_{title}" if title else f"{num:04}"

    #从具体的小说(url)中获取所有的标题和url
    #返回值list[dict]
    def get_chapter_lst(self, base_url):
        chapters = {}


        domain = get_homepage_url(base_url)
        logger = logger_helper("", base_url)

        logger.info("开始获取章节列表")
        first_url=f"{base_url}1/"
        logger.update_target(detail=first_url)
        tree = content_tree(first_url, logger=logger, cookies=self.cookies, headers=self.headers)
        if tree is None:
            logger.error("异常", except_stack(), update_time_type=UpdateTimeType.ALL)
            return {},[]
        book_info=info_from_first_catalog(tree, domain, logger)
               
        theme=book_info["title"]
        logger.update_target(target=theme)
        

        
        page_urls=  get_chapter_page_lst(tree, domain, logger) 
        page_urls.insert(0,first_url)
        
            
        for cur_url in unique(page_urls):
            logger.update_target(detail=cur_url)
            if cur_url != first_url:
                tree = content_tree(cur_url, logger=logger, cookies=self.cookies, headers=self.headers)
                if tree is None:
                    logger.error("异常", except_stack(), update_time_type=UpdateTimeType.ALL)
                    continue
            cur_chapter= handle_chapter_lst(tree,domain, logger)
            if not cur_chapter:
                continue
            cur_chapter = {k: v for k, v in cur_chapter.items() if k not in chapters}
            if not cur_chapter:
                continue
            chapters.update(cur_chapter)
            
            
            
        logger.update_target(detail=base_url)
        logger.info("完成", f"共{len(chapters)}个", update_time_type=UpdateTimeType.ALL)
       
       # 提取每个字典中的第一个键值对
        # formatted_chapters = [{"index": index + 1, "url": url, "title": title} 
        #                     for index, d in enumerate(chapters) 
        #                     for url, title in [next(iter(d.items()))]]

        result=[{"index":index+1,"url":url,"title":chapters[url]}   for index,url in  enumerate(chapters)]
        
        return book_info,result

    @exception_decorator()
    async def get_chapters_data(self, semaphore, args: list | tuple):
        async with semaphore:
            title, url, keys = args
            if title in keys:
                return
            logger = logger_helper(url, title)
            base_url = url.rsplit('.', 1)[0]
            content = []
            page = 0
            success_count = 0
            async with aiohttp.ClientSession() as session:
                while True:
                    page_url = f"{base_url}_{page}.html" if page > 0 else url
                    page += 1
                    async with session.get(page_url, cookies=self.cookies, headers=self.headers) as response:
                        if response.status != 200 or str(response.url) != page_url:
                            if page > 1:
                                break
                            else:
                                continue
                        cur_content = await response.read()
                        tree = html.fromstring(cur_content)
                        txt_div = tree.xpath('//div[@class="txt" and @id="txt"]')
                        if not txt_div:
                            txt_div = tree.xpath('//div[@class="word_read"]')
                            if not txt_div:
                                logger.warn(f"{page_url} 内容为空")
                                continue
                        b_tags = txt_div[0].xpath('.//p/text()')
                        content.extend(b_tags)
                        success_count += 1
                if not content:
                    return
                try:
                    logger.trace("保存成功", f"个数:{success_count}", update_time_type=UpdateTimeType.ALL)
                    return (title, '\n'.join(content))
                except Exception as e:
                    print(f"Error occurred while writing to file: {e}")

    def mutithread_chapters_data(self, chapters: list[dict] , datas: list[dict] = None):
        if not chapters:
            return datas
        urls = [item["url"] for item in datas if item] if datas else []
        if not datas:
            datas = []
        first_item=chapters[0]
        first_url=first_item["url"]
        theme = first_item["title"]
            
        playlist_logger = logger_helper(f"{theme}-下载", f"共{len(chapters)}章")
        params = []
        # params = [(key, url, urls) for item in chapters if item and item["url"] not in urls]
        if not params:
            playlist_logger.info("完成", f"已下载{len(datas)}章", update_time_type=UpdateTimeType.ALL)
            return datas
        multi_thread_coroutine = MultiThreadCoroutine(self.get_chapters_data, params, threads_count=10, concurrent_task_count=10, semaphore_count=50)
        try:
            asyncio.run(multi_thread_coroutine.run_tasks())
            success = multi_thread_coroutine.success
            if not success:
                info = [multi_thread_coroutine.fail_infos, except_stack()]
                info_str = "\n".join(info)
                playlist_logger.error("异常", f"\n{info_str}\n", update_time_type=UpdateTimeType.ALL)
            for items in multi_thread_coroutine.result:
                if items:
                    for item in items:
                        if item:
                            title, data = item
                            datas[title] = data
            playlist_logger.info("完成", f"已下载{len(datas)}章", update_time_type=UpdateTimeType.ALL)
        except Exception as e:
            playlist_logger.error("下载异常", f"已下载{len(datas)}章\n{except_stack()}", update_time_type=UpdateTimeType.ALL)
        finally:
            return self.reset_dict_num(dict(sorted(datas.items())))

    def format_filename(self, filename, width=40, fillchar=' '):
        filename = os.path.splitext(os.path.basename(filename))[0]
        formatted_name = filename.center(width, fillchar)
        return formatted_name

    def merge_txt_files(self, source_dir, target_file):
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, 'w', encoding='utf-8-sig') as outfile:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.txt'):
                        file_path = os.path.join(root, file)
                        formatted_name = self.format_filename(file)
                        outfile.write(formatted_name + '\n\n')
                        with open(file_path, 'r', encoding='utf-8-sig') as infile:
                            outfile.write(infile.read())
                        outfile.write("\n\n")

    def export_datas(self, datas: dict, target_file):
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, 'w', encoding='utf-8-sig') as outfile:
            for title, data in sorted(datas.items()):
                outfile.write(title.center(40, " ") + '\n\n')
                outfile.write(data)
                outfile.write("\n\n")

    def reset_dict_num(self, dict_data: dict) -> dict:
        if not dict_data:
            return
        first_key = next(iter(dict_data), None)
        num_len = len(first_key.split("_")[0])
        count = len(dict_data)
        if count < pow(10, num_len) and count >= pow(10, num_len - 1):
            return dict_data
        num_len = math.ceil(math.log10(count))
        logger = logger_helper(f"重置编号,eg:{first_key}", f"{count}->{num_len}")
        dest_datas = {}
        for key, val in dict_data.items():
            titles = key.split("_")
            new_key = key
            if titles:
                num = int(titles[0])
                titles[0] = f"{num:0{num_len}}"
                new_key = "_".join(titles)
            dest_datas[new_key] = val
        logger.info("完成", update_time_type=UpdateTimeType.ALL)
        return dict(sorted(dest_datas.items()))

    def reset_json_order(self, json_path):
        if not os.path.exists(json_path):
            return
        logger = logger_helper("读取已有文件", json_path)
        datas = json.load(open(json_path, 'r', encoding='utf-8-sig'))
        dest_datas = self.reset_dict_num(datas)
        changed = datas.keys() != dest_datas.keys()
        if changed:
            logger.info("重置顺序，并保存", update_time_type=UpdateTimeType.STEP)
            json.dump(dest_datas, open(json_path, 'w', encoding='utf-8-sig'), ensure_ascii=False, indent=4)
        logger.info("读取完成", update_time_type=UpdateTimeType.ALL)
        return dest_datas






    def process_story(self, index, row):
        url = row["url"]
        title = row["title"]
        author = row["author"]
        date = row["date"]
        last = row["last"]



        logger = logger_helper(f"第{index + 1}个_{title}", url)

        file_title = sanitize_filename(title, limit_length=80)
        cur_temp_dir = os.path.join(self.temp_dir, file_title)
        os.makedirs(cur_temp_dir, exist_ok=True)
        logger.info("开始", "获取章节URL", update_time_type=UpdateTimeType.STAGE)

        # 各个章节的地址
        base_url_json = os.path.join(cur_temp_dir, f"{file_title}_url.json")

        if os.path.exists(base_url_json):
            chapters = self.reset_json_order(base_url_json)
        else:
            chapters = self.get_chapter_lst(url)
            if not chapters:
                logger.error("失败", update_time_type=UpdateTimeType.STAGE)
                return

            json.dump(chapters, open(base_url_json, 'w', encoding='utf-8-sig'), ensure_ascii=False, indent=4)

        # 各个章节的内容
        base_data_json = os.path.join(cur_temp_dir, f"{file_title}_data.json")
        datas = {}
        if os.path.exists(base_data_json):
            datas = self.reset_json_order(base_data_json)
        org_len = len(datas)

        logger.info("完成", "获取章节URL", update_time_type=UpdateTimeType.STAGE)
        logger.info("开始", "获取章节内容")

        dest_datas = self.mutithread_chapters_data(chapters, datas)
        if isinstance(dest_datas,ReturnState) and not dest_datas.is_success():
            logger.error("失败",update_time_type=UpdateTimeType.STAGE)
            return
        
        logger.info("完成", "获取章节内容", update_time_type=UpdateTimeType.STAGE)
        changed = len(dest_datas) > org_len or datas.keys() != dest_datas.keys()
        if changed:
            json.dump(dest_datas, open(base_data_json, 'w', encoding='utf-8-sig'), ensure_ascii=False, indent=4)

        # 最终文件
        target_file = os.path.join(self.dest_dir, f"{file_title}.txt")
        if dest_datas and changed:
            self.export_datas(dest_datas, target_file)
        count = len(dest_datas)

        row[ "title"] = title
        row[ "last"] = last if (last and last > count) else count
        row[ "author"] = author
        row[ "date"] = date

        logger.info("完成", update_time_type=UpdateTimeType.ALL)
        return index,row

    def run(self):
        #表格中获取所有小说信息
        def operator_func():
            lst = self.get_story_infos()
            df = pd.DataFrame(lst)
            df["last"] = 0
            df.drop_duplicates(subset='url', inplace=True)
            return df

        infos_df = priority_read_excel_by_pandas(self.base_url_xlsx,operator_func=operator_func)
        # print(infos_df)
        #获取所有的小说详情信息
        for index, row in infos_df.iterrows():
            url=row["url"]
            title=row["title"]
            catelog=row["catelog"]
            author=row["author"]
            date=row["date"]
            last_url=row["last_url"]
            last_title=row["last_title"]
            last=row["last"]
            if not url:
                continue

            book_info,chapters=self.get_chapter_lst(url)
            if book_info:
                dest_info=row.to_dict()
                dest_info.update(book_info)
                infos_df.loc[index] = book_info
            
            
            if index>2:
                break
        write_dataframe_excel(self.base_url_xlsx,infos_df)
        
        

        with ThreadPoolExecutor(1) as executor:
            futures = []
            for index, row in infos_df.iterrows():
                if index<847:
                    continue

                future = executor.submit(self.process_story, index, row)
                futures.append(future)
            # 等待所有任务完成
            for future in futures:
                result=future.result()
                if not result or (not isinstance(result, tuple) or len(result) <2):
                    continue
                index,dest_row=result
                if dest_row and isinstance(dest_row, pd.Series):
                    infos_df.loc[index] = dest_row

        # 重新保存
        infos_df.to_excel(self.base_url_xlsx, index=False)
        
if __name__== "__main__":
    wrapper=StoryScraper(r'F:\worm_practice\storys')
    wrapper.run()
    
    pass