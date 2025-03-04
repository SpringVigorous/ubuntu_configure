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

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import (
    get_homepage_url, is_http_or_https, logger_helper, fetch_sync, UpdateTimeType,
    arabic_number_tuples, sanitize_filename, chinese_num, exception_decorator,
    except_stack, hash_text, MultiThreadCoroutine,ReturnState
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

class StoryScraper:
    def __init__(self, root_dir=r'F:\worm_practice\storys'):
        self.root_dir = Path(root_dir)
        self.dest_dir = self.root_dir / 'dest'
        self.temp_dir = self.root_dir / 'temp'
        self.base_url_xlsx = self.temp_dir / 'urls.xlsx'
        self.cookies = cookies
        self.headers = headers
        os.makedirs(self.dest_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_story_lst(self):
        chapters = []
        base_url = 'https://www.nlxs.org/list/'
        domain = get_homepage_url(base_url)
        chapter_pattern = re.compile(r'\[(.*)\]')
        category_index = 1
        logger = logger_helper(f"catelogy:{category_index}")
        try:
            while True:
                page = 1
                valid_count = len(chapters)
                while True:
                    cur_url = f"{base_url}{category_index}-{page}.html"
                    logger.update_target(cur_url)
                    logger.update_time(UpdateTimeType.ALL)
                    page += 1
                    response = requests.get(cur_url, cookies=self.cookies, headers=self.headers)
                    if response.status_code != 200:
                        logger.warn("失败")
                        break
                    tree = html.fromstring(response.content)
                    lis_all = tree.xpath('//ul[@class="txt-list txt-list-row5"]')
                    if not lis_all:
                        lis_all = tree.xpath('//ul[@class="sort_list"]')
                        if not lis_all:
                            break
                    lis = lis_all[0].xpath('./li')
                    if not lis:
                        break
                    for li in lis:
                        catelog = li.xpath('.//span[@class="s1"]')[0].xpath('text()')[0].strip()
                        info = li.xpath('.//span[@class="s2"]/a')[0]
                        url = info.xpath('@href')[0]
                        title = info.xpath('text()')[0].strip()
                        author = li.xpath('.//span[@class="s4"]')[0].xpath('text()')[0].strip()
                        date = li.xpath('.//span[@class="s5"]')[0].xpath('text()')[0].strip()
                        if not is_http_or_https(url):
                            url = domain + url
                        match = chapter_pattern.match(catelog)
                        if match:
                            catelog = match.group(1)
                        chapters.append({"catelog": catelog, "title": title, "author": author, "date": date, "url": url})
                    logger.info("成功", update_time_type=UpdateTimeType.ALL)
                category_index += 1
                if valid_count == len(chapters):
                    break
        except Exception as e:
            logger.error(e)
        return chapters

    def extract_after_colon(self, text):
        match = re.search(r'：\s*(.*)', text)
        return match.group(1).strip() if match else None

    def title_form_detail(self, url):
        response = requests.get(url, cookies=self.cookies, headers=self.headers)
        if response.status_code != 200:
            return
        tree = html.fromstring(response.content)
        title = tree.xpath('//div[@class="bookname"]/text()')
        if title:
            return title[0]
        titles = tree.xpath('//h2[@class="layout-tit xs-hidden"]/a/text()')
        return titles[1] if titles and len(titles) > 1 else ""

    def info_from_lst(self, url):
        response = requests.get(url, cookies=self.cookies, headers=self.headers)
        if response.status_code != 200:
            return
        tree = html.fromstring(response.content)
        infos = tree.xpath('//div[@class="info"]')
        if not infos:
            infos = tree.xpath('//div[@class="book-info"]')
            if not infos:
                return
        org_info = infos[0]
        title = org_info.xpath('.//h1/text()')[0]
        info = org_info.xpath('.//p')
        info_txt = org_info.xpath('.//p/text()')
        if len(info_txt) < 3:
            return title, None
        author = self.extract_after_colon(info_txt[0])
        catelog = self.extract_after_colon(info_txt[1])
        date = self.extract_after_colon(info_txt[-2])
        last = arabic_number_tuples(info[-1].xpath('./a')[-1].xpath('text()')[0])[0][1]
        return title, author, catelog, date, last

    def real_title(self, num, title):
        num = int(num)
        return f"{num:05}_{title}" if title else f"{num:04}"

    def get_chapter_list(self, base_url):
        chapters = {}
        page = 0
        domain = get_homepage_url(base_url)
        book_info = self.info_from_lst(base_url)
        theme = book_info[0] if book_info else ""
        logger = logger_helper(theme, base_url)
        logger.info("开始获取章节列表")
        chapter_pattern = re.compile(r'\S([0-9' + chinese_num + r']+)\S\s*(\S*)')
        indexes = {}
        while True:
            cur_url = f"{base_url}{page}/" if page > 0 else base_url
            page += 1
            response = None
            try:
                response = requests.get(cur_url, cookies=self.cookies, headers=self.headers, timeout=10)
            except:
                logger.error("异常", except_stack(), update_time_type=UpdateTimeType.ALL)
                return
            if response.status_code != 200:
                break
            logger.update_target(detail=cur_url)
            tree = html.fromstring(response.content)
            lis_all = tree.xpath('//ul[@class="chapter-list"]')
            if not lis_all:
                lis_all = tree.xpath('//ul[@class="fix section-list"]')
                if not lis_all:
                    break
            lis = lis_all[-1].xpath('./li')
            if not lis:
                break
            valid_count = len(chapters)
            for li in lis:
                a_tag = li.xpath('.//a')[0]
                url = a_tag.xpath('@href')[0]
                if not is_http_or_https(url):
                    url = domain + url
                if not url:
                    continue
                titles = a_tag.xpath('text()')
                title = titles[0].strip() if titles else hash_text(url, strict_no_num=True)
                org_title = title
                match = chapter_pattern.match(title)
                if match:
                    chapter_number = arabic_number_tuples(match.group(1))[0][-1]
                    chapter_title = match.group(2)
                    logger_fun = logger.trace if chapter_title else logger.warn
                    title = self.real_title(chapter_number, chapter_title)
                    logger_fun(f"匹配标题:{org_title}->{title}", update_time_type=UpdateTimeType.STEP)
                else:
                    logger.warn(f"未匹配标题: {org_title}", update_time_type=UpdateTimeType.STEP)
                if chapters.get(url):
                    continue
                chapters[url] = title
                indexes[len(chapters) - 1] = bool(match)
            add_count = len(chapters) - valid_count
            logger.info("完成", f"本次添加{add_count}个", update_time_type=UpdateTimeType.STAGE)
            if add_count < 1:
                break
        logger.update_target(detail=base_url)
        logger.info("完成", f"共{len(chapters)}个", update_time_type=UpdateTimeType.ALL)
        if not all(indexes.values()):
            keys = list(chapters.keys())
            chapters = {key: (val if indexes[keys.index(key)] else self.real_title(keys.index(key) + 1, val)) for key, val in chapters.items()}
        chapters = {val: key for key, val in chapters.items()}
        return self.reset_dict_num(chapters)

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

    def mutithread_chapters_data(self, chapters, datas: dict = None):
        keys = datas.keys() if datas else []
        if not datas:
            datas = {}
        first_url = next(iter(chapters), None) if chapters else None
        theme = self.title_form_detail(first_url) if first_url else ""
        playlist_logger = logger_helper(f"{theme}-下载", f"共{len(chapters)}章")
        params = [(key, url, keys) for key, url in chapters.items() if key not in keys]
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

        info = self.info_from_lst(url)
        if info and len(info) > 2:
            detail_title, detail_author, detail_catelog, detail_date, detail_last = info
            title = detail_title if detail_title else title
            author = detail_author if detail_author else author
            date = detail_date if detail_date else date
            last = detail_last if detail_last else last

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
            chapters = self.get_chapter_list(url)
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
        if not os.path.exists(self.base_url_xlsx):
            lst = self.get_story_lst()
            df = pd.DataFrame(lst)
            df["last"] = 0
            df.drop_duplicates(subset='url', inplace=True)
            df.to_excel(self.base_url_xlsx, index=False)
        else:
            df = pd.read_excel(self.base_url_xlsx)

        with ThreadPoolExecutor() as executor:
            futures = []
            for index, row in df.iterrows():
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
                    df.loc[index] = dest_row

        # 重新保存
        df.to_excel(self.base_url_xlsx, index=False)
        
if __name__== "__main__":
    wrapper=StoryScraper(r'F:\worm_practice\storys')
    wrapper.run()
    
    pass