import os.path
from pathlib import Path
import os
import sys
from DrissionPage import WebPage
import time
import re
import concurrent.futures





from base import  logger_helper,UpdateTimeType,flat_df
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base.state import ReturnState

from base import set_attributes,get_attributes,hash_text,tree_by_str,pretty_tree,get_url,arabic_numbers,convert_seconds_to_datetime,remove_none,ResultThread
import pandas as pd
import json 
from base import bit_fuzzy_search,unique
from base.xml_tools import *
import math
import bisect
class RangeItem:
    def __init__(self,min_con=0,max_con=0,val=None) -> None:
        self.set(min_con,max_con,val)

    
    def set(self,min_con,max_con,val):
        self.min_con,self.max_con,self.val=min_con,max_con,val

        
        
#左闭右开

class RangeItems:
    def __init__(self) -> None:
        self.range_items=[]
        pass
    @staticmethod
    def from_lst_dict(lst_dict):
        result=RangeItems()
        for item in lst_dict:
            inner_result= RangeItems()
            for inner in item["prices_info"]:
                inner_result.add(inner["min_weight"],inner["max_weight"],inner["price"])
    
            result.add(item["min_count"],item["max_count"],inner_result.sorted())
        return result.sorted()
        
    @property
    def is_empty(self):
        return  not self.range_items
    
    @property
    def is_one(self):
        return self.is_empty and len(self.range_items)==1
    
        
    def add(self,min_con,max_con,val):
        self.range_items.append(RangeItem(min_con,max_con,val))

    #左闭右开
    @property
    def keys(self):
        return [item.min_con for item in self.range_items]
        
    def sorted(self):
        self.range_items=sorted(self.range_items,key=lambda x: x.min_con)
        return self
    
    def index(self,count):
        keys=self.keys
        if count in keys:
            return keys.index(count)
        
        pos=bisect.bisect_left(self.keys, count)
        
        #处理边界： 比最小值还小的情况，返回第一个
        return pos if pos==0 else pos-1

    
    def is_last(self,item):
        return item==self.range_items[-1]
    #获取值
    def cal(self,count):
        result=self.item(count)
        if isinstance(result.val,RangeItems):
            return result.val
        
        if self.is_one or (not self.is_one and not self.is_last(result)):
            return result.val
        
        last_item=self.range_items[-2]
        val=math.ceil((count-last_item.max_con)/result.max_con)*result.val+last_item.val
        return val
    
    def item(self,count):

        i=self.index(count)
        return self.range_items[i]
        







