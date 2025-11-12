
from audio_thread import *
from audio_kenel import *
from base import exception_decorator,backup_xlsx,unique

class AudioApp():
    def __init__(self) -> None:
        self.bz_url_queue=Queue()
        self.audio_url_queue=Queue()
        
        self.bz_stop_envent=threading.Event()
        audio_stop_envent=threading.Event()

        self.interact_bz=InteractBoZhu(self.bz_url_queue,self.audio_url_queue,self.bz_stop_envent,audio_stop_envent)
        self.interact_audio=InteractAudio(self.audio_url_queue,audio_stop_envent)
                
        self.interact_bz.start()
        self.interact_audio.start()
        
        self.logger=logger_helper(self.__class__.__name__)
        
        self._xlsx_lsts=[]
        
        
    @exception_decorator(error_state=False)
    def add_bz_url(self,urls:str|list[str]):
        if isinstance(urls,str):
            urls=[urls]
        for index,url in enumerate(urls):
            with self.logger.raii_target(f"添加博主消息",f"第{index+1}个{url}") as logger:
                self.bz_url_queue.put(url)

        
        
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
        if msg_lst:= msgs_from_xlsx(xlsx_path,sheet_name):
            self.add_audio_url(msg_lst)
            self._xlsx_lsts.append((xlsx_path,sheet_name))
            

    def run(self):
        self.bz_stop_envent.set()
        self.bz_url_queue.join()
        self.audio_url_queue.join()
        
        
        self.interact_bz.join()
        self.interact_audio.join()
        
        
        fail_df= pd.DataFrame(self.interact_audio.fail_param_lst)
        buy_df= pd.DataFrame(self.interact_audio.buy_param_lst)

        if xlsx_lst:=self.interact_bz._xlsx_lsts:
            self._xlsx_lsts.extend(xlsx_lst)
            self._xlsx_lsts=unique(self._xlsx_lsts)
        

        #保存xlsx
        self.save_xlsx()
        self.logger.info("结束",update_time_type=UpdateTimeType.ALL)
        
    @exception_decorator(error_state=False)
    def save_xlsx(self):
        for xlsx_path,sheet_name in self._xlsx_lsts:
            df=pd.read_excel(xlsx_path,sheet_name=sheet_name)
            if df_empty(df):
                return
            if dest_path:=backup_xlsx(xlsx_path,update_df(df),sheet_name):
                self.logger.info(f"保存成功:{dest_path}")
            else:
                self.logger.error("保存失败")

            


def msgs_from_xlsx(xlsx_path,sheet_name):
    cur_path=Path(xlsx_path)
    dest_root=audio_root/cur_path.stem
    
    df:pd.DataFrame=pd.read_excel(xlsx_path,sheet_name=sheet_name)
    df=update_df(df,dest_root)
    results=df.to_dict(orient="records")
    msgs=[]
    for row in results:
        if (msg:=row_dict_to_msg(row)):
            msgs.append(msg)
    
    return msgs

def msgs_from_log(log_file):
    content=read_from_txt_utf8_sig(log_file)
    pattern=r"InteractUrl-【第\d+个消息】-【失败】详情：(.*?)->(.*?),"
    
    matches=re.findall(pattern,content)
    msg_lst=[]
    for match in matches:
        if not match:
            continue
        url,file_path=match
        msg={url_id:url,dest_path_id:file_path}
        msg_lst.append(msg)
        
    return msg_lst
    

def main():
    
    
    app:AudioApp= AudioApp()

    bz_urls=[
        "https://www.ximalaya.com/zhubo/68394601",
             ]
    # app.add_bz_url(bz_urls)
    # app.add_audio_url(msgs_from_xlsx(xlsx_path,sheet_name))
    
    app.continue_audio(r"E:\旭尧\有声读物\宝宝巴士.xlsx","audio")
    # app.continue_audio(r"E:\旭尧\有声读物\米小圈.xlsx","audio")
    app.run()
    
    



if __name__ == "__main__":
    main()
    # os.system(f"shutdown /s /t {5}")
    
    exit()
    xmlx_path=r"E:\旭尧\有声读物\晓北姐姐讲故事.xlsx"
    sheet_name="audio"
    log_path=r"F:\worm_practice\logs\xmly_thread\xmly_thread-trace.log.2025-11-11.log"
    
    
    
    html_path=Path(xmlx_path).with_suffix(".html")
    html_content=read_from_txt_utf8(html_path)
    #博主所有的音频
    df=get_album_lst_from_content(html_content)
    df.to_excel(xmlx_path,sheet_name=sheet_name,index=False)
    
    
    # msg_lst= msgs_from_log(log_path)
    # msg_lst=msgs_from_xlsx(xmlx_path,sheet_name)
    # pd.json_normalize(msg_lst).to_excel(log_path.replace(".log",".xlsx"),index=False)
    
    
    
    
    
    
    

    pass
    
    