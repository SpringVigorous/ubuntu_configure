import abc
import multiprocessing
from .routine_task import RoutineTask


#进程任务
class ProcessTask(RoutineTask, multiprocessing.Process,metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue=None, stop_event=None):
        super().__init__(input_queue, output_queue, stop_event)
        multiprocessing.Process.__init__(self)
    @abc.abstractmethod
    def _handle_data(self, data):
        # 示例同步处理逻辑
        raise NotImplementedError("Subclasses must implement this method")