class DeliverInfo:
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

        # 先访问基础页面
        self.wp.get('https://fahuo.cainiao.com/web/marketing/quotation.htm')  # 菜鸟裹裹
        pass
    @exception_decorator(error_state=False)
    def handle_packet(self,bodys):
        if not bodys: 
            return
        for body in bodys:
            data_item=body["data"]["cpFeeTemplateDTOList"][0]
            name=data_item["cpName"]
            price_lst=[]
            contents_item=data_item["feeTemplateList"][0]["generalAreaInfos"]
            for content_item in contents_item:
                areas=[ item["displayName"] for item in content_item["areaInfos"]]
                prices=[]
                prices_item=content_item["ladderOrderNumberDataList"]
                for price_item in prices_item:
                    price_name=price_item.get("orderNumberDesc")
                    if not price_name:
                        continue
                    min_count=price_item["startOrderNumber"]
                    max_count=price_item["endOrderNumber"]
                    weight_info=price_item["ladderStartContinuePrice"]
                    weight_titles=weight_info["titleList"]
                    
                    
                    prices_info=[]
   
                    for weight_item in weight_info["startContinuePriceList"]:
                        min_weight=weight_item["startWeight"]
                        max_weight=weight_item["endWeight"]
                        price_val=weight_item["fixPrice"]
                        
                        prices_info.append({"min_weight":min_weight,"max_weight":max_weight,"price":price_val,"each":False})

                    prices_info.append({"min_weight":price_item["continueStartWeight"],
                                "max_weight":price_item["continueWeight"],
                                "price":price_item["continuePrice"],
                                "each":True})
                    
                    price_whole=[]
                    for price_dict,title in  zip(prices_info,weight_titles):
                        price_dict["title"]=title
                        price_whole.append(price_dict)
                    
                    result={"price_name":price_name,"min_count":min_count,"max_count":max_count,"prices_info":price_whole}
                    prices.append(result)
                price_lst.append({"areas":areas,"prices":prices})

            result={"name":name,"price_lst":price_lst}
            
            dest_dir=os.path.join(self.root_dir,"dest")
            os.makedirs(dest_dir,exist_ok=True)
            with open(os.path.join(dest_dir,f"{name}-整理.json"),"w",encoding="utf-8") as f:
                json.dump(result,f,ensure_ascii=False)

    def listen_wait_reg(self, listen_args,  res_type="XHR", retries=3):
        if not isinstance(listen_args,list):
            listen_args=[listen_args]
        companys=self.wp.eles('xpath://div[@class="cpExpressWrapper-wGmqR6"]/div')
        results=[]
        for company in companys:
            name=company.ele('xpath://span/text()')
            self.logger.update_target("获取报价", name)
            
            dest_dir=os.path.join(self.root_dir,"org")
            os.makedirs(dest_dir,exist_ok=True)
            json_path=os.path.join(dest_dir,f"{name}.json")
            result=None
            
            if os.path.exists(json_path):
                self.logger.info("成功","已存在，直接读取",update_time_type=UpdateTimeType.STEP)
                try:
                    with open(json_path,"r",encoding="utf-8") as f:
                        result=json.load(f)
                except:
                    pass
                    
            if not result:
                company.click()
                self.wp._wait_loaded()  # 等待页面开始加载（或使用其他等待条件）
                self.wp.listen.start(targets=listen_args)
                if (packet := self.wp.listen.wait(timeout=30)):
                    self.logger.info("完成","wait成功",update_time_type=UpdateTimeType.STEP)
                    result=packet.response.body
                    if not result:
                        continue
                    
                    #缓存到本地
                    with open(json_path,"w",encoding="utf-8") as f:
                        json.dump(result,f,ensure_ascii=False)
                        
                    self.logger.info(f"成功","获取成功")
            if result:
                results.append(result)
            
        return results 



        
       

    def handle_info(self):
        

        self.logger.trace("开始")

        listen_args=["/consigns/gg/feeTemplateForChosenCp.do","/api/consigns/gg/feeTemplateForChosenCp.do"]

        # 设置 API 路径，用于获取特定的信息，可能是费用模板或其他数据
        response_body=None
        # 初始化 response_body 变量为 None，用于存储 API 响应的正文内容
        response_body = self.listen_wait_reg(listen_args)
        # 调用 self.listen_wait 方法，传入 listen_args 参数，等待并获取 API 响应，将响应内容赋值给 response_body
        result=self.handle_packet(response_body)
        # 调用 self._handle_video_packet 方法，传入 response_body 参数，处理视频数据包，将处理结果赋值给 result
        if not result:
            # 如果 result 为空（即处理失败）
            self.logger.error("失败","结果为空",update_time_type=UpdateTimeType.STAGE)
            # 使用 logger 的 error 方法记录错误信息，说明失败原因，并指定更新时间类型为 STAGE
            return



        
    
    def export(self):
        
        with pd.ExcelWriter(self.excel_path,mode="w") as w:
            pass



class PriceItems:
    def __init__(self) -> None:
        self._pos_dict={}
        self._pos_prices={}
        self.logger=logger_helper()
        
    @property
    def all_pos(self):
        lst=[]
        for key in self._pos_dict.keys():
            lst.extend(self._pos_dict[key])
        return lst
    @property
    def spec_pos(self):
        return self._pos_dict.keys()
    
    
    def pos_key(self,pos:str):
        self.logger.update_target(f"查找地点:{pos}",)
        dest=bit_fuzzy_search(pos,self._pos_dict.keys())
        if dest:
            self.logger.trace("成功",dest)
            return dest
        
        for key,vals in self._pos_dict.items():
            dest=bit_fuzzy_search(pos, vals)
            if dest:
                self.logger.trace("成功",f"【{','.join(vals)}】=>【{key}】")
                return key   
        self.logger.trace("失败")
        
        return dest
        
        
    def add(self,pos:list|str,items:RangeItems):
        is_list=isinstance(pos,list)
        key=pos[0] if is_list else pos 
        dest_key=self.pos_key(key)
        if dest_key:
            if is_list and len(pos)>1:
                self._pos_dict[dest_key].extend(pos[1:])
        else:
            dest_key=key
            self._pos_dict[dest_key]=pos if is_list else [pos]
        self._pos_prices[dest_key]=items

    def pos(self,key)->RangeItems:
        dest_key=self.pos_key(key)
        return self._pos_prices[dest_key]
    

