import abc
import threading
import sys
from .routine_task import RoutineTask


#线程任务
class ThreadTask(RoutineTask, threading.Thread,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None,out_stop_event=None):
        super().__init__(input_queue, output_queue, stop_event,out_stop_event=out_stop_event)
        threading.Thread.__init__(self)
        
    
    @abc.abstractmethod
    def _handle_data(self, data):
        # 示例同步处理逻辑
        raise NotImplementedError("Subclasses must implement this method")
    
    def _except_to_break(self)->bool:
        return False
    
    def _each_except_after(self,data):    
        pass
    
    def _each_run_after(self,data):

        pass
    
    def _final_run_after(self):

        pass
    
    
class ResultThread(threading.Thread):
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        self._return = None  # 初始化存储返回值的变量

    def run(self):
        if self._target:
            self._return = self._target(*self._args)  # 执行目标函数并保存结果

    def join(self, timeout=None):
        super().join(timeout)  # 调用原生join方法等待线程结束
        return self._return  # 返回结果

    @property
    def result(self):
        return self._return  # 返回结果