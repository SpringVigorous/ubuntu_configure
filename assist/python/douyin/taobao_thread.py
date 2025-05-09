import sys
from DrissionPage import WebPage
from pathlib import Path
import os
import time
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import ThreadTask,get_param_from_url,find_last_value_by_col_val,ThreadPool,get_next_filepath,write_to_json_utf8_sig,RetryOperater,fatal_link_error
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from taobao_config import *
from taobao_tools import *
from taobao_manager import tb_manager
from taobao_setting import *
import re
import json
import threading
from queue import Queue
def sleep(sec:int|float=6):
    time.sleep(sec)
def desc_json(org_str)->dict:
    return bracket_params_to_dict(org_str,"mtopjsonp")
def shopName_from_title(title):
    pattern = r"-(.*?)-"  # 匹配两个短横线之间的内容
    result = re.search(pattern, title)
    if result:
        return result.group(1)  # 输出: 木槿食养
    else:
        return title
    
    
    
class InteractImp():
    def __init__(self,cache_thread:ThreadPool):
        self._lock=threading.Lock()
        self.wp:WebPage=WebPage()
        url='https://www.taobao.com/'
        self.wp.get(url)
        self.logger=logger_helper("InteractImp")
        self.manager=tb_manager()
        self.cache_thread:ThreadPool=cache_thread
        self._msg_count:int=0
        #登录
        pass
        self.fetch_count:int=0
        
        self.retry_operater=RetryOperater(3)
    @property
    def msg_count(self)->int:
        self._msg_count+=1
        return self._msg_count
    @property
    def fatal_error(self)->bool:
        return self.retry_operater.fatal_error or fatal_link_error()
    
    @exception_decorator(error_state=False)
    def close(self):
        self.wp.close()

    @exception_decorator(error_state=False)
    def handle_goods(self,url):
        itemId=get_param_from_url(url,"id")
        logger=self.logger
        logger.update_target(f"收到第{self.msg_count}个消息:{url}",f"当前id:{itemId}")
        logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
        random_sleep(8,20,logger)
        if not force_update and  self.manager.has_id_val(self.manager.pic_df,item_id,itemId):
            logger.info(f"数据已存在，忽略此消息",update_time_type=UpdateTimeType.STAGE)
            return
        main_pic_result:dict=None
        desc_pic_result:dict=None
        listen_apis=[listent_main_api,listen_desc_api]
        
        
        def do_fun():
            packets = self.wp.listen.wait(2,fit_count=False,timeout=10)            
            return packets
            
        def faliure_fun():

            logger.warn(f"未监听到:{';'.join(listen_apis)}",except_stack(),update_time_type=UpdateTimeType.STAGE)
            self.wp.listen.stop()
            self.wp.scroll.to_bottom()
            self.wp.listen.start(listen_apis)
            self.wp.refresh()
        
        with self._lock:
            try:
                self.wp.listen.start(listen_apis) 
                self.wp.get(url)
                self.retry_operater.reset(2,do_fun,faliure_fun)
                self.wp.wait.eles_loaded(goods_loaded_path,timeout=10)
                packets=self.retry_operater.success()
                if not packets:
                    return
                for packet in packets:
                    target=packet.target
                    body=packet.response.body
                    if not body:
                        continue
                    if target==listent_main_api:
                        main_pic_result=body
                    else:
                        desc_pic_result=desc_json(body)
                self.wp.scroll.to_bottom()
            except Exception as e:
                logger.error("异常",f"{e}:\n{except_stack()}",update_time_type=UpdateTimeType.STAGE)
                
                
        logger.info(f"完成",update_time_type=UpdateTimeType.STAGE)
        
        
        if main_pic_result:
            main_pic_result[item_id]=itemId
        if desc_pic_result:
            desc_pic_result[item_id]=itemId
        #判断是不是受限了
        pass
        
        #写入
        if main_pic_result:
            self.cache_thread.submit(write_to_json_utf8_sig,get_next_filepath(main_dir,f"main_{itemId}",".json"),main_pic_result)  
        if desc_pic_result:
            self.cache_thread.submit(write_to_json_utf8_sig,get_next_filepath(desc_dir,f"desc_{itemId}",".json"),desc_pic_result)  
            
        if  main_pic_result or desc_pic_result:
            return main_pic_result,desc_pic_result

    @exception_decorator(error_state=False)
    def handle_shop(self, url)->tuple[type,list]:
        shopId=shop_id_by_shop_goods_url(url)
        logger=self.logger
        logger.update_target(f"收到第{self.msg_count}个消息:{url}",f"当前id:{shopId}")
        if  not force_update and  not shopId or self.manager.has_shop_id(shopId):
            logger.info(f"数据已存在，忽略此消息",update_time_type=UpdateTimeType.STAGE)
            return
        json_results=[]
        def do_func():
            # 捕获API数据包
            packet = self.wp.listen.wait(timeout=15)
            return packet
            pass
        
        def failure_func():
            logger.warn("未捕获到数据包，尝试重新监听...",update_time_type=UpdateTimeType.STEP)
            self.wp.listen.start(listent_shop_api)  # 重新启动监听
            random_sleep(3,10,logger)
            
            
            
        with self._lock:
            # 初始化监听
            self.retry_operater.reset(2, normal_func=do_func, failure_func=failure_func)
            
            self.wp.listen.start(listent_shop_api)
            self.wp.get(url)
            # shop_name=shopName_from_title(self.wp.title)

            # json_results=self.retry_operater.success()
            index = 1
            
            while True:
                try:
                    # 等待页面元素加载
                    if index==1 and not self.wp.wait.eles_loaded(shop_loaded_path, timeout=10):
                        logger.warn("未检测到加载元素，可能已到达最后一页",update_time_type=UpdateTimeType.STAGE)
                        break
                    packet=self.retry_operater.success()
                    if not packet:
                        break
                    json_data = packet.response.body
                    json_data[shop_id]=shopId
                    
                    #写入
                    self.cache_thread.submit(write_to_json_utf8_sig,get_next_filepath(shop_dir,f"shop_{shopId}",".json"),json_data)  
                   
                    #加入
                    json_results.append(json_data)
                    # 提取核心数据
                    data = json_data.get('data', {})
                    if "itemInfoDTO" in data:
                        data = data["itemInfoDTO"]
                    # 检查是否还有下一页
                    if not data.get('hasNext', False):
                        logger.info("完成","检测到最后一页标志",update_time_type=UpdateTimeType.STAGE)
                        break
                    # 准备翻页操作
                    tabs = self.wp.eles(shop_loaded_path)
                    if tabs:
                        # 先停止旧监听再启动新监听
                        self.wp.listen.stop()
                        random_sleep(10,20,logger)
                        self.wp.listen.start(listent_shop_api)
                        # 滚动到可见区域并点击
                        self.wp.scroll.to_see(tabs[-1])
                        self.wp.scroll.to_bottom()
                        index += 1
                    else:
                        logger.warn("失败","未找到翻页元素",update_time_type=UpdateTimeType.STAGE)
                        break
                except Exception as e:
                    logger.error("异常",except_stack(),update_time_type=UpdateTimeType.STAGE)
                    if max_retries <= 0:
                        logger.warn("失败","超过最大重试次数，终止操作",update_time_type=UpdateTimeType.STAGE)
                        break
                    max_retries -= 1
                    # self.wp.refresh()
        return json_results
    @exception_decorator(error_state=False)
    def handle_goods_old(self,url):
        itemId=get_param_from_url(url,"id")
        logger=self.logger
        logger.update_target(f"收到第{self.msg_count}个消息:{url}",f"当前id:{itemId}")
        logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
        random_sleep(8,20,logger)
        if self.manager.has_id_val(self.manager.pic_df,item_id,itemId):
            logger.info(f"数据已存在，忽略此消息",update_time_type=UpdateTimeType.STAGE)
            return
        main_pic_result:dict=None
        desc_pic_result:dict=None
        
        listen_apis=[listent_main_api,listen_desc_api]
        # with self._lock:
        #     try:
        #         self.wp.listen.start(listen_apis) 
        #         self.wp.get(url)
                    
        #         self.retry_operater.reset(retry_count=3)
                
        #         self.wp.wait.eles_loaded(goods_loaded_path,timeout=10)
        #         def do_func():
        #             packets = self.wp.listen.wait(2,fit_count=False,timeout=10)

        #         if not packets:
        #             logger.warn(f"未监听到:{';'.join(listen_apis)}",except_stack(),update_time_type=UpdateTimeType.STAGE)
        #             return
                
        #         for packet in packets:
        #             target=packet.target
        #             body=packet.response.body
        #             if not body:
        #                 continue
        #             if target==listent_main_api:
        #                 main_pic_result=body
                    
        #             else:
        #                 desc_pic_result=desc_json(body)
        #         self.wp.scroll.to_bottom()
        #     except Exception as e:
        #         logger.error("异常",f"{e}:\n{except_stack()}",update_time_type=UpdateTimeType.STAGE)
                
                
        logger.info(f"完成",update_time_type=UpdateTimeType.STAGE)
        
        
        if main_pic_result:
            main_pic_result[item_id]=itemId
        if desc_pic_result:
            desc_pic_result[item_id]=itemId
        #判断是不是受限了
        pass
        
        #写入
        self.cache_thread.submit(write_to_json_utf8_sig,get_next_filepath(main_dir,f"main_{itemId}",".json"),main_pic_result)  
        self.cache_thread.submit(write_to_json_utf8_sig,get_next_filepath(desc_dir,f"desc_{itemId}",".json"),desc_pic_result)  
        if  main_pic_result or desc_pic_result:
            return main_pic_result,desc_pic_result
    @exception_decorator(error_state=False)
    def handle_shop_old(self, url)->tuple[type,list]:
        shopId=shop_id_by_shop_goods_url(url)
        logger=self.logger
        logger.update_target(f"收到第{self.msg_count}个消息:{url}",f"当前id:{shopId}")
        if not shopId or self.manager.has_shop_id(shopId):
            logger.info(f"数据已存在，忽略此消息",update_time_type=UpdateTimeType.STAGE)
            return
        json_results=[]
        with self._lock:
            # 初始化监听
            self.wp.listen.start(listent_shop_api)
            self.wp.get(url)
            index = 1
            max_retries_def = 3  # 最大重试次数
            max_retries = max_retries_def  # 最大重试次数
            shop_name=shopName_from_title(self.wp.title)
            while True:
                try:
                    # 等待页面元素加载
                    if index==1 and not self.wp.wait.eles_loaded(shop_loaded_path, timeout=10):
                        logger.warn("未检测到加载元素，可能已到达最后一页",update_time_type=UpdateTimeType.STAGE)
                        break
                    # 捕获API数据包
                    packet = self.wp.listen.wait(timeout=15)
                    if not packet and max_retries>=0:
                        logger.warn("未捕获到数据包，尝试重新监听...",update_time_type=UpdateTimeType.STEP)
                        self.wp.listen.start(listent_shop_api)  # 重新启动监听
                        random_sleep(3,10,logger)
                        max_retries-=1
                        continue
                    max_retries=max_retries_def
                    # 处理响应数据
                    json_data = packet.response.body
                    json_data[shop_id]=shopId
                    
                    #写入
                    self.cache_thread.submit(write_to_json_utf8_sig,get_next_filepath(shop_dir,f"shop_{shopId}",".json"),json_data)  
                   
                    #加入
                    json_results.append(json_data)
                    # 提取核心数据
                    data = json_data.get('data', {})
                    if "itemInfoDTO" in data:
                        data = data["itemInfoDTO"]
                    # 检查是否还有下一页
                    if not data.get('hasNext', False):
                        logger.info("完成","检测到最后一页标志",update_time_type=UpdateTimeType.STAGE)
                        break
                    # 准备翻页操作
                    tabs = self.wp.eles(shop_loaded_path)
                    if tabs:
                        # 先停止旧监听再启动新监听
                        self.wp.listen.stop()
                        random_sleep(10,20,logger)
                        self.wp.listen.start(listent_shop_api)
                        # 滚动到可见区域并点击
                        self.wp.scroll.to_see(tabs[-1])
                        self.wp.scroll.to_bottom()
                        index += 1
                    else:
                        logger.warn("失败","未找到翻页元素",update_time_type=UpdateTimeType.STAGE)
                        break
                except Exception as e:
                    logger.error("异常",except_stack(),update_time_type=UpdateTimeType.STAGE)
                    if max_retries <= 0:
                        logger.warn("失败","超过最大重试次数，终止操作",update_time_type=UpdateTimeType.STAGE)
                        break
                    max_retries -= 1
                    # self.wp.refresh()
        return json_results
