
from audio_thread import *
from audio_kenel import *
from base import exception_decorator,backup_xlsx,unique,envent_sequence,read_from_txt_utf8_sig
from audio_manager import AudioManager
class AudioApp():
    def __init__(self) -> None:
        self.bz_url_queue=Queue()
        self.audio_url_queue=Queue()
        
        self.album_url_queue=Queue()
        self.sound_from_album_queue=Queue() 
        
        #博主所有声音 停止时间
        self.bz_stop_envent=threading.Event()
        #专辑所有声音 停止时间
        self.album_stop_envent=threading.Event()

        bz_latter_stop_envent=threading.Event()
        album_latter_stop_envent=threading.Event()
        sound_stop_envent=threading.Event()
        audio_stop_envent=envent_sequence([bz_latter_stop_envent,sound_stop_envent])

        self.interact_bz=InteractBoZhu(self.bz_url_queue,self.audio_url_queue,self.bz_stop_envent,bz_latter_stop_envent)
        self.interact_album=InteractAlbum(self.album_url_queue,self.sound_from_album_queue,self.album_stop_envent,album_latter_stop_envent)
        self.interact_album_sound=InteractSoundFromAlbum(self.sound_from_album_queue,self.audio_url_queue,album_latter_stop_envent,sound_stop_envent)
        self.interact_audio=InteractAudio(self.audio_url_queue,audio_stop_envent)
        
                
        self.interact_bz.start()
        self.interact_audio.start()
        self.interact_album.start()
        self.interact_album_sound.start()
        
        self.logger=logger_helper(self.__class__.__name__)
        
        self._audio_xlsx_lsts=[]
        self._album_xlsx_lsts=[]
        
        
        self.manager=AudioManager()
        
    @exception_decorator(error_state=False)
    def add_bz_url(self,urls:str|list[str]):
        if isinstance(urls,str):
            urls=[urls]
        for index,url in enumerate(urls):
            with self.logger.raii_target(f"添加博主消息",f"第{index+1}个{url}") as logger:
                self.bz_url_queue.put(url)

    @exception_decorator(error_state=False)
    def add_album_url(self,urls:str|list[str]):
        if isinstance(urls,str):
            urls=[urls]
        for index,url in enumerate(urls):
            with self.logger.raii_target(f"添加专辑消息",f"第{index+1}个{url}") as logger:
                self.album_url_queue.put(url)
        
    @exception_decorator(error_state=False)
    def add_audio_url(self,urls:dict|list[dict]):   
        if isinstance(urls,dict):
            urls=[urls]
        
        for index,url in enumerate(urls):
            with self.logger.raii_target(f"添加音频消息",f"第{index+1}个{url}") as logger:
                self.audio_url_queue.put(url)
                logger.trace("成功","加入下载队")
    @exception_decorator(error_state=False)
    def continue_audio(self,xlsx_path,sheet_name):
        
        df=self.manager.get_df(xlsx_path,sheet_name)
        self.manager.cache_audio_df(xlsx_path,sheet_name,df)
        cur_df=df[df[downloaded_id]!=TaskStatus.SUCCESS]
        if df_empty(cur_df):
            return
        
        msg_lst=[]
        for _,row in cur_df.iterrows():
            msg_lst.append(row_path_to_msg(row,xlsx_path,sheet_name))
        if msg_lst:
            self.add_audio_url(msg_lst)
            self._audio_xlsx_lsts.append((xlsx_path,sheet_name))
            
    def add_audio_xlsx(self,xlsx_lst):
        if xlsx_lst:
            self._audio_xlsx_lsts.extend(xlsx_lst)
            self._audio_xlsx_lsts=unique(self._audio_xlsx_lsts)
    def add_album_xlsx(self,xlsx_lst):
        if xlsx_lst:
            self._album_xlsx_lsts.extend(xlsx_lst)
            self._album_xlsx_lsts=unique(self._album_xlsx_lsts)
    def run(self):
        self.bz_stop_envent.set()
        self.album_stop_envent.set()
        
        self.bz_url_queue.join()
        self.album_url_queue.join()
        self.sound_from_album_queue.join()
        self.audio_url_queue.join()
        
        self.interact_bz.join()
        self.interact_album.join()
        self.interact_album_sound.join()
        self.interact_audio.join()
        
        
        # fail_df= pd.DataFrame(self.interact_audio.fail_param_lst)
        # buy_df= pd.DataFrame(self.interact_audio.buy_param_lst)
    


        # self.add_audio_xlsx(self.interact_bz._xlsx_lsts)
        # self.add_audio_xlsx(self.interact_album_sound._xlsx_lsts)
        # self.add_album_xlsx(self.interact_album._xlsx_lsts)
        
        #保存xlsx
        self.save_xlsx()
        self.logger.info("结束",update_time_type=UpdateTimeType.ALL)
        
    @exception_decorator(error_state=False)
    def save_xlsx(self):


        #保存前，更新专辑信息
        for xlsx_path,sheet_name,df in self.manager.album_dfs:
            df=self.manager.update_album_df(df)
            self.manager.cache_df(xlsx_path,sheet_name,df)
        self.manager.save()


def main():
    
    
    app:AudioApp= AudioApp()

    bz_urls=[
        "https://www.ximalaya.com/zhubo/51763868",
             ]
    app.add_album_url(bz_urls)
    # app.add_bz_url(bz_urls)
    # app.add_audio_url(msgs_from_xlsx(xlsx_path,sheet_name))
    
    # app.continue_audio(r"E:\旭尧\有声读物\宝宝巴士.xlsx",audio_sheet_name)
    # app.continue_audio(r"E:\旭尧\有声读物\米小圈.xlsx",audio_sheet_name)
    app.run()
    
    



if __name__ == "__main__":
    main()
    # os.system(f"shutdown /s /t {5}")
    
    exit()
    xmlx_path=r"E:\旭尧\有声读物\晓北姐姐讲故事.xlsx"
    sheet_name=audio_sheet_name
    log_path=r"F:\worm_practice\logs\xmly_thread\xmly_thread-trace.log.2025-11-11.log"
    
    
    
    html_path=Path(xmlx_path).with_suffix(".html")
    html_content=read_from_txt_utf8(html_path)
    #博主所有的音频
    df=sound_lst_from_author_content(html_content)
    df.to_excel(xmlx_path,sheet_name=sheet_name,index=False)
    
    

    
    
    
    
    

    pass
    
    