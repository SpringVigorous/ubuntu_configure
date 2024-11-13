import queue
import abc
from .base_task import TaskBase
from com_log import logger_helper,UpdateTimeType
from com_decorator import exception_decorator
from except_tools import except_stack
import time

def clear_queue(q):
    while not q.empty():
        try:
            val = q.get_nowait()  # 或者使用 q.get(False)
            q.task_done()
        except queue.Empty:
            break


#非协程任务
class RoutineTask(TaskBase,metaclass=abc.ABCMeta):

    def __init__(self, input_queue, output_queue=None, stop_event=None,out_stop_event=None):
        super().__init__(input_queue, output_queue, stop_event,out_stop_event=out_stop_event)
        #记录已从队列中获取了多少个
        self.input_count=0
    
    @abc.abstractmethod
    def _handle_data(self, data):
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
    
    #出现异常，是否终止
    @abc.abstractmethod
    def _except_to_break(self)->bool:
        return False


    # 单次获取值，处理后，放入输出队列，并执行每个处理后逻辑
    def _imp_run(self):
        if not self.Valid:
            return
        input_data = self._pop_data()
        if input_data is None:
            return
        self.input_count+=1
        output_data = self._handle_data(input_data)
        #过滤掉空，是否合适待商议
        if output_data:
            self._push_data(output_data)
        self._each_run_after(output_data)

    def clear_input(self):
        clear_queue(self.input_queue)
        
    #真正的运行逻辑
    @exception_decorator()
    def run(self):
        while self.Valid:
            try:
                self._imp_run()
            except Exception as e:
                self.task_logger.error("异常",except_stack() )

                if self._except_to_break():
                    if self.InputValid:
                        clear_queue(self.input_queue)
                    break
        self._final_run_after()
        if self.out_stop_event:
            self.out_stop_event.set()
        
    
    def _put(self,data):
        if self.InputValid:
            self.input_queue.put(data)

    @exception_decorator()
    def _pop_data(self):
        if not self.InputValid:
            return None
        
        try:
            data = self.input_queue.get(timeout=1)  # 阻塞等待数据
            if not self.is_input_mutiprocess:
                self.input_queue.task_done()  # 标记数据任务完成
            return data
        except  queue.Empty as e:
            time.sleep(5)
            return None
        #其他的异常，上述装饰器处理

    @exception_decorator()
    def _push_data(self, data):
        if not self.OutputValid:
            return

        self._output_queue.put(data)


