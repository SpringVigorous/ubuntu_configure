
from audio_thread import *
from audio_kenel import *
from base import exception_decorator,backup_xlsx,unique,envent_sequence,read_from_txt_utf8_sig,audio_root
from audio_manager import AudioManager
from analyse_log import download_audio_by_log
import time
class AudioApp():
    def __init__(self) -> None:
        
        self.audio_url_queue=Queue()
        self.bz_url_queue=Queue()
        self.album_url_queue=Queue() 
        self.download_queue=Queue()
        
        self.bz_stop_envent=threading.Event()#博主所有专辑 停止事件
        album_stop_envent=threading.Event()#专辑所有声音 停止事件
        audio_stop_envent=threading.Event()
        self.download_stop_event=threading.Event()


        self.interact_bz=InteractBoZhu(self.bz_url_queue,self.album_url_queue,self.bz_stop_envent,album_stop_envent)
        self.interact_album=InteractAlbum(self.album_url_queue,self.audio_url_queue,album_stop_envent,audio_stop_envent)
        self.interact_audio=InteractAudio(self.audio_url_queue,audio_stop_envent)
        self.download_thread=DownloadVideo(self.download_queue,self.download_stop_event)
        
                
        self.interact_bz.start()
        self.interact_album.start()
        self.interact_audio.start()
        self.download_thread.start()
        self.logger=logger_helper(self.__class__.__name__,"获取音频")

        
        self.manager=AudioManager()
        
        
        self.msg_index_lst:list=[0]*3
        

    
        
    
    def _msg_count(self,index:int,add_val:int=0)->int:
        if index<0 or index+1>len(self.msg_index_lst):
            return -1
        self.msg_index_lst[index]+=add_val
        return self.msg_index_lst[index]
    
    @property
    def author_msg_index(self)->int:
        return 0
    

    @property
    def album_msg_index(self)->int:
        return 1

        

    @property
    def audio_msg_index(self)->int:
        return 2

    
    
    
    @exception_decorator(error_state=False)
    def _add_msg(self,msg_lst:list|str|dict,msg_index,target_name,msg_queue:Queue):
        if not msg_lst: return
        if not isinstance(msg_lst,list):
            msg_lst=[msg_lst]
            
            
        self.logger.update_time(UpdateTimeType.STAGE)
        with self.logger.raii_target(f"添加{target_name}消息",f"共{len(msg_lst)}个") as outer_logger:
            cur_index=self._msg_count(msg_index,1)
            for index,url in enumerate(msg_lst):
                with self.logger.raii_target(detail=f"第{cur_index}次：第{index+1}个{url} ") as inner_logger:
                    msg_queue.put(url)
                    inner_logger.trace("成功",update_time_type=UpdateTimeType.STEP)
            inner_logger.trace("成功",update_time_type=UpdateTimeType.STAGE)

        
        
    @exception_decorator(error_state=False)
    def add_bz_msg(self,urls:str|list[str]):
        self._add_msg(urls,self.author_msg_index,"博主",self.bz_url_queue)


    """
    data:dict={           
        href_id:"",
        album_id:"",
        local_path_id:"",
        parent_xlsx_path_id:"",
        parent_sheet_name_id:"",
    }
    
    """
    @exception_decorator(error_state=False)
    def add_album_msg(self,msg_lst:dict|list[dict]):
        self._add_msg(msg_lst,self.album_msg_index,"专辑",self.album_url_queue)

            
        
    """
    data:dict={
        url_id:str,
        dest_path_id:str,
        xlsx_path_id:str,
        sheet_name_id:str
    }

    """

    @exception_decorator(error_state=False)
    def add_audio_msg(self,msg_lst:dict|list[dict]):   
        self._add_msg(msg_lst,self.audio_msg_index,"音频",self.audio_url_queue)

    @staticmethod

    def continue_audio_impl(album_df,album_xlsx_path,audio_sheet_name):
        

        if df_empty(album_df):
            return
        msg_lst=[]
        for index,row in album_df.iterrows():
            status=TaskStatus.from_value( row[downloaded_id])
            if status.is_temp_canceled:
               album_df.loc[index,downloaded_id] =status.clear_temp_canceled.value
            if msg:=row_path_to_msg(row,album_xlsx_path,audio_sheet_name):
                msg_lst.append(msg)
        return msg_lst
    @exception_decorator(error_state=False)
    def continue_author(self):
        xlsx_path,name,catalog_df=self.manager.filter_catalog_df
        if df_empty(catalog_df) :
            return
        if urls:=list(filter(lambda x:x ,catalog_df[href_id])):
            self.add_bz_msg(urls)

            
            
    @staticmethod

    def continue_album_impl(author_xlsx_path,author_name,author_df):

        msg_lst=[]
        for author_index,author_row in author_df.iterrows():
            album_path= author_row[local_path_id]
            if not isinstance(album_path,str) or not album_path:
                continue
            
 
            msg={
                href_id:author_row[href_id],
                local_path_id:album_path,
                title_id:author_row[title_id],
                
                parent_xlsx_path_id:author_xlsx_path,
                parent_sheet_name_id:author_name,                   
            }
            
            album_name=author_row.get(album_id,None)
            if not album_name:
                album_name=get_album_name(author_row[title_id])
            msg[album_id]=album_name

            msg_lst.append(msg)


    
        return msg_lst


    @exception_decorator(error_state=False)
    def continue_album(self):
        for author_xlsx_path,author_name,author_df in self.manager.filter_author_df:
            msg_lst=AudioApp.continue_album_impl(author_xlsx_path,author_name,author_df )
            if msg_lst:
                self.add_album_msg(msg_lst)
        
    @exception_decorator(error_state=False)
    def continue_audio(self):
        for album_xlsx_path,album_name,album_df in self.manager.filter_album_df:
            if msg_lst:=AudioApp.continue_audio_impl(album_df,album_xlsx_path,album_name):
                self.add_audio_msg(msg_lst)

    @exception_decorator(error_state=False)
    def continue_download(self):
        msg_lst= self.manager.fail_has_media_url_audios
        if not msg_lst: return

        with self.logger.raii_target("添加Download消息",f"共{len(msg_lst)}个") as logger:
            self.download_queue.put(msg_lst)
            logger.trace("成功",update_time_type=UpdateTimeType.STAGE)




    def run(self):
        self.bz_stop_envent.set()
        self.download_stop_event.set()
        
        self.download_queue.join()
        self.bz_url_queue.join()
        self.album_url_queue.join()
        self.audio_url_queue.join()
        
        
        
        
        self.download_thread.join()
        self.interact_bz.join()
        self.interact_bz.join()
        self.interact_album.join()
        self.interact_audio.join()
        
        #通过日志信息，下载未下载成功的音频
        download_audio_by_log()
        
        #保存xlsx
        self.save_xlsx()
        self.logger.info("结束",update_time_type=UpdateTimeType.ALL)
        
        
    @exception_decorator(error_state=False)
    def save_xlsx(self):
        self.manager.save()

    def force_init_ignore_sound(self,ignore=True):
        self.manager.set_ignore_sound(ignore)
        
        
    def force_init_ignore_album(self,ignore=True):
        self.manager.set_ignore_album(ignore)    
