from handle_config import redbook_setting,sync_note_comment
import os
from handle_comment import NoteCommentWriter
from interact_base import InteractBase,ResultType
from base import ThreadTask
from base import  logger_helper,UpdateTimeType
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base import ReturnState

from redbook_tools import next_equal_ids,no_sort


class InteractUrl(ThreadTask,InteractBase):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event,comment_queue,result_type=ResultType.ONLY_NOTE,theme="note"):

        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_event,out_stop_event=out_stop_event)  
        InteractBase.__init__(self,output_queue,comment_queue,self.task_logger,result_type,next_id_func=next_equal_ids ,sec_sort_fun=no_sort)
        self.set_theme(theme)
        self.theme_dir=os.path.join(redbook_setting.note_path, self.theme)
        os.makedirs(self.theme_dir, exist_ok=True)
        self.csvj_writer=NoteCommentWriter(os.path.join( self.theme_dir,f"评论-{theme}.csv"))        
        

    @exception_decorator()
    def _handle_data(self, url):
        self.task_logger.update_target("url采集",f" {self.input_count}\t{url}")
        self.task_logger.info("开始")
        if self.result_type.is_only_comment:
            result=ReturnState.from_state(self.handle_comment_by_urls([url],self.csvj_writer))
            if result.is_netExcept:
                ls=[url]
                ls.extend(self.clear_input())
                self.task_logger.error("网络异常",f"清空队列,未完成项:\n{'\n'.join(map(str,ls))}",update_time_type=UpdateTimeType.ALL)
                
                return result
            # self.task_logger.info("完成",update_time_type=UpdateTimeType.ALL)
            return
        
        self.webPage.get(url)
        
        #等待页面更新
        self.webPage.wait.url_change(url)
        title=self.title
        hrefs=self.handle_theme(title,self.csvj_writer,1)
        # if not sync_note_comment and hrefs  and  self.result_type.is_only_note:
        #     self.handle_comment_by_urls(hrefs,self.csvj_writer)
        #     pass
        self.task_logger.info("完成",update_time_type=UpdateTimeType.ALL)
        return 
