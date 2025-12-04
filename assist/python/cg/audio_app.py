
from audio_thread import *
from audio_kenel import *
from base import exception_decorator,backup_xlsx,unique,envent_sequence,read_from_txt_utf8_sig,audio_root
from audio_manager import AudioManager
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
        
        
        self.author_msg_index:int=0
        self.album_msg_index:int=0
        self.audio_msg_index:int=0
        
    @exception_decorator(error_state=False)
    def add_bz_msg(self,urls:str|list[str]):
        if not urls: return
        
        self.author_msg_index+=1
        
        if isinstance(urls,str):
            urls=[urls]
        for index,url in enumerate(urls):
            with self.logger.raii_target(f"添加博主消息",f"第{self.author_msg_index}：{index+1}个{url}") as logger:
                self.bz_url_queue.put(url)

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
        if not msg_lst: return
        self.album_msg_index+=1
        if isinstance(msg_lst,dict):
            msg_lst=[msg_lst]
            
        self.logger.update_time(UpdateTimeType.STAGE)
        with self.logger.raii_target(f"添加专辑消息",f"第{self.album_msg_index}：共{len(msg_lst)}个") as outer_logger:
            for index,msg in enumerate(msg_lst):
                with self.logger.raii_target(detail=f"第{self.album_msg_index}：{index+1}个{msg}") as inner_logger:
                    self.album_url_queue.put(msg)
                    inner_logger.trace("成功",update_time_type=UpdateTimeType.STEP)
            outer_logger.info("成功",update_time_type=UpdateTimeType.STAGE)
            
        
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
        if not msg_lst: return
        self.audio_msg_index+=1
        
        if isinstance(msg_lst,dict):
            msg_lst=[msg_lst]
        
        for index,msg in enumerate(msg_lst):
            with self.logger.raii_target(f"添加音频消息",f"第{self.audio_msg_index}：{index+1}个{msg}") as logger:
                self.audio_url_queue.put(msg)
                logger.trace("成功","加入下载队")
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
        urls=list(filter(lambda x:x ,catalog_df[href_id]))
        
        self.logger.update_time(UpdateTimeType.STAGE)
        with self.logger.raii_target("添加Author消息",f"共{len(urls)}个") as logger:
            for index,url in enumerate(urls):
                self.add_bz_msg(url)
                logger.trace("成功",f"第{index}个：{url}")

            logger.trace("成功",update_time_type=UpdateTimeType.STAGE)
            
            
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
    # os.system(f"shutdown /s /t {5}")
    
    exit()


    
    