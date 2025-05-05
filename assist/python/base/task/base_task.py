

import multiprocessing
import asyncio

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from com_log import logger_helper,UpdateTimeType
from com_decorator import exception_decorator
from except_tools import except_stack


#生产者-消费者模型(一个输入队列，一个输出队列)
class TaskBase():
    def __init__(self, input_queue, output_queue=None, stop_event=None,out_stop_event=None):
        #结束事件
        self._stop_event = stop_event
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._out_stop_event=out_stop_event
        self._logger=logger_helper("Task","run")
        

    def __del__(self):
        if self.task_logger:
            self.task_logger.trace("析构完成",update_time_type= UpdateTimeType.ALL)
    @property
    def task_logger(self):
        return self._logger
        
    @property
    def Stopped(self)->bool:
        return  not self._stop_event or self._stop_event.is_set()
    
    def Stop(self):
        if self._stop_event:
            self._stop_event.set()
            
    def ReStart(self):
        if self._stop_event:
            self._stop_event.clear()
    
    @property
    def logger(self)->logger_helper:
        return self._logger
    
    @property
    def Valid(self)->bool:
        return not(self.Stopped and self.InputValid and self._input_queue.empty())

    @property
    def InputValid(self)->bool:
        return not self._input_queue is None
    @property
    def OutputValid(self)->bool:
        return not self._output_queue is None

    def __check_queue_type__(self,obj,type):
        return  not obj and isinstance(obj,type)
    def check_input_type(self,type):
        return self.__check_queue_type__(self._input_queue,type)
    def check_output_type(self,type):
        return self.__check_queue_type__(self._output_queue,type)
    @property
    def is_input_coroutine(self):
        return self.check_input_type(asyncio.Queue)
    @property
    def is_output_coroutine(self):    
        return self.check_output_type(asyncio.Queue)
    @property
    def is_input_mutiprocess(self):
        return self.check_input_type(multiprocessing.Queue)
    @property
    def is_output_mutiprocess(self):
        return self.check_output_type(multiprocessing.Queue)

    @property
    def input_queue(self):
        return self._input_queue
    
    @property
    def output_queue(self):
        return self._output_queue
    
    @property
    def stop_event(self):
        return self._stop_event
    
    @property
    def out_stop_event(self):
        return self._out_stop_event
    
    
    def set_input_queue(self,queue):
        self._input_queue=queue

    def set_output_queue(self,queue):
        self._output_queue=queue
    
    def set_stop_event(self,event):
        self._stop_event=event
    
    def set_out_stop_event(self,event):
        self._out_stop_event=event
    

    
    





