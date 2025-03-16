from pathlib import Path
import os
import sys
from DrissionPage import WebPage
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

from base import set_attributes,get_attributes,hash_text,tree_by_str,pretty_tree,get_url,arabic_numbers,convert_seconds_to_datetime,remove_none,ResultThread
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
        self.autho_name="作者"
        self.dest_name="地点"
        if os.path.exists(self.excel_path):
            self.video_infos=pd.read_excel(self.excel_path,sheet_name=self.video_name).to_dict("records")
            self.author_infos=pd.read_excel(self.excel_path,sheet_name=self.autho_name).to_dict("records")
            self.dest_infos=pd.read_excel(self.excel_path,sheet_name=self.dest_name).to_dict("records")
        # 先访问基础页面
        # self.wp.get('https://www.douyin.com/')  # 抖音主页
    
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
        anchor_extra_data=json.loads(anchor_info["extra"]) 
        ext_data=json.loads(anchor_extra_data["ext_json"])
        anchor_extra_data["ext_json"]=ext_data
        anchor_info["extra"]=anchor_extra_data
        detail["anchor_info"]=anchor_info
        aweme_id=detail["aweme_id"]
        #json展示
        with open(os.path.join(root_dir,"html",f"{aweme_id}.json"),"w",encoding="utf-8") as f:
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

        self.wp.listen.start(targets=listen_args, res_type=res_type)
        
        def get_body():

            logger=logger_helper("监听消息体", "listen_wait")
            
            self.logger.info("开始",update_time_type=UpdateTimeType.STEP)

            times=0

            while times<retries:
                logger.stack_target("监听", f"第{times}次")
                
                if (packet := self.wp.listen.wait(timeout=30)):
                    self.logger.info("结束",update_time_type=UpdateTimeType.STEP)
                    result=packet.response.body
                    if result:
                        return result
                times+=1
                logger.warn("失败",update_time_type=UpdateTimeType.STEP)
                logger.pop_target()
                
            logger.error("异常",update_time_type=UpdateTimeType.STEP)


        
        thread= ResultThread(target=get_body)
        thread.start()
        time.sleep(2)
        try:
            logger=logger_helper("WebPage", "get")

            logger.info("开始",update_time_type=UpdateTimeType.STEP)
            self.wp.get(url)
            logger.info("结束",update_time_type=UpdateTimeType.STEP)
            logger.update_target("thread","join")
            logger.info("开始",update_time_type=UpdateTimeType.STEP)
            result=thread.join(5)
            logger.info("结束",update_time_type=UpdateTimeType.STEP)
            if result:
                return result
            logger.warn(f"请求{url}:未捕获数据包")
        except Exception as e:
            self.logger.error(f"请求{url}:请求异常: {except_stack()}")


        self.logger.error(f"请求失败: {url}")
        return None     
    def listen_wait_js(self, listen_args, url, res_type="XHR", retries=3):
        if not isinstance(listen_args,list):
            listen_args=[listen_args]

        
        
        # 创建唯一按钮ID防止重复
        btn_id = f"dynamic_btn_{hash_text(url)}"
        
        # 构建点击脚本
        js_script = f"""
        // 创建按钮元素
        let btn = document.createElement('button');
        btn.id = '{btn_id}';
        btn.style.position = 'fixed';
        btn.style.zIndex = '9999';
        btn.style.top = '20px';
        btn.style.right = '20px';
        btn.style.padding = '10px';
        btn.textContent = '加载内容';
        
        // 添加点击事件
        btn.onclick = function() {{
            window.location.href = '{url}';
            this.remove();  // 点击后移除按钮
        }};
        
        // 插入到页面
        document.body.appendChild(btn);
        """
        # 点击按钮并等待跳转
        click_script = f"""
        document.getElementById('{btn_id}').click();
        """
        self.wp.listen.start(targets=listen_args, res_type=res_type)
        for attempt in range(retries):
            try:
                self.wp.run_js(js_script)
                self.wp.run_js(click_script)
                if (packet := self.wp.listen.wait()):
                    self.logger.trace("捕获到数据包",str(packet.response))
                    return packet.response.body
                
                self.logger.warn(f"第{attempt+1}次请求未捕获数据包")
            except Exception as e:
                # self.wp.refresh()
                self.logger.error(f"第{attempt+1}次请求失败: {except_stack()}")
            finally:
                # self.wp.listen.stop()
                time.sleep(2)  # 重试间隔

        self.logger.error(f"请求失败: {url}")
        return None

    def _video_info(self,url,index):
        
        self.logger.update_target(f"第{index+1}个",url)
        self.logger.trace("开始")
        
        is_pure_url=video_pure_url(url)
        
        # listen_args="/aweme/v1/web/aweme/detail/"
        listen_args="/v1/web/aweme/detail"

        response_body=None
                
        if not is_pure_url:
            response_body = self.listen_wait(listen_args,url)
            url=self.wp.url
        self.logger.update_target(detail=url)
        
        #查找是否存在
        author_info,dest_info=[None]*2
        video_info=self._seek_video_info(url)

        if video_info:
            author_info=self._seek_author_info(video_info["uid"])
            dest_info=self._seek_dest_info(video_info["poi_id"])
            if author_info and dest_info:
                self.logger.trace("完成","信息已存在",update_time_type=UpdateTimeType.STAGE)
                return video_info,author_info,dest_info
            

        
                
        if is_pure_url:    
            
            response_body = self.listen_wait(listen_args,url)
            
        if not response_body:
            self.logger.error("失败","response_body为空",update_time_type=UpdateTimeType.STAGE)
            
            return 
        result=self._handle_video_packet(response_body)
        if not result:
            self.logger.error("失败","结果为空",update_time_type=UpdateTimeType.STAGE)
            return
        video_info,author_info,dest_info=result
 
        #缓存
        if video_info:
            self.video_infos.append(video_info)
        if author_info:
            self.author_infos.append(author_info)
        if dest_info:
            self.dest_infos.append(dest_info)
        self.logger.trace("完成",update_time_type=UpdateTimeType.STAGE)
        # time.sleep(2)
        return video_info,author_info,dest_info
    def get_video_infos(self,urls):
        results=[self._video_info(url,index) for index,url in enumerate(urls) ]
        return results
    
    def export(self):
        
        with pd.ExcelWriter(self.excel_path,mode="w") as w:
            video_df=pd.DataFrame(self.video_infos)
            video_df.drop_duplicates(subset=["aweme_id"],keep="last",inplace=True)
            video_df.to_excel(w, sheet_name=self.video_name, index=False)
            
            author_df=pd.DataFrame(self.author_infos)
            author_df.drop_duplicates(subset=["uid"],keep="last",inplace=True)
            author_df.to_excel(w, sheet_name=self.autho_name, index=False)
            
            dest_df=pd.DataFrame(self.dest_infos)
            dest_df.drop_duplicates(subset=["poi_id"],keep="last",inplace=True)
            dest_df.to_excel(w, sheet_name=self.dest_name, index=False)
        

    
    @property
    def title(self)->str:
        return self.wp.title
    


    
