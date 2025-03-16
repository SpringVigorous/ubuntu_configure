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

from base import set_attributes,get_attributes,hash_text,tree_by_str,pretty_tree,get_url,arabic_numbers
import pandas as pd

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
        self.root_dir=root_dir
        self.excel_path=os.path.join(root_dir,f"{file_name}.xlsx")
        self.video_name="视频"
        self.autho_name="作者"
        if os.path.exists(self.excel_path):
            self.video_infos=pd.read_excel(self.excel_path,sheet_name=self.video_name).to_dict("records")
            self.author_infos=pd.read_excel(self.excel_path,sheet_name=self.autho_name).to_dict("records")
        
        
        
    def _author_info(self,domain_url):
        self.wp.get(domain_url,timeout=5)
        self.logger.update_target(domain_url,self.title)
        self.logger.trace("开始")
        auto_ele=self.wp.ele("xpath://div[@class=\"a3i9GVfe nZryJ1oM _6lTeZcQP y5Tqsaqg\"]")
        url_ele=auto_ele.ele("xpath://img[@class=\"fiWP27dC\"]")
        autho_name=url_ele.attr("alt")
# <span class="arnSiSbK">
# 	<span>
# 		<span>
# 			<span>
# 				<span>娑影阑珊</span>
# 			</span>
# 		</span>
# 	</span>
# </span>
        name=auto_ele.eles("xpath://span[@class=\"arnSiSbK\"]//span/text()")[0]

        image_url=url_ele.attr("src")
        guanzhu=auto_ele.eles("xpath://div[@class=\"C1cxu0Vq\"]/text()")
        counts=dict(zip(["关注","粉丝","点赞",],real_counts(guanzhu) ))
        
        
# <p class="eTvkFY8I">
# 	<span class="OcCvtZ2a">抖音号：dkkj5188</span>
# 	<span class="DtUnx4ER">IP属地：江苏</span>
# 	<span class="YcpSmZeQ">
# 		<svg width="12" height="12" fill="none"
# 			xmlns="http://www.w3.org/2000/svg" class="" viewBox="0 0 12 12" style="margin-right:4px">
# 			<mask id="woman_svg__a" maskUnits="userSpaceOnUse" x="-2" y="-2" width="16" height="16" style="mask-type:alpha">
# 				<path fill="#C4C4C4" d="M-2-2h16v16H-2z"></path>
# 			</mask>
# 			<g mask="url(#woman_svg__a)" stroke="#F5588E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
# 				<circle cx="7.2" cy="4.896" r="3.25"></circle>
# 				<path d="M1.617 10.511l3.115-3.115M1.904 7.396l2.828 2.829"></path>
# 			</g>
# 		</svg>
# 		<span>女</span>
# 	</span>
# 	<span class="YcpSmZeQ">江苏·无锡</span>
# </p>
        
        detail_ele=self.wp.ele("xpath://p[@class=\"eTvkFY8I\"]")
        # detail=detail_ele.eles("xpath://span/text()")
        
        id=detail_ele.ele("xpath:/span[@class=\"OcCvtZ2a\"]/text()")
        ip=detail_ele.ele("xpath:/span[@class=\"DtUnx4ER\"]/text()")
        sex=""
        pos=""
        sex_pos=detail_ele.eles("xpath:/span[@class=\"YcpSmZeQ\"]")
        vals=[[item.ele("xpath:/span/text()"),item.ele("xpath:/text()")] for item in sex_pos]
        for val in vals:
            sex_temp,pos_temp=val
            if sex_temp:
                sex=sex_temp
            if pos_temp:
                pos=pos_temp
        
        # <span class="MNSB3oPV" data-e2e="user-tab-count">1184</span>
        count=self.wp.ele("xpath://span[@class=\"MNSB3oPV\"]/text()")
        
        

        result={"author_name":autho_name,"image_url":image_url,"domain_url":domain_url,"title":self.title,"id":id,"ip":ip,"sex":sex,"pos":pos,"count":count}
        result.update(counts)
        self.author_infos.append(result)
        
        return result
    
    @property
    def domain_urls(self):
        return [item["domain_url"]  for item in self.author_infos]
    
    def video_urls(self):
        return [item["url"] for item in self.video_infos]
    
    
    def _seek_author_info(self,domain_url):
        keys=self.domain_urls
        if domain_url in keys:
            return self.author_infos[keys.index(domain_url)]
        return None
    
    def _seek_video_info(self,url):
        keys=self.video_urls()
        if url in keys:
            return self.video_infos[keys.index(url)]
        return None
        
    
    def _video_info(self,url):
        is_pure_url=video_pure_url(url)
        if not is_pure_url:
            self.wp.get(url)
            url=self.wp.url
            
        def update_author_info(result:dict):
            if not result:
                return
            domain_url=result["domain_url"]
            if not domain_url:
                return
            author_info=self._seek_author_info(domain_url)
            if not author_info:
                self._author_info(domain_url)
        
        if self._seek_video_info(url):
            result=self._seek_video_info(url)
            if result:
                update_author_info(result)
                return result
        
                
        if is_pure_url:    
            self.wp.get(url)
        self.logger.update_target(url,self.title)
        self.logger.trace("开始")
       
        url=self.wp.url
        id=short_url(url)
        html_path=os.path.join(root_dir,"html",f"{id}.html")
        tree=tree_by_str(self.wp.html)
        with open(html_path,"w",encoding="utf-8") as f:
            f.write(pretty_tree(tree))
        
        count_eles=self.wp.eles("xpath://div[@class=\"fN2jqmuV\"]/div")
        
        counts=[]
        
        #点赞 评论 收藏 转发
        if count_eles:
            counts=[ele.text for ele in count_eles]
        
        count_dict=dict(zip(["点赞","评论","收藏","转发"],real_counts(counts))) 
        author_ele=self.wp.ele("xpath://div[@class=\"cHwSTMd3\"]")
        url_ele=author_ele.ele("xpath://div[@class=\"X1j3RKm7\"]//a")
        domain_url=url_ele.attr("href") if url_ele else ""
        image_ele=url_ele.ele("xpath://img[@class=\"fiWP27dC\"]") if url_ele else ""
        image_url=image_ele.attr("src") if image_ele else ""
        author_name=image_ele.attr("alt") if image_ele else ""

        all_counts=author_ele.eles("xpath://span[@class=\"EBi41nRR\"]/text()")
        
        
        all_counts_dict=dict(zip(["粉丝","总点赞",], real_counts(all_counts) )) 
        result={"domain_url":domain_url,"image_url":image_url,"author_name":author_name,"url":url,"title":self.title,"id":id}
        result.update(count_dict)
        result.update(all_counts_dict)
        
        #更新作者信息
        update_author_info(result)
        #缓存
        self.video_infos.append(result)
        
        return result
    def get_video_infos(self,urls):
        results=[self._video_info(url) for url in urls]
        return results
    
    def export(self):
        
        
        with pd.ExcelWriter(self.excel_path,mode="w") as w:
            video_df=pd.DataFrame(self.video_infos)
            video_df.to_excel(w, sheet_name=self.video_name, index=False)
            
            author_df=pd.DataFrame(self.author_infos)
            author_df.to_excel(w, sheet_name=self.autho_name, index=False)
            
            
        

    
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
    
    # print(short_url(urls[0]))
    # exit(0)
    wp=WebPage()
    root_dir=r"F:\worm_practice\douyin\videos"
    info_obj=VideoInfo(wp,root_dir,"景区")
    result=info_obj.get_video_infos(urls)
    info_obj.export()
    pass