class InteractShop(ThreadTask):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event,interact:InteractImp):
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_event,out_stop_event=out_stop_event)
        self.interact:InteractImp=interact
        self.set_name(self.__class__.__name__)
    @exception_decorator()
    def _handle_data(self, data):
        #致命错误，退出
        if self.interact.fatal_error:
            self.clear_input()
            self.stop()
            return

        url=data
        result=None
        res=self.interact.handle_shop(url)
        return res
class InteractProduct(ThreadTask):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event,interact:InteractImp):
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_event,out_stop_event=out_stop_event)
        self.interact:InteractImp=interact
        self.set_name(self.__class__.__name__)
        
        
    def _final_run_after(self):
        self.interact.close()
        pass
    @exception_decorator(error_state=False)
    def _handle_data(self, data):
        #致命错误，退出
        if self.interact.fatal_error:
            self.clear_input()
            self.stop()
            return
        
        
        url=data
        result=self.interact.handle_goods(url)
        return result
class HandleProducts(ThreadTask):
    def __init__(self,input_queue,stop_event,output_queue,out_stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=output_queue,out_stop_event=out_stop_event)
        self.manager=tb_manager()
        class_name=self.__class__.__name__
        
        
        self.logger.update_target(class_name)
        self.set_name(class_name)
    @exception_decorator(error_state=False)
    def _handle_data(self, data):
        if not data:
           return
        self._handle_goods_data(data)
    def _handle_goods_data(self,data):
        shop_df:pd.DataFrame=pd.DataFrame()
        goods_dfs=[]
        shopId=None
        for json_data in data:
            shopId=json_data.get(shop_id,None)
            shop_data=org_shop_dict_from_product(json_data)
            if  shop_df.empty and shop_data:
                shop_df=pd.DataFrame([shop_data])
            goods_dfs.append(org_procduct_to_df(json_data))
        goods_df=pd.concat(goods_dfs)
        goods_df[shop_id]=shopId
        self.manager.update_shop_df(shop_df)
        new_df:pd.DataFrame=self.manager.update_product_df(goods_df)
        if new_df.empty:
            return
        else:
            logger=self.logger
            # print(new_df)
            for index,item in new_df.iterrows():
                url=item[item_url_id]
                itemId=item[item_id]
                logger.update_target(f"处理第{index}个商品",f"{url}:{itemId}")
                self.logger.trace("开始")
                #测试流程用
                # if index>1:break
                self.output_queue.put(url)
