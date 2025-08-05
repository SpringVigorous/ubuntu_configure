
import sys
from pathlib import Path
import os
import time
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import ThreadTask,get_param_from_url,logger_helper,UpdateTimeType,exception_decorator,except_stack,ThreadPool

from taobao_manager import tb_manager
from taobao_thread import InteractShop,HandleProducts,InteractProduct,HandlePics,InteractImp,DownloadPics,OcrPics
from queue import Queue
import threading
from taobao_setting import *
from taobao_config import *
from taobao_tools import dest_file_path
import pandas as pd
class TbApp():
    
    def __init__(self) -> None:
        self.manager=tb_manager()
        class_name=self.__class__.__name__
        self.logger=logger_helper(class_name)

        self.shop_url_queue=Queue()
        self.products_json_queue=Queue()
        self.product_url_queue=Queue()
        self.pics_json_queue=Queue()
        self.download_pic_queue=Queue()
        self.ocr_pic_queue=Queue()
        
        
        self.cache_pool=ThreadPool(root_thread_name=class_name)
        
        self.stop_shop_interact_event=threading.Event()
        stop_goods_interact_event=threading.Event()
        stop_handle_goods_event=threading.Event()
        stop_handle_pics_event=threading.Event()
        stop_downnload_pics_event=threading.Event()
        stop_ocr_pics_event=threading.Event()
        
        
        imp=InteractImp(self.cache_pool)
        
        self.interact_shop= InteractShop(self.shop_url_queue,self.products_json_queue,self.stop_shop_interact_event,out_stop_event=stop_handle_goods_event,interact=imp)
        self.handle_goods=HandleProducts(self.products_json_queue,stop_handle_goods_event,output_queue=self.product_url_queue,out_stop_event=stop_goods_interact_event)
        
        self.interact_goods= InteractProduct(self.product_url_queue,self.pics_json_queue,stop_goods_interact_event,out_stop_event=stop_handle_pics_event,interact=imp)
        self.handle_pics=HandlePics(self.pics_json_queue,stop_handle_pics_event,output_queue=self.download_pic_queue, out_stop_event=stop_downnload_pics_event)
        self.download_pics=DownloadPics(self.download_pic_queue,stop_downnload_pics_event,output_queue=self.ocr_pic_queue,out_stop_event=stop_ocr_pics_event)
        self.ocr_pics=OcrPics(self.ocr_pic_queue,stop_ocr_pics_event,output_queue=None,out_stop_event=None)
        
        
        self.queue_lst:list=[]
        self.thread_lst:list=[]
        
    @property
    def _msg_queque_dict(self):
        result={
            shop_type:self.shop_url_queue,
            goods_type:self.product_url_queue
        }
        return result
        
    @exception_decorator(error_state=False)
    def handle_nodone_task(self):
        results=self.manager.get_undone_df()
        if not results:return
        nodetail_df,undownload_df,unocr_df=results

        
        #未识别图片
        if not unocr_df.empty:
            
            self.logger.trace(f"开始处理未识别图片",f"共{len(unocr_df)}个")
            # index=0
            for _,row in unocr_df.iterrows():
                # if index>8:
                #     break
                # index+=1
                name=f"{row[name_id]}.jpg"
                org_pic=dest_file_path(org_pic_dir,name)
                # orc_pic=dest_file_path(ocr_pic_dir,name)
                self.ocr_pic_queue.put(org_pic)
            pass
        
        #未下载图片
        if not undownload_df.empty:
            self.download_pic_queue.put((True,undownload_df))
            
            
        #未获取详情
        if not nodetail_df.empty:
            urls=nodetail_df[item_url_id].tolist()
            self.send_msg(goods_type,urls)

    def msg_queue(self,type):
        result=self._msg_queque_dict
        return result.get(type,None)
    def send_msg(self,msg_type,urls:list|str):
        if isinstance(urls,str):
            urls=[urls]
        logger=self.logger
        logger.update_target(f"收到消息共{len(urls)}个",f"msg_type:{msg_type},url:{urls}") 
        logger.info("开始处理",update_time_type=UpdateTimeType.STAGE) 
        cur_queue=self.msg_queue(msg_type)
        if not cur_queue:
            logger.error("查找不到指定类型的输入队列",update_time_type=UpdateTimeType.STAGE)
            return
        for index,url in enumerate(urls):
            logger.update_target(f"第{index}个消息入队",f"{url}") 
            cur_queue.put(url)
            logger.trace("开始",update_time_type=UpdateTimeType.STEP) 
            
    

    pass

    @exception_decorator(error_state=False)
    def start(self):
        
        
        
        self.interact_shop.start()
        self.interact_goods.start()
        self.handle_goods.start()
        self.handle_pics.start()
        self.download_pics.start()
        self.ocr_pics.start()
        
        
        #停止标志
        self.stop_shop_interact_event.set()
        
        
        #队列join()
        self.shop_url_queue.join()
        self.products_json_queue.join()
        self.product_url_queue.join()
        self.pics_json_queue.join()
        self.download_pic_queue.join()
        self.ocr_pic_queue.join()
        
        #开启缓冲池
        # self.cache_pool._start()
        
        #现成join()
        self.interact_shop.join()
        self.interact_goods.join()
        self.handle_goods.join()
        self.handle_pics.join()
        self.download_pics.join()
        self.ocr_pics.join()

    @exception_decorator(error_state=False)
    def done(self):
        tb_manager.destroy_instance()
    
    def stop_cache_pool(self):
        self.cache_pool.join()
        

    
def main():
    # tb=tb_manager()
    # # tb.init_product_df_product_name()
    # # tb._save_xlsx_df()
    
    #结果分别存储到各自文件夹中，可选
    # tb.separate_ocr_results()
    
    
    #图片按照num新建文件夹存放，后续不需要
    # c
    
    #图片名长度过短,临时补救措施，后续不需要
    # # if tb.rename_pic_name(3):
    # #     tb._save_xlsx_df()
    

    # return
    
    
    goods_urls=[
        'https://item.taobao.com/item.htm?id=742960815434',
                ]
    # shop_urls=['https://shop60537259.taobao.com/?spm=tbpc.mytb_followshop.item.shop',
    # "https://shop293825603.taobao.com/?spm=tbpc.mytb_followshop.item.shop",
            #    ]
    shop_urls=["https://shop380595428.taobao.com/?spm=tbpc.mytb_followshop.item.shop",]

    app=TbApp()
    app.handle_nodone_task()
    try:
        # for url in goods_urls:
        #     manager.put((goods_type,url))
        for url in shop_urls:
            app.send_msg(shop_type,url) 
        app.start()
        # app.done()
    except:
        pass
    finally:
        app.stop_cache_pool()
        tb_manager()._save_xlsx_df()
        #拆分看结果
        tb_manager().separate_ocr_results()

    
    # os.system(f"shutdown /s /t 1")
    
if __name__=="__main__":
    main()
    
