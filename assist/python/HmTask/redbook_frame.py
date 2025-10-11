from queue import Queue
from base.task import ThreadTask
import threading
import sys
import time





from __init__ import *
from base.com_log import logger as logger
from base import setting as setting


# from tools import *




        

class Interact(threading.Thread):
    def __init__(self, theme_queue:Queue, datas_queue:Queue, data_queue:Queue):
        super().__init__()
        self.theme_queue = theme_queue
        self.datas_queue = datas_queue
        self.data_queue = data_queue

    def run(self):
        while not self.theme_queue.empty():
            theme = self.theme_queue.get()
            json_queue = Queue()
            
            stop_event = threading.Event()
            parse = Parse(json_queue, output_queue=self.data_queue, datas_queue=self.datas_queue, stop_event=stop_event)
            parse.start()
            count = 20
            i = 0
            while i < count:
                time.sleep(0.5)
                json_body = f"Interact:{theme} {i}"
                logger.debug(f"json_queue即将加入:{json_body}")
                
                
                json_queue.put(json_body)
                i += 1
                
            stop_event.set()
            parse.join()
            
            self.theme_queue.task_done()




class Parse(ThreadTask):
    def __init__(self, input_queue, output_queue=None,datas_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
        self.datas_queue=datas_queue
        self.stop_event=stop_event
        self.datas_lst=[]
    def _each_run_after(self,data):
        self.datas_lst.append(data)
    def _final_run_after(self):
        if self.datas_lst:
            self.datas_queue.put(self.datas_lst)
        pass
    def _handle_data(self, json_body):
        if json_body:
            time.sleep(0.1)
            data=f"Parse:{json_body}" #处理后获得的数据
            logger.debug(f"handle_data:{data}")
            return data
        
        pass


class InputTask(ThreadTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)


    def _each_run_after(self,data):
        pass
    def _final_run_after(self):
        pass

class HandleNote(InputTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
    def _handle_data(self, data):
        
        time.sleep(0.7)
        logger.info(f"DownLoad:{data}")
        time.sleep(0.1)
        logger.info(f"WriteNotePad:{data}")
        pass
    



#以下两个可以并行
class HandleTheme(InputTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
    def _handle_data(self, data):
        time.sleep(1)
        logger.info(f"WriteExcel:{data}")
        time.sleep(1)
        logger.info(f"WriteWord:{data}")
        pass





class App:
    def __init__(self) :
        
        pass
        

    def run(self,themes:list):
        theme_queue=Queue()
        data_queue=Queue()
        datas_queue=Queue()       
        stop_event=threading.Event()
        
        interact=Interact(theme_queue=theme_queue,datas_queue=datas_queue,data_queue=data_queue)
        handle_note=HandleNote(input_queue=data_queue,stop_event=stop_event)

        handle_theme=HandleTheme(input_queue=datas_queue,stop_event=stop_event)

        
        
        for theme in themes:
            theme_queue.put(theme)
        
        interact.start()
        handle_note.start()

        handle_theme.start()
        
        interact.join()
        stop_event.set()
        
        theme_queue.join()

        handle_note.join()

        handle_theme.join()
        



if __name__ == '__main__':
    lst=[f"item_{i}" for i in range(10)]
    app=App()
    app.run(lst)