class HandlePics(ThreadTask):
    def __init__(self,input_queue,stop_event,output_queue,out_stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=output_queue,out_stop_event=out_stop_event)
        self.manager=tb_manager()
        self.set_name(self.__class__.__name__)
    @exception_decorator()
    def _handle_data(self, data):

        if not data:
           return
        return self._handle_detail_data(data)
    def _handle_detail_data(self,data):
        main_data, desc_data=data
        main_pic=org_main_lst(main_data)
        sku_pic=sku_infos_from_main(main_data)
        
        itemId=main_data.get(item_id)
        userId=None
        if itemId :
            shopId=find_last_value_by_col_val(self.manager.product_df,item_id,itemId,shop_id)
            userId=find_last_value_by_col_val(self.manager.shop_df,shop_id,shopId,user_id)
        if not userId:
            self.logger.warn("失败",f"未找到用户ID,当前{item_id}:{itemId}",update_time_type=UpdateTimeType.STAGE)
            # print(self.manager.product_df)
            # print(self.manager.shop_df)
            # return
        desc_pic=org_desc_lst(desc_data,userId)
        main_df=pd.DataFrame(main_pic)
        desc_df=pd.DataFrame(desc_pic)
        sku_df=pd.DataFrame(sku_pic)
        
        product_df=pd.concat([main_df,sku_df,desc_df])
        product_df[item_id]=product_df[item_id].astype(str)
        new_df=self.manager.update_pic_df(product_df)
        if( not new_df is None) and  (not new_df.empty):
            if new_df[pic_url_id].isna().any():
                pass
            return (True,new_df)



