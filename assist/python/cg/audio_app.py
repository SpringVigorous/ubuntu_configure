
from audio_thread import *
from audio_kenel import *
from base import exception_decorator,backup_xlsx,unique,envent_sequence,read_from_txt_utf8_sig,audio_root
from audio_manager import AudioManager
class AudioApp():
    def __init__(self) -> None:
        
        self.audio_url_queue=Queue()
        self.bz_url_queue=Queue()
        self.album_url_queue=Queue() 
        
        
        self.bz_stop_envent=threading.Event()#博主所有专辑 停止事件
        album_stop_envent=threading.Event()#专辑所有声音 停止事件
        audio_stop_envent=threading.Event()



        self.interact_bz=InteractBoZhu(self.bz_url_queue,self.album_url_queue,self.bz_stop_envent,album_stop_envent)
        self.interact_album=InteractAlbum(self.album_url_queue,self.audio_url_queue,album_stop_envent,audio_stop_envent)
        self.interact_audio=InteractAudio(self.audio_url_queue,audio_stop_envent)
        
                
        self.interact_bz.start()
        self.interact_album.start()
        self.interact_audio.start()
        
        self.logger=logger_helper(self.__class__.__name__)

        
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
                with self.logger.raii_target(f"添加专辑消息",f"第{self.album_msg_index}：{index+1}个{msg}") as inner_logger:
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
    @exception_decorator(error_state=False)
    def continue_audio_impl(self,xlsx_path,sheet_name):
        
        df=self.manager.get_df(xlsx_path,sheet_name)
        if df_empty(df):
            return
        
        
        self.manager.cache_album_df(xlsx_path,sheet_name,df)
        cur_df=df[df[downloaded_id]!=TaskStatus.SUCCESS.value]
        if df_empty(cur_df):
            return
        
        msg_lst=[]
        for index,row in cur_df.iterrows():
            status=TaskStatus.from_value( row[downloaded_id])
            if status.is_temp_canceled:
               cur_df.loc[index,downloaded_id] =status.clear_temp_canceled.value
            if msg:=row_path_to_msg(row,xlsx_path,sheet_name):
                msg_lst.append(msg)
        return msg_lst
    @exception_decorator(error_state=False)
    def continue_author(self):
        xlsx_path,name,catalog_df=self.manager.catalog_df
        if df_empty(catalog_df) :
            return
        self.logger.update_time(UpdateTimeType.STAGE)
        
        
        for _,catalog_row in catalog_df.iterrows():
            author_path= catalog_row[local_path_id]
            author_status=TaskStatus.from_value(catalog_row[downloaded_id])
            if not author_status.can_download:
                continue
            
            if url:=catalog_row[href_id]:
                self.add_bz_msg(url)

            
            
            


    @exception_decorator(error_state=False)
    def continue_album(self):
        catalog_xlsx_path,catalog_name,catalog_df=self.manager.catalog_df
        if df_empty(catalog_df) :
            return
        self.logger.update_time(UpdateTimeType.STAGE)
        
        msg_lst=[]
        for _,catalog_row in catalog_df.iterrows():
            author_path= catalog_row[local_path_id]
            author_status=TaskStatus.from_value(catalog_row[downloaded_id])
            # if not author_status.can_download:
            #     continue
            
            author_df=self.manager.get_df(author_path,album_id)
            if df_empty(author_df) :
                continue
            self.manager.cache_author_df(author_path,album_id,author_df)
            for author_index,author_row in author_df.iterrows():
                album_path= author_row[local_path_id]
                if not isinstance(album_path,str) or not album_path:
                    continue
                
                album_status=TaskStatus.from_value(author_row[downloaded_id]).clear_temp_canceled.clear_error
                if not album_status.can_download:
                    continue              
                msg={
                    href_id:author_row[href_id],
                    local_path_id:album_path,
                    title_id:author_row[title_id],
                    
                    parent_xlsx_path_id:author_path,
                    parent_sheet_name_id:album_id,

                    
                }
                if album_name:=author_row.get(album_id,None):
                    msg[album_id]=album_name
                
                
                msg_lst.append(msg)

        if not msg_lst:
            return 
        
        self.add_album_msg(msg_lst)
        
    @exception_decorator(error_state=False)
    def continue_audio(self):
        
        xlsx_path,name,catalog_df=self.manager.catalog_df
        if df_empty(catalog_df) :
            return
        self.logger.update_time(UpdateTimeType.STAGE)
        
        msg_lst=[]
        for _,catalog_row in catalog_df.iterrows():
            author_path= catalog_row[local_path_id]
            author_status=TaskStatus.from_value(catalog_row[downloaded_id])
            if not author_status.can_download:
                continue
            
            author_df=self.manager.get_df(author_path,album_id)
            if df_empty(author_df) :
                continue
            self.manager.cache_author_df(author_path,album_id,author_df)
            for author_index,author_row in author_df.iterrows():
                album_path= author_row[local_path_id]
                if not isinstance(album_path,str) or not album_path:
                    continue
                
                album_status=TaskStatus.from_value(author_row[downloaded_id])
                if not album_status.can_download:
                    continue
                #修正路径问题（遗留+）
                cur_path=Path(album_path)
                if cur_path.stem.replace("_album","")==cur_path.parent.stem:
                    album_path=str(cur_path.parent.parent /cur_path.name)
                    author_df.loc[author_index,local_path_id]=album_path

                if lst:=self.continue_audio_impl(album_path,audio_sheet_name):
                    msg_lst.extend(lst)

        if not msg_lst:
            return 
        
        
        self.add_audio_msg(msg_lst)
        



    def run(self):
        self.bz_stop_envent.set()


        self.bz_url_queue.join()
        self.album_url_queue.join()
        self.audio_url_queue.join()
        
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
        "https://www.ximalaya.com/zhubo/6460629",
        "https://www.ximalaya.com/zhubo/90400568",
        "https://www.ximalaya.com/zhubo/62273426",
        "https://www.ximalaya.com/zhubo/67632526",
        "https://www.ximalaya.com/zhubo/52023510",
        "https://www.ximalaya.com/zhubo/163605621",

             ]
    # app.add_bz_url(bz_urls)
    # app.add_bz_url(bz_urls)
    # app.add_audio_url(msgs_from_xlsx(xlsx_path,sheet_name))
    #筛选album
    # app.force_init_ignore_album()
    
    #筛选sound
    app.force_init_ignore_sound(True)
    # app.continue_author()
    app.continue_album()
    # app.continue_audio()
    app.run()
    
    



if __name__ == "__main__":
    main()
    # os.system(f"shutdown /s /t {5}")
    
    exit()


    
    