if __name__=="__main__":
    
    
    
    urls=get_url("""劲竹韧石:
4.64 去抖音看看【橙子探江南的作品】我本无意入江南，奈何江南入我心！春暖花开，来无锡蠡... https://v.douyin.com/FFd9CStSuzs/ 12/08 i@C.HI mQ:/ 

劲竹韧石:
6.43 去抖音看看【娑影阑珊的作品】3月2日实拍花星球龙梅已经盛开啦！人间仙境，龙梅圣... https://v.douyin.com/5fhn-ttv6W0/ WM:/ 04/29 u@S.yt 

劲竹韧石:
4.66 去抖音看看【温岭风云旅游的作品】这么美的温州樱花园，你心动了吗？绝美赏樱胜地等你来... https://v.douyin.com/HtwS29iavOA/ yg:/ W@m.qE 04/13 

劲竹韧石:
0.05 去抖音看看【家美丽的作品】鼋头渚早樱已入盛花期# 鼋头渚樱花 # 一年一度赏... https://v.douyin.com/i5GNf9LP/ q@e.Bg Sy:/ 08/08 

劲竹韧石:
8.23 去抖音看看【晓文旅拍的作品】天台国清寺，风景秀丽空气清新，你来过了吗？古建筑之... https://v.douyin.com/nUs2XFpbbjs/ 02/13 aa:/ y@g.Ok 

劲竹韧石:
8.23 去抖音看看【做棵🌻向日葵的作品】湖州森赫樱花园的樱花，有了春天的味道，三月带上心爱... https://v.douyin.com/i5GNw1hp/ 02/27 G@i.ca OK:/ 

劲竹韧石:
4.61 去抖音看看【九华山旅拍摄影师东南山人的作品】# 治愈文案 人生最好的境界是丰富的安静让我们在静... https://v.douyin.com/i5GNojgy/ CH:/ R@K.Ji 06/27 

劲竹韧石:
5.84 去抖音看看【南京九州的作品】春天的气息扑面而来，邂逅南京牛首山，见证佛顶宫的恢... https://v.douyin.com/i5GFetRy/ GV:/ 05/17 q@E.HV 

劲竹韧石:
7.43 去抖音看看【处处皆风景@美景悠然生的作品】苏州虎丘山｜一键穿越千年，古风天花板原地封神！ 🌸... https://v.douyin.com/i5GFe5np/ G@V.yG 04/21 nQ:/ 
""")
    

    wp=WebPage()
    root_dir=r"F:\worm_practice\douyin\videos"
    info_obj=VideoInfo(wp,root_dir,"景区")
    result=info_obj.get_video_infos(urls)
    invalid_urls=[]
    for index,item in enumerate(result):
        if not item:
            invalid_urls.append(urls[index])
    
    info_obj.export()
    
    print("\n".join(invalid_urls))
    pass