class DownloadPics(ThreadTask):
    def __init__(self,input_queue,stop_event,output_queue,out_stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=output_queue,out_stop_event=out_stop_event)
        self.manager=tb_manager()

        class_name=self.__class__.__name__
        
        self.cache_thread=ThreadPool(thread_name=class_name)
        self.set_name(class_name)
    @exception_decorator()
    def _handle_data(self, data):
        self._download_by_df(data)
    
    

    def _final_run_after(self):
        self.cache_thread.shutdown()
        
    def _download_by_df(self,data)->list[str]:
        df:pd.DataFrame=data[1]
        if df.empty:
            return
        if not self.cache_thread.has_init_thread:
            self.cache_thread.restart()
        logger=self.logger


        def _download(url,dest_path):
            logger.update_target(detail=f"{url}->{dest_path}")
            try:
                if download_sync(url,dest_path,headers=download_pic_headers,verify=download_verify):
                    # results.append(dest_path)
                    self._push_data(dest_path)
            except  Exception as e:
                logger.error("异常",f"原因：{e}",update_time_type=UpdateTimeType.STAGE)
            
        
        for index,row in df.iterrows():
            url=row[pic_url_id].strip()
            name=row[name_id]
            if not url or not name:
                logger.warn(f"信息为空",f"{row.to_dict()}")
                continue
            file_path=dest_file_path(org_pic_dir,f"{name}.jpg")
            self.cache_thread.submit(_download,fix_url(url),file_path)
            


        
