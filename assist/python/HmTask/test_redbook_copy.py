from queue import Queue
from base_task import ThreadTask
import threading
import sys
import time


sys.path.append("..")
sys.path.append(".")

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
                time.sleep(1)
                json_body = f"Interact:{theme} {i}"
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
    def _imp_run_after(self,data):
        self.datas_lst.append(data)
    def _run_after(self):
        if self.datas_lst:
            self.datas_queue.put(self.datas_lst)
        pass
    def handle_data(self, json_body):
        if json_body:
            time.sleep(1)
            data=f"Parse:{json_body}" #处理后获得的数据
            return data
        
        pass


class InputTask(ThreadTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)


    def _imp_run_after(self,data):
        pass
    def _run_after(self):
        pass

class DownLoad(InputTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
    def handle_data(self, data):
        
        time.sleep(1)
        logger.info(f"DownLoad:{data}")
        pass
    


class WriteNotePad(InputTask):

    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
    def handle_data(self, data):
        
        time.sleep(1)
        logger.info(f"WriteNotePad:{data}")
        pass

#以下两个可以并行
class WriteExcel(InputTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
    def handle_data(self, data):
        time.sleep(1)
        logger.info(f"WriteExcel:{data}")
        pass

class WriteWord(InputTask):
    def __init__(self, input_queue,  stop_event=None):
        super().__init__(input_queue=input_queue, stop_event=stop_event)
    def handle_data(self, data):
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
        download=DownLoad(input_queue=data_queue,stop_event=stop_event)
        write_notepad=WriteNotePad(input_queue=data_queue,stop_event=stop_event)
        write_excel=WriteExcel(input_queue=datas_queue,stop_event=stop_event)
        write_word=WriteWord(input_queue=datas_queue,stop_event=stop_event)
        
        
        for theme in themes:
            theme_queue.put(theme)
        
        interact.start()
        download.start()
        write_notepad.start()
        write_word.start()
        write_excel.start()
        
        stop_event.set()
        interact.join()
        theme_queue.join()

        download.join()
        write_notepad.join()
        write_word.join()
        write_excel.join()
        



if __name__ == '__main__':
    lst=[f"item_{i}" for i in range(2)]
    app=App()
    app.run(lst)