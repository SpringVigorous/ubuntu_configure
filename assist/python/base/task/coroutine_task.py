import abc
import asyncio
from .base_task import TaskBase
from com_log import logger_helper,UpdateTimeType
from com_decorator import exception_decorator
from except_tools import except_stack


#协程任务
class CoroutineTask(TaskBase,metaclass=abc.ABCMeta):
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
        while not self._stop_event.is_set() or not self.input_queue.empty():
            try:
                await self._imp_run()
            except Exception as e:
                self.task_logger.error("异常",except_stack() )
    async def put(self,data):
        if self.is_input_coroutine:
            await self.input_queue.put(data)
        else:
            self.input_queue.put(data)
            await asyncio.sleep(.1)
    @exception_decorator()
    async def pop_data(self):
            data = (await self.input_queue.get() )if self.is_input_coroutine else self.input_queue.get(timeout=1)  # 阻塞等待数据
            if not self.is_input_mutiprocess:
                self.input_queue.task_done()  # 标记数据任务完成
            return data


    @exception_decorator()
    async def push_data(self, data):
        if self.is_output_coroutine:
            (await self._output_queue.put(data)) if self.is_output_coroutine else self._output_queue.put(data)