class OcrPics(ThreadTask):
    def __init__(self,input_queue,stop_event,output_queue,out_stop_event):
        super().__init__(input_queue,stop_event=stop_event,output_queue=output_queue,out_stop_event=out_stop_event)
        self.manager=tb_manager()
        class_name=self.__class__.__name__
        self.cache_thread=ThreadPool(thread_name=class_name)
        self.set_name(class_name)
        self._lock=threading.Lock()
        self._ocr_lst:list[str]=[]
        self.logger.update_target("文字识别")
    @exception_decorator()
    def _handle_data(self,data):
        if not data or not isinstance(data,str):
            return

        return self._ocr_pic(data)
        
    def _final_run_after(self):
        self.cache_thread.shutdown()
        with self._lock:
            if not self._ocr_lst:
                return
            ocr_df=pd.DataFrame(self._ocr_lst)
            self.manager.update_ocr_df(ocr_df)
            self._ocr_lst=[]
 

    def _ocr_pic(self,pic_path):
        if not self.cache_thread.has_init_thread:
            self.cache_thread.restart()
        logger=self.logger

        def _ocr_pics(org_path,ocr_path):
            orc_logger=logger_helper("文字识别",f"{org_path}->{ocr_path}")

            texts=None
            try:
                ocr_pic=OCRProcessor()
                _,texts=ocr_pic.process_image(org_path,output_path=ocr_path)
                orc_logger.trace("成功",f"{ocr_path}",update_time_type=UpdateTimeType.STAGE)
            except  Exception as e:
                orc_logger.error("异常",f"原因：{e}",update_time_type=UpdateTimeType.STAGE)
            finally:
                # if texts:
                with self._lock:
                    self._ocr_lst.append({name_id:Path(ocr_path).stem,ocr_text_id:";".join(texts)})
        try:
            logger.stack_target("收到消息",f"{pic_path}")
            logger.trace("提交处理",update_time_type=UpdateTimeType.STAGE)
            ocr_path=dest_file_path(ocr_pic_dir, Path(pic_path).name)
            self.cache_thread.submit(_ocr_pics,pic_path,ocr_path)
        except  Exception as e:
            logger.error("异常",f"原因：{e}",update_time_type=UpdateTimeType.STAGE)
        finally:
            logger.pop_target()
        
