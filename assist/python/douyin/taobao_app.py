
import sys
from pathlib import Path
import os
import time
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import ThreadTask,get_param_from_url,logger_helper,UpdateTimeType,exception_decorator,except_stack,ThreadPool

from taobao_manager import tb_manager
from douyin.taobao_thread import InteractShop,HandleProducts,InteractProduct,HandlePics,InteractImp,DownloadPics,OcrPics
from queue import Queue
import threading
from taobao_setting import *
from taobao_config import *

class TbApp():
    
    def __init__(self) -> None:
        
        self.shop_url_queue=Queue()
        self.products_json_queue=Queue()
        self.product_url_queue=Queue()
        self.pics_json_queue=Queue()
        self.download_pic_queue=Queue()
        self.ocr_pic_queue=Queue()
        
        class_name=self.__class__.__name__
        
        self.cache_pool=ThreadPool(thread_name=class_name)
        
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
        
        
        self.manager=tb_manager()
        self.logger=logger_helper(class_name)
        
        #开启缓冲池
        self.cache_pool.start()
        
    @property
    def _msg_queque_dict(self):
        result={
            shop_type:self.shop_url_queue,
            goods_type:self.product_url_queue
        }
        return result
        
    def msg_queue(self,type):
        result=self._msg_queque_dict
        return result.get(type,None)
    def send_msg(self,msg_type,urls:list|str):
        if isinstance(urls,str):
            urls=[urls]
        logger=self.logger
        logger.update_target("收到消息",f"msg_type:{msg_type},url:{urls}") 
        logger.trace("开始处理",update_time_type=UpdateTimeType.STAGE) 
        cur_queue=self.msg_queue(msg_type)
        if not cur_queue:
            logger.error("查找不到指定类型的输入队列",update_time_type=UpdateTimeType.STAGE)
            return
        for url in urls:
            cur_queue.put(url)
            logger.trace(f"消息入队",url,update_time_type=UpdateTimeType.STEP) 
            
    
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
        self.interact_shop.join()
        self.handle_goods.join()
        self.interact_goods.join()
        self.handle_pics.join()
        self.download_pic_queue.join()
        self.ocr_pic_queue.join()
        


    @exception_decorator(error_state=False)
    def done(self):
        tb_manager.destroy_instance()
    
    def stop_cache_pool(self):
        self.cache_pool.shutdown()
def main():
    
    goods_urls=[
        'https://item.taobao.com/item.htm?id=742960815434',
                ]
    # shop_urls=["https://shop293825603.taobao.com/?spm=tbpc.mytb_followshop.item.shop",
    #            'https://shop60537259.taobao.com/?spm=tbpc.mytb_followshop.item.shop']
    shop_urls=["https://shop293825603.taobao.com/?spm=tbpc.mytb_followshop.item.shop",]

    app=TbApp()
    try:
        # for url in goods_urls:
        #     manager.put((goods_type,url))
        for url in shop_urls:
            app.send_msg(shop_type,url)
        app.start()
        # app.done()
        tb_manager()._save_xlsx_df()
        app.stop_cache_pool()
    except:
        pass
    finally:
        pass
    
    
    
if __name__=="__main__":
    main()