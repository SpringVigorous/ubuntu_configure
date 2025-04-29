import threading
from queue import Queue
from typing import Any, Callable, List, Dict, Optional

class ParallelProcessor:
    """
    多线程任务处理器
    :param worker_func: 处理单个数据的函数，格式应为 func(data) -> result
    :param num_workers: 最大线程数 (默认CPU核心数*2)
    :param max_retries: 单个任务失败重试次数 (默认0不重试)
    :param progress_callback: 进度回调函数 (func(completed, total))
    """
    def __init__(
        self,
        worker_func: Callable[[Any], Any],
        num_workers: int = None,
        max_retries: int = 0,
        progress_callback: Callable[[int, int], None] = None
    ):
        self.worker_func = worker_func
        self.num_workers = num_workers or (threading.active_count() * 2)
        self.max_retries = max_retries
        self.progress_callback = progress_callback
        
        # 运行时状态
        self._task_queue: Queue = Queue()
        self._result_queue: Queue = Queue()
        self._error_records: List[Dict] = []
        self._is_running: bool = False

    def _worker(self) -> None:
        """ 工作线程的核心逻辑 """
        while not self._task_queue.empty() and self._is_running:
            data, attempt = self._task_queue.get()
            
            try:
                result = self.worker_func(data)
                self._result_queue.put((True, data, result))
                if self.progress_callback:
                    self.progress_callback(1, 0)  # +1 completed
            except Exception as e:
                if attempt < self.max_retries:
                    self._task_queue.put((data, attempt + 1))  # 重试
                else:
                    self._error_records.append({
                        "data": data,
                        "exception": e,
                        "attempts": attempt + 1
                    })
                    self._result_queue.put((False, data, None))
            finally:
                self._task_queue.task_done()

    def process(self, data_list: List[Any]) -> List[Any]:
        """
        执行并行处理
        :param data_list: 待处理数据列表
        :return: 按原始顺序排列的结果列表 (失败项为None)
        """
        self._is_running = True
        results = [None] * len(data_list)
        
        # 初始化任务队列 (保留原始顺序索引)
        for idx, data in enumerate(data_list):
            self._task_queue.put(( (idx, data), 0 ))  # (元组数据, 重试次数)

        # 启动线程池
        threads = []
        for _ in range(min(self.num_workers, len(data_list))):
            thread = threading.Thread(target=self._worker)
            thread.start()
            threads.append(thread)

        # 等待任务完成
        self._task_queue.join()
        self._is_running = False

        # 收集结果并还原顺序
        while not self._result_queue.empty():
            success, (idx, data), result = self._result_queue.get()
            results[idx] = result if success else None

        return results

    @property
    def errors(self) -> List[Dict]:
        """ 获取错误记录 """
        return self._error_records

    def reset(self) -> None:
        """ 重置处理器状态 """
        self._task_queue = Queue()
        self._result_queue = Queue()
        self._error_records.clear()