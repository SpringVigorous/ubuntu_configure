from pathlib import Path
import os
import sys
from DrissionPage import WebPage, ChromiumOptions
import time
import re
import concurrent.futures
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import  logger_helper,UpdateTimeType
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base.state import ReturnState

from base import set_attributes,get_attributes,hash_text,tree_by_str,pretty_tree,get_url,arabic_numbers,convert_seconds_to_datetime,remove_none,unique
import pandas as pd
import json 








def video_pure_url(url):
    pattern = r'https://www.douyin.com/video/\d+'
    return bool( re.fullmatch(pattern, url))
def short_url(url)->str:
    cur_path=Path(url)
    return cur_path.stem

def real_counts(counts):
    return map(lambda x: arabic_numbers(x)[0], counts)



class VideoInfo:
    def __init__(self,page:WebPage,root_dir,file_name="景区"):
        self.wp=page
        self.logger=logger_helper()
        self.video_infos=[]
        self.author_infos=[]
        self.dest_infos=[]
        self.root_dir=root_dir
        self.excel_path=os.path.join(root_dir,f"{file_name}.xlsx")
        self.video_name="视频"
        self.author_name="作者"
        self.dest_name="地点"
        self.video_path=os.path.join(root_dir,"video.json")
        self.author_path=os.path.join(root_dir,"author.json")
        self.dest_path=os.path.join(root_dir,"dest.json")
        
    
        self.init()
        # 先访问基础页面
        # self.wp.get('https://www.douyin.com/')  # 抖音主页
    def export(self):
        self.export_json()
        self.export_excel()
        
    def export_json(self):
        def save_json(file_path,data):
            if not data:
                return
            with open(file_path,"w",encoding="utf-8") as f:
                json.dump(data,f,indent=4,ensure_ascii=False)
                
        save_json(self.video_path,self.video_infos)
        save_json(self.author_path,self.author_infos)
        save_json(self.dest_path,self.dest_infos)
        
    def init(self):
        
        def load_json(file_path):
            if not os.path.exists(self.video_path):
                return
            with open(file_path,"r",encoding="utf-8") as f:
                return json.load(f)
        video_info,author_info,dest_info=load_json(self.video_path),load_json(self.author_path),load_json(self.dest_path)
        
        self.video_infos=video_info if video_info else []
        self.author_infos=author_info if author_info else []
        self.dest_infos=dest_info if dest_info else []

    @property
    def author_ids(self):
        return [item["uid"]  for item in self.author_infos]
    
    @property
    def video_urls(self):
        return [item["url"] for item in self.video_infos]
    
    @property
    def video_ids(self):
        return [item["aweme_id"] for item in self.video_infos]
    
    @property
    def dest_ids(self):
        return [item["poi_id"] for item in self.dest_infos]
    
    
    
    def _seek_author_info(self,author_id):
        keys=self.author_ids
        if author_id in keys:
            return self.author_infos[keys.index(author_id)]
        return None
    
    def _seek_video_info(self,url):
        keys=self.video_urls
        if url in keys:
            return self.video_infos[keys.index(url)]
        return None
    
    def _seek_video_info_by_id(self,id):
        keys=self.video_ids
        if id in keys:
            return self.video_infos[keys.index(id)]
        return None
    
    
    def _seek_dest_info(self,dest_id):
        keys=self.dest_ids
        if dest_id in keys:
            return self.dest_infos[keys.index(dest_id)]
        return None
    
    @exception_decorator(error_state=False)
    def _handle_video_packet(self,body):
        if not body:
            self.logger.error("失败","body为空",update_time_type=UpdateTimeType.STAGE)
            return
        detail=body.get("aweme_detail")
        if not detail:
            self.logger.error("失败","aweme_detail为空",update_time_type=UpdateTimeType.STAGE)
            return
        
        anchor_info=detail["anchor_info"]
        anchor_extra_info=anchor_info.get("extra")
        anchor_extra_data=json.loads(anchor_extra_info)  if anchor_extra_info else None
        ext_data=json.loads(anchor_extra_data["ext_json"]) if anchor_extra_data.get("ext_json") else None
        anchor_extra_data["ext_json"]=ext_data
        anchor_info["extra"]=anchor_extra_data
        detail["anchor_info"]=anchor_info
        aweme_id=detail["aweme_id"]
        html_dir=os.path.join(self.root_dir,"html")
        os.makedirs(html_dir,exist_ok=True)
        #json展示
        with open(os.path.join(html_dir,f"{aweme_id}.json"),"w",encoding="utf-8") as f:
            json.dump(detail,f,indent=4,ensure_ascii=False)
        
        author=detail["author"]
        name=author["nickname"]
        short_id=author["short_id"]
        signature=author["signature"]
        unique_id=author["unique_id"]
        uid=author["uid"]
        
        total_favorited=author["total_favorited"]
        
        
        caption=detail["caption"]
        desc=detail["desc"]
        create_time=convert_seconds_to_datetime(detail["create_time"])
        
        
        suggest_words=[item["words"] for item in detail["suggest_words"]["suggest_words"] if item.get("words")] if detail.get("suggest_words") and detail["suggest_words"].get("suggest_words") else []
        suggest=[]
        for items in suggest_words:
            suggest.extend([item["word"] for item in items if item.get("word")])
            
            
        extra_words=[item.get("hashtag_name") for item in detail["text_extra"]]  if detail.get("text_extra") else []

        suggest.extend(remove_none(extra_words))
        video_tag=[item.get("tag_name") for item in detail["video_tag"]] if detail.get("video_tag") else []

        poi_name=anchor_extra_data["poi_name"]
        user_count=anchor_extra_data["user_count"]
        poi_id=anchor_extra_data["poi_id"]

        address_info=anchor_extra_data["address_info"]
        address=[address_info.get(item) for item in ["province","city","district","address","simple_addr"] ]
        
        collected_count=anchor_extra_data["collected_count"]
        item_count=anchor_extra_data["item_count"]
        poi_type=anchor_extra_data["poi_backend_type"]["name"]
        view_count=anchor_extra_data["view_count"]

        domain=f"https://www.douyin.com/user/{author["sec_uid"]}"
        
        statistics=detail["statistics"]
        # statistics= {
        # "admire_count": 0,
        # "aweme_id": "7479303050247654691",
        # "collect_count": 3,
        # "comment_count": 2,
        # "digg_count": 16,
        # "play_count": 0,
        # "share_count": 3
        # }
        admire_count=statistics["admire_count"]
        collect_count=statistics["collect_count"]
        comment_count=statistics["comment_count"]
        digg_count=statistics["digg_count"]
        share_count=statistics["share_count"]
        
        follower_count=author["follower_count"]
        favoriting_count=author["favoriting_count"]
        following_count=author["following_count"]
        age=author["user_age"]
        duration=detail["duration"]/1000.0
        music_info=detail["music"]
        author_image_url=author["avatar_thumb"]["url_list"][0]
        music_title=music_info["title"]
        music_url=music_info["play_url"]["uri"]
        video_info=detail["video"]
        video_image_url=video_info["cover_original_scale"]["url_list"][0]
        video_image_url=video_info["dynamic_cover"]["url_list"][0]
        video_url=video_info["play_addr"]["url_list"][-1]
        popularity=anchor_extra_data["popularity"]
        
        item_ext_info=ext_data["item_ext"]
        life_extra_info=anchor_extra_data["life_extra"]
        life_comment_count=life_extra_info["tag_rate_agg_info"]["total_count"]
        anchor_tag=[item["content"] for item  in item_ext_info["anchor_comment"]["poi_anchor"]["primary_tags"][:-2]]
        dest_url=anchor_extra_data["share_info"]["share_url"]
        group_id=detail["group_id"]
        is_life_item=detail["is_life_item"]
        dest_result={
            "poi_id":poi_id,
            "poi_name":poi_name,
            "popularity":popularity,

            "comment_count":life_comment_count,
            "anchor_tag":" ".join(anchor_tag),
            "address":" ".join(address),
            "poi_type":poi_type,
            "collected_count":collected_count,
            "view_count":view_count,
            "item_count":item_count,
            "user_count":user_count,
            "dest_url":dest_url,
        }

        video_result={
            
            # "short_id":short_id,
            
            "uid":uid,  
            "create_time": create_time,
            "video_url":video_url,
            "music_title":music_title,
            "music_url":music_url,
            "duration":duration,
            "video_image_url":video_image_url,
            
            "admire_count":admire_count,
            "collect_count":collect_count,
            "comment_count":comment_count,
            "digg_count":digg_count,
            "share_count":share_count,
            "group_id":group_id,

            "aweme_id":aweme_id,
            
            "poi_id":poi_id,
            "url":f"https://www.douyin.com/video/{aweme_id}",
            "suggest":" ".join(suggest),
            "video_tag":" ".join(video_tag),
            "caption":caption,
            "desc":desc,
            "is_life_item":is_life_item,
        }
        
        author_result={
            "uid":uid,
            "name":name,
            "age":age,
            
            "short_id":short_id,
            "unique_id":unique_id,  
            "author_image_url":author_image_url,
            "signature":signature,

           
            "total_favorited":total_favorited,   
            "domain":domain,

            "follower_count":follower_count,
            "favoriting_count":favoriting_count,
            "following_count":following_count,

            
        }
        return video_result,author_result,dest_result
    
    def listen_wait(self, listen_args, url, res_type="XHR", retries=3):
        if not isinstance(listen_args,list):
            listen_args=[listen_args]

        try:
            logger=logger_helper("监听消息体", url)
            logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
            self.wp.get(url)
            # self.wp._wait_loaded()  # 等待页面开始加载（或使用其他等待条件）
            times=0
            result=None
            retry_times=15
            
            while times<retry_times:
                self.wp.listen.start(targets=listen_args, res_type=res_type)
                logger.stack_target(f"第{times+1}次",f"监听消息体:{url}")
                if (packet := self.wp.listen.wait(timeout=1.5)):
                    result=packet.response.body
                if result:
                    logger.info("成功",update_time_type=UpdateTimeType.STAGE)
                    return result
                times+=1
                logger.pop_target()
                
            logger.error("失败",f"已重试{retry_times}次",update_time_type=UpdateTimeType.STEP)
            
        except Exception as e:
            logger.error("异常",f"{except_stack()}")
        finally:
            self.wp.listen.stop()
            logger.pop_target()

        logger.error("失败",update_time_type=UpdateTimeType.STAGE)
        return None     

    def _video_info(self,url,index):
        
        logger=logger_helper(f"第{index+1}个",url)
        logger.trace("开始",update_time_type=UpdateTimeType.STEP)
        is_pure_url=video_pure_url(url)
        # listen_args="/aweme/v1/web/aweme/detail/"
        listen_args="/aweme/v1/web/aweme/detail/"

        response_body=None
        
        def url_result(success:bool):
            return success,url
        
        if not is_pure_url:
            response_body = self.listen_wait(listen_args,url)
            url=self.wp.url
        logger.update_target(detail=url)
        
        #查找是否存在
        author_info,dest_info=[None]*2
        video_info=self._seek_video_info(url)

        if video_info:
            author_info=self._seek_author_info(video_info["uid"])
            dest_info=self._seek_dest_info(video_info["poi_id"])
            if author_info and dest_info:
                logger.trace("完成","信息已存在",update_time_type=UpdateTimeType.STAGE)
                return url_result(True)

        if is_pure_url:    
            
            response_body = self.listen_wait(listen_args,url)
            
        if not response_body:
            logger.error("失败","response_body为空",update_time_type=UpdateTimeType.STAGE)
            
            return url_result(False)
        result=self._handle_video_packet(response_body)
        if not result:
            logger.error("失败","结果为空",update_time_type=UpdateTimeType.STAGE)
            return url_result(False)
        video_info,author_info,dest_info=result
 
        #缓存
        if video_info:
            self.video_infos.append(video_info)
        if author_info:
            self.author_infos.append(author_info)
        if dest_info:
            self.dest_infos.append(dest_info)
        logger.trace("完成",update_time_type=UpdateTimeType.STAGE)

        return url_result(True)
    
    #返回是否爬取完成
    def crawl_video_infos(self,urls):
        if not urls:
            return False
        times=0
        total_count=len(urls)
        logger=logger_helper(f"获取视频信息:{total_count}个",f"\n{'\n'.join(urls)}")
        dest_urls=[]
        logger.info("开始")
        invalid_urls=None
        while(times<3):
            try:
                times+=1
                cur_count=len(urls)
                logger.stack_target(f"第{times}次获取视频信息",f"本次{cur_count}个")
                logger.trace("开始",update_time_type=UpdateTimeType.STEP)
                result=[self._video_info(url,index) for index,url in enumerate(urls) if url]
                if not dest_urls:
                    dest_urls=[ item[1] for item in result if  item]
                
                
                invalid_urls=[ item[1] for item in result if not item[0]]
                if not invalid_urls:
                    logger.info("成功",f"共{cur_count}个",update_time_type=UpdateTimeType.STEP)
                    break
                invalid_count=len(invalid_urls)
                logger.info("完成",f"成功{cur_count-invalid_count}个,失败{invalid_count}个，重试一次",update_time_type=UpdateTimeType.STEP)
                urls=invalid_urls               
            except Exception as e:
                logger.error("异常",f"{except_stack()}\n重试一次",update_time_type=UpdateTimeType.STEP)
            finally:
                logger.pop_target()
        if dest_urls:
            logger.update_target(detail=f"\n{'\n'.join(dest_urls)}")
        success=not invalid_urls
        log= logger.info if success else logger.error
        log_content=f"\n以下链接失败：\n{'\n'.join(invalid_urls)}\n" if not success else None
        log_type="成功" if success else "失败"
        log(log_type,log_content,update_time_type=UpdateTimeType.STAGE)

            
        return success
        

    
    def export_excel(self):
        
        with pd.ExcelWriter(self.excel_path,mode="w") as w:
            video_df=pd.DataFrame(self.video_infos)
            video_df.drop_duplicates(subset=["aweme_id"],keep="last",inplace=True)
            video_df.to_excel(w, sheet_name=self.video_name, index=False)
            
            author_df=pd.DataFrame(self.author_infos)
            author_df.drop_duplicates(subset=["uid"],keep="last",inplace=True)
            author_df.to_excel(w, sheet_name=self.author_name, index=False)
            
            dest_df=pd.DataFrame(self.dest_infos)
            dest_df.drop_duplicates(subset=["poi_id"],keep="last",inplace=True)
            dest_df.to_excel(w, sheet_name=self.dest_name, index=False)
        

    
    @property
    def title(self)->str:
        return self.wp.title
    


    
