import abc
import threading
import multiprocessing
import queue
import asyncio
import time
# multiprocessing.Queue 、queue.Queue、asyncio.Queue


import sys
sys.path.append("..")
sys.path.append(".")

from __init__ import *
from base.com_log import logger ,record_detail

def asRoutinetask(func,*args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    restult = loop.run_until_complete(func(*args, **kwargs))
    loop.close()
    return restult
    
async def asCoroutine(func,*args, **kwargs):
    await asyncio.sleep(.1)
    return func(*args, **kwargs)
    


class BaseTask():
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        #结束事件
        self.stop_event = stop_event
        self.input_queue = input_queue
        self.output_queue = output_queue
    @property
    def Stopped(self)->bool:
        return  not self.stop_event or self.stop_event.is_set()
    
    def Stop(self):
        if self.stop_event:
            self.stop_event.set()
    
    @property
    def Valid(self)->bool:
        return not(self.Stopped and self.InputValid and self.input_queue.empty())

    @property
    def InputValid(self)->bool:
        return not self.input_queue is None
    @property
    def OutputValid(self)->bool:
        return not self.output_queue is None

    def __check_queue_type__(self,obj,type):
        return  not obj and isinstance(obj,type)
    def check_input_type(self,type):
        return self.__check_queue_type__(self.input_queue,type)
    def check_output_type(self,type):
        return self.__check_queue_type__(self.output_queue,type)
    @property
    def input_coroutine(self):
        return self.check_input_type(asyncio.Queue)
    @property
    def output_coroutine(self):    
        return self.check_output_type(asyncio.Queue)
    @property
    def input_mutiprocess(self):
        return self.check_input_type(multiprocessing.Queue)
    @property
    def output_mutiprocess(self):
        return self.check_output_type(multiprocessing.Queue)

    @property
    def InputQueue(self):
        return self.input_queue
    
    @property
    def OutputQueue(self):
        return self.output_queue
    
def clear_queue(q):
    while not q.empty():
        try:
            val = q.get_nowait()  # 或者使用 q.get(False)
            q.task_done()
        except queue.Empty:
            break
    
class RoutineTask(BaseTask,metaclass=abc.ABCMeta):

    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)

    @abc.abstractmethod
    def handle_data(self, data):
        raise NotImplementedError("Subclasses must implement this method")
    
    
    @abc.abstractmethod
    def _each_run_after(self,data):
        pass
        
    @abc.abstractmethod
    def _final_run_after(self):
        pass
    
    @abc.abstractmethod
    def _each_except_after(self,data):    
        pass
    
    #是否break循环
    @abc.abstractmethod
    def final_except(self)->bool:
        return False
        pass

    def _imp_run(self):
        if not self.Valid:
            return
        input_data = self.pop_data()
        if input_data is None:
            return
        output_data = self.handle_data(input_data)
        #过滤掉空，是否合适待商议
        if output_data:
            self.push_data(output_data)
        self._each_run_after(output_data)

        
    def run(self):
        while self.Valid:
            try:
                self._imp_run()
            except Exception as e:
                logger.error(record_detail("处理数据","异常",f"{e}") )
                if self.final_except():
                    if self.InputValid:
                        clear_queue(self.input_queue)
                    break
        self._final_run_after()
    
    def put(self,data):
        if self.InputValid:
            self.input_queue.put(data)

    def pop_data(self):
        if not self.InputValid:
            return None
        
        try:
            data = self.input_queue.get(timeout=1)  # 阻塞等待数据
            if not self.input_mutiprocess:
                self.input_queue.task_done()  # 标记数据任务完成

            return data
        except  queue.Empty as e:
            # logger.trace(record_detail("获取数据","异常",未找到数据) )
            time.sleep(5)
            return None
        except Exception as e:
            logger.error(record_detail("获取数据","异常",f"{e}") )
            return None

    def push_data(self, data):
        if not self.OutputValid:
            return
        
        try:
            self.output_queue.put(data)
        except Exception as e:
            logger.error(record_detail("输出数据","异常",f"{e}") )

class CoroutineTask(BaseTask,metaclass=abc.ABCMeta):
    
    
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
    @abc.abstractmethod
    async def handle_data(self, data):
        raise NotImplementedError("Subclasses must implement this method")

    async def _imp_run(self):
            
        input_data = await self.pop_data() 
        if input_data is None:
            return
        output_data = await self.handle_data(input_data) 

        await self.push_data(output_data)


    async def run(self):
        while not self.stop_event.is_set() or not self.input_queue.empty():
            try:
                await self._imp_run()
            except Exception as e:
                logger.error(record_detail("处理数据","异常",f"{e}") )
    async def put(self,data):
        if self.input_coroutine:
            await self.input_queue.put(data)
        else:
            self.input_queue.put(data)
            await asyncio.sleep(.1)
    async def pop_data(self):
        try:
            data = (await self.input_queue.get() )if self.input_coroutine else self.input_queue.get(timeout=1)  # 阻塞等待数据
            if not self.input_mutiprocess:
                self.input_queue.task_done()  # 标记数据任务完成
            return data
        except Exception as e:
            logger.error(record_detail("获取数据","异常",f"{e}") )
            return None

    async def push_data(self, data):
        try:
            (await self.output_queue.put(data)) if self.output_coroutine else self.output_queue.put(data)
        except Exception as e:
            logger.error(record_detail("输出数据","异常",f"{e}") )



class ThreadTask(RoutineTask, threading.Thread,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
        threading.Thread.__init__(self)
        
    @abc.abstractmethod
    def handle_data(self, data):
        # 示例同步处理逻辑
        raise NotImplementedError("Subclasses must implement this method")

    def _each_run_after(self,data):
        pass


    def _final_run_after(self):
        pass
    
    def final_except(self)->bool:
        return False
    
    def _each_except_after(self,data):    
        pass
    
    def _each_run_after(self,data):

        pass
    
    def _final_run_after(self):

        pass

class ProcessTask(RoutineTask, multiprocessing.Process,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
        multiprocessing.Process.__init__(self)
    @abc.abstractmethod
    def handle_data(self, data):
        # 示例同步处理逻辑
        raise NotImplementedError("Subclasses must implement this method")


