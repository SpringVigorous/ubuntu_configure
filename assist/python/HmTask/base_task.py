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
from base.com_log import logger as logger

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
    def stop(self):
        return  not self.stop_event or self.stop_event.is_set()
    @property
    def alive(self):
        return not(self.stop and  self.input_queue.empty())

    @property
    def IsInputNone(self):
        return not self.input_queue
    @property
    def IsOutputNone(self):
        return not self.output_queue

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
    
    
class RoutineTask(BaseTask,metaclass=abc.ABCMeta):

    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)

    @abc.abstractmethod
    def handle_data(self, data):
        raise NotImplementedError("Subclasses must implement this method")
    
    
    @abc.abstractmethod
    def _imp_run_after(self,data):
        pass
        
    @abc.abstractmethod
    def _run_after(self):
        pass

    def _imp_run(self):
        if not self.alive:
            return
        input_data = self.pop_data()
        if input_data is None:
            return
        output_data = self.handle_data(input_data)
        if output_data:
            self.push_data(output_data)
        self._imp_run_after(output_data)
    def run(self):
        while self.alive:
            try:
                self._imp_run()
            except Exception as e:
                logger.error(f"处理数据时发生异常: {e}")
        self._run_after()
    
    def put(self,data):
        self.input_queue.put(data)

    def pop_data(self):
        
        try:
            data = self.input_queue.get(timeout=1)  # 阻塞等待数据
            if not self.input_mutiprocess:
                self.input_queue.task_done()  # 标记数据任务完成

            return data
        except  queue.Empty as e:
            # logger.trace("未获取到数据")
            time.sleep(5)
            return None
        except Exception as e:
            logger.error(f"获取输入数据时发生异常: {e}")
            return None

    def push_data(self, data):
        try:
            self.output_queue.put(data)
        except Exception as e:
            logger.error(f"输出数据时发生异常: {e}")

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
                logger.error(f"处理数据时发生异常: {e}")
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
            logger.error(f"获取输入数据时发生异常: {e}")
            return None

    async def push_data(self, data):
        try:
            (await self.output_queue.put(data)) if self.output_coroutine else self.output_queue.put(data)
        except Exception as e:
            logger.error(f"输出数据时发生异常: {e}")



class ThreadTask(RoutineTask, threading.Thread,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
        threading.Thread.__init__(self)
    @abc.abstractmethod
    def handle_data(self, data):
        # 示例同步处理逻辑
        raise NotImplementedError("Subclasses must implement this method")

class ProcessTask(RoutineTask, multiprocessing.Process,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
        multiprocessing.Process.__init__(self)
    @abc.abstractmethod
    def handle_data(self, data):
        # 示例同步处理逻辑
        raise NotImplementedError("Subclasses must implement this method")