if __name__=="__main__":
    
    
    
    urls=get_url("""劲竹韧石:

清风细雨:
8.46 j@p.QX 12/10 TLW:/ 顾村公园樱花节 第十五届上海樱花节将于2025年3月15日至4月15日在顾村公园举行，公园首次推出夜赏樱花活动，时间为18：00-21：30，樱花岛有5大赏樱区、5大打卡点、3大活动区。# 樱花 # 一起去春游 # 樱花节 # 顾村公园  https://v.douyin.com/-4Vm0zOGZDs/ 复制此链接，打开Dou音搜索，直接观看视频！

清风细雨:
4.15 12/08 o@Q.kC AgB:/ 顾村公园# 旅行推荐官 # 上海旅游攻略 # 上海游玩推荐 # 上海游玩景点推荐 # 赏花春游好去处  https://v.douyin.com/E7TFTNEljUI/ 复制此链接，打开Dou音搜索，直接观看视频！

清风细雨:
樱花和我都想见你，樱花季赏花攻略来了，快来上海顾村公园赏樱花吧。#顾村公园赏樱护照 #赏樱护照薅羊毛 #满城尽是樱花粉 #春日遛娃好去处 #腔调上海 https://v.douyin.com/7aFqcXQOm8c/ 复制此链接，打开【抖音短视频】，直接观看视频！

清风细雨:
8.97 sEh:/ 09/04 y@g.BT # 带你看樱花 顾村公园的樱花，不另外收费。  https://v.douyin.com/L7HVDFLDk30/ 复制此链接，打开Dou音搜索，直接观看视频！

清风细雨:
7.66 D@h.oq 03/26 ATY:/ 顾村公园樱花节反转封神！免费樱花岛+顾村夜场光影秀血赚！ 2025年顾村公园樱花节被全网骂的票中票争议大反转！现在樱花岛白天随便进！亲测不收费！顾村公园这波立正挨打+火速整改，格局拉满！ 早樱：已进入"樱吹雪"倒计时（翻译：秃头预警⚠️速来捡漏） 中樱：下周染井吉野大爆发！三公里粉白隧道即将霸屏！ 晚樱+双花海：4月王者登场！蝶之恋/醉美人叠buff，郁金香油画田+油菜花小清新，三花同框美到窒息！ 8:00准时开挂！16万㎡樱花岛变身魔幻宇宙—— ✓ 激光麋鹿踏雾来 ✓ 3D蝶恋樱全息暴击 # 顾村公园 # 顾村公园樱花 # 上海樱花 # 上海樱花节 # 顾村公园樱花节  https://v.douyin.com/CIq0dtSiahM/ 复制此链接，打开Dou音搜索，直接观看视频！

清风细雨:
樱花和我都想见你，樱花季赏花攻略来了，快来上海顾村公园赏樱花吧。#顾村公园赏樱护照 #赏樱护照薅羊毛 #满城尽是樱花粉 #春日遛娃好去处 #腔调上海 https://v.douyin.com/I_LPplokQwc/ 复制此链接，打开【抖音短视频】，直接观看视频！

清风细雨:
8.41 pqR:/ b@a.Nw 08/10 顾村公园# 旅行推荐官 # 上海旅游攻略 # 上海游玩推荐 # 上海游玩景点推荐 # 赏花春游好去处  https://v.douyin.com/OaCAuNR1kCg/ 复制此链接，打开Dou音搜索，直接观看视频！

清风细雨:
8.79 q@r.rr 01/01 Gic:/ 3月25日顾村公园樱花岛 开放进度约70%%，大部分树上还有绿芽没有完全开。# 顾村公园樱花 # 顾村公园樱花岛 # 春天  https://v.douyin.com/SSIiT_8yaww/ 复制此链接，打开Dou音搜索，直接观看视频！


""")
    
    urls=unique(urls)


    
    
    
    
    
    
    
    

    #使用本地浏览器用户数据


    # 创建 Chromium 配置对象
    co = ChromiumOptions()

    # 添加禁用缓存的启动参数
    # co.set_no_loading_images(False)  # 可选：允许加载图片
    co.set_argument('--disk-cache-size=0')       # 禁用磁盘缓存
    co.set_argument('--disable-application-cache')  # 禁用应用缓存

    # co.remove_argument('--enable-automation')

    # #窗口最大化
    # co.set_argument("--start-maximized")
    # #无界面运行(无窗口)，也叫无头浏览器
    # co.set_argument("--headless")
    # #禁用GPU，防止无头模式出现莫名的bug
    # co.set_argument("--disable-gpu")
    # #禁用启用Blink运行时
    # co.set_argument('--disable-blink-features=Automationcontrolled')
    
    # 初始化 WebPage 并应用配置
    wp = WebPage(chromium_options=co)
    root_dir=r"F:\worm_practice\douyin\videos"
    info_obj=VideoInfo(wp,root_dir,"景区")
    info_obj.crawl_video_infos(urls)
    info_obj.export()
    

    pass