def main():
    
    
    app:AudioApp= AudioApp()

    bz_urls=[
        "https://www.ximalaya.com/zhubo/460372713",
        "https://www.ximalaya.com/zhubo/29434986",
        "https://www.ximalaya.com/zhubo/181500128",
        "https://www.ximalaya.com/zhubo/58841314",
        "https://www.ximalaya.com/zhubo/235830385",
        "https://www.ximalaya.com/zhubo/51763868",
        "https://www.ximalaya.com/zhubo/43361493",
        "https://www.ximalaya.com/zhubo/10553948",
        "https://www.ximalaya.com/zhubo/55168786",
        "https://www.ximalaya.com/zhubo/6460629",
        "https://www.ximalaya.com/zhubo/90400568",
        "https://www.ximalaya.com/zhubo/62273426",
        "https://www.ximalaya.com/zhubo/67632526",
        "https://www.ximalaya.com/zhubo/52023510",
        "https://www.ximalaya.com/zhubo/163605621",
        "https://www.ximalaya.com/zhubo/65689410",

             ]
    # app.add_bz_msg(bz_urls)

    #筛选album
    # app.force_init_ignore_album()

    #筛选sound
    
    app.force_init_ignore_sound(True)
    
    # app.continue_download()
    # app.continue_author()
    # app.continue_album()
    app.continue_audio()
    app.run()
    
    



if __name__ == "__main__":
    main()
    # for i in range(30):
    #     main()
    #     time.sleep(120)
    # os.system(f"shutdown /s /t {5}")
    
    exit()


    
    