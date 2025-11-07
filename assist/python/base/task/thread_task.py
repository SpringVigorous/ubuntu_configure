import abc
import threading
import sys
from .routine_task import RoutineTask

class envent_sequence:
    def __init__(self):
        self._thread_event:list[threading.Event]=[]
        
    def add_envent(self,event:threading.Event):
        if not event or (event in self._thread_event):
            return
        self._thread_event.append(event)
        
    def set(self):
        for event in self._thread_event:
            event.set()

    def clear(self):
        for event in self._thread_event:
            event.clear()
            
    def is_set(self)->bool:
        return all(event.is_set() for event in self._thread_event)

#线程任务
class ThreadTask(RoutineTask, threading.Thread,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None,out_stop_event=None):
        super().__init__(input_queue, output_queue, stop_event,out_stop_event=out_stop_event)
        threading.Thread.__init__(self)
        
    def set_thread_name(self,name:str):
        threading.Thread.setName(self,name)
    @property
    def thread_name(self)->str:
        return threading.Thread.getName(self)
    
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