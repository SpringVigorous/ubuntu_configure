from interact_base import InteractBase,ResultType
from base import ThreadTask
from handle_config import redbook_config
import os
from handle_comment import NoteCommentWriter

from base.except_tools import except_stack
from base.com_decorator import exception_decorator
import json
from redbook_tools import *




    
    
    
class InteractTheme(ThreadTask,InteractBase):
    def __init__(self,input_queue,output_queue,stop_event,out_stop_event,comment_queue,result_type=ResultType.ONLY_NOTE,search_count:int=10):
        super().__init__(input_queue,output_queue=output_queue,stop_event=stop_event,out_stop_event=out_stop_event)
        InteractBase.__init__(self,output_queue,comment_queue,self.task_logger, result_type,next_id_func=next_ignore_ids ,sec_sort_fun=sort_by_y)
        self.comment_queue=comment_queue
        self.search_count=search_count
        
    @exception_decorator()
    def _handle_data(self, theme):
        self.set_theme(theme)

        self.theme_dir=os.path.join(redbook_config.setting.note_path, theme)
        os.makedirs(self.theme_dir, exist_ok=True)

        csvj_writer=NoteCommentWriter(os.path.join( self.theme_dir,f"评论-{theme}.csv"))
        hrefs=self.handle_theme(theme,csvj_writer,self.search_count)
        # if not redbook_config.sync_note_comment and hrefs and  self.result_type.is_only_note:
        #     #下列只是针对 评论部分

        #     self.handle_comment_by_urls(hrefs,csvj_writer)
        # return 

      