class DeliverPrice:
    def __init__(self,json_dir:str=None) -> None:
        self._companys={}
        self.logger=logger_helper()
        self.init_from_dir(json_dir)
        
    def init_from_dir(self,json_dir):
        
        if not json_dir or not os.path.exists(json_dir):
            return
        self.logger.update_target("目录初始化", json_dir)
        self.logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
        target_files = []
        for file_name in os.listdir(json_dir):
            if re.search(r"整理\.json$", file_name, re.IGNORECASE):  # 忽略大小写
                target_files.append(os.path.join(json_dir, file_name))
        for file_path in target_files:
            self.logger.stack_target("文件初始化",file_path)
            self.logger.trace("开始",update_time_type=UpdateTimeType.STEP)
            self.add_json_file(file_path)
            self.logger.trace("完成",update_time_type=UpdateTimeType.STEP)
            self.logger.pop_target()
        self.logger.trace("完成",update_time_type=UpdateTimeType.ALL)
        
        

    def add(self,company:str,price:PriceItems):
        self._companys[company]=price

    def add_json_file(self,file_path):
        result=None
        with open(file_path,"r",encoding="utf-8") as f:
            result=json.load(f)
        if not result:
            return
        name=result["name"]
        info= PriceItems()
        for pos_info in result["price_lst"]:
            areas=pos_info["areas"]
            info.add(areas,RangeItems.from_lst_dict(pos_info["prices"]))
            
        self.add(name,info)
    
    def company(self,company:str):   
        self.logger.update_target(f"查找公司名:{company}",company)
        dest_name=bit_fuzzy_search(company,self._companys.keys())
        
        logger= self.logger.trace if dest_name else self.logger.warn
        logger("成功" if dest_name else f"失败",f"找到公司名：{company}")
        return self._companys[dest_name] if dest_name else None
        
    def pos_info(self,company_name:str,pos:str):
        company_info=self.company(company_name)
        if not company_info:
            return
        
        return company_info.pos(pos)
    
    def count_info(self,company:str,pos:str,count:int):
        info=self.pos_info(company,pos)
        if not info:
            return
        return info.cal(count)
    
    #获取价格：参数按照公司-位置-数量-重量的顺序
    def price(self,company:str,pos:str,count:int,weight:int):
        info=self.count_info(company,pos,count)
        if not info:
            return
        val= info.cal(weight)
        
        return val
        
    #获取价格：按照公司-位置-数量-重量的顺序返回
    def prices(self,pos:str,count:int,weight:int):
        results={"pos":pos,"count":count,"weight":weight}
        
        prices={}
        for company in self._companys.keys():
            prices[company]=self.price(company,pos,count,weight)
            
        #按照价格排序
        results.update(dict(sorted(prices.items(), key=lambda x: x[1])))
        return results

    #纯粹是为了显示，作为核对依据
    def show_tab(self,root_dir=None):
        pos_lst=[]
        count_lst=[]
        weight_lst=[]
        company_lst=self._companys.keys()
        for company in company_lst:
            poses_item=self._companys[company]
            cur_poses=poses_item.all_pos
            pos_lst.extend(cur_poses)
            
            for pos in poses_item.spec_pos:
                pos_info=poses_item.pos(pos)
                cur_count= pos_info.keys.copy()
                cur_count[0]=1
                
                count_lst.extend(cur_count)
                for count in cur_count:
                    weight_info=pos_info.item(count)
                    cur_wight=weight_info.val.keys.copy()
                    cur_wight[0]=100
                    if len(cur_wight)>1:
                        cur_wight.append(cur_wight[-1]+1345)
                    
                    weight_lst.extend(cur_wight)
                    break
                break
            
        df=flat_df([ [{"pos":pos}for pos in unique(pos_lst)] ,
                    [{"count":count}for count in unique(count_lst)],
                    [{"weight":weight}for weight in unique(weight_lst)]

        ])
        result_lst=[]
        for row in df.itertuples():
            pos,count,weight=row.pos,row.count,row.weight
            val=manager.prices(pos,count,weight)
            if val:
                result_lst.append(val)
        result_df=pd.DataFrame(result_lst)
        result_df.to_excel(os.path.join(root_dir,"快递费用.xlsx"),index=False)
        

        
        
        pass
    
    
if __name__=="__main__":
    root_dir=r"F:\worm_practice\red_book\deliver"

    manager= DeliverPrice(os.path.join(root_dir,"dest"))
    manager.show_tab(root_dir)

    #manager.prices(pos,count,weight)
    exit()
    




    wp=WebPage()
    root_dir=r"F:\worm_practice\red_book\deliver"
    info_obj=DeliverInfo(wp,root_dir,"快递价格")
    deliver=info_obj.handle_info()


    
    info_obj.export()

    pass