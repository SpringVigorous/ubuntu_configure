import multiprocessing as mp
import time
import queue
import threading
from typing import Callable, Any, Tuple, Dict

class DynamicProcessPool:
    """
    动态进程池管理工具类
    
    特点：
    1. 使用队列缓存任务（可调用对象及参数）
    2. 根据任务负载动态调整进程数量
    3. 自动处理空闲进程（长时间空闲则减少进程数量）
    4. 确保至少保留一个进程运行
    5. 支持任务超时监控

    使用示例：
    pool = DynamicProcessPool(min_workers=1, max_workers=5)
    for task in tasks:
        pool.submit(task_function, arg1, arg2, kwarg1=value)
    pool.start()
    pool.shutdown()
    """

    def __init__(self, min_workers: int = 1, max_workers: int = 4, 
                 idle_timeout: float = 30.0, task_timeout: float = 300.0):
        """
        初始化动态进程池
        
        :param min_workers: 最小工作进程数（至少保留1个）
        :param max_workers: 最大工作进程数
        :param idle_timeout: 空闲超时时间（秒），队列空超过此时长则减少进程
        :param task_timeout: 任务超时时间（秒），任务执行超过此时长会被终止
        """
        # 验证参数
        if min_workers < 1:
            raise ValueError("min_workers must be at least 1")
        if max_workers < min_workers:
            raise ValueError("max_workers must be >= min_workers")
        
        # 配置参数
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.idle_timeout = idle_timeout
        self.task_timeout = task_timeout
        
        # 共享状态
        self.task_queue = mp.Queue()                     # 任务队列
        self.result_queue = mp.Queue()                   # 结果队列
        self.active_workers = mp.Value('i', 0)           # 活跃工作进程数
        self.running = mp.Value('b', False)              # 池运行状态
        self.shutdown_event = mp.Event()                 # 关闭事件
        self.adjustment_lock = mp.Lock()                 # 进程调整锁
        self.last_activity_time = mp.Value('d', time.time())  # 最后活动时间
        
        # 本地状态
        self.processes = []                              # 工作进程列表
        self.monitor_thread = None                       # 监控线程

    def submit(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        提交任务到队列
        
        :param func: 可调用对象
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        if not self.running.value:
            raise RuntimeError("Pool must be started before submitting tasks")
        
        # 记录最后活动时间
        with self.last_activity_time.get_lock():
            self.last_activity_time.value = time.time()
        
        self.task_queue.put((func, args, kwargs))
        
        # 动态增加进程（如果任务积压且未达最大进程数）
        with self.adjustment_lock:
            if self.active_workers.value < self.max_workers:
                current_queue_size = self.task_queue.qsize()
                if current_queue_size > self.active_workers.value * 2:
                    self._add_worker()

    def start(self) -> None:
        """启动进程池"""
        if self.running.value:
            return
        
        self.running.value = True
        self.shutdown_event.clear()
        
        # 启动初始工作进程
        for _ in range(self.min_workers):
            self._add_worker()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._monitor_pool, 
            daemon=True
        )
        self.monitor_thread.start()

    def shutdown(self, wait: bool = True) -> None:
        """关闭进程池"""
        if not self.running.value:
            return
        
        # 设置关闭标志
        self.running.value = False
        self.shutdown_event.set()
        
        # 等待监控线程结束
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        # 等待工作进程结束
        if wait:
            for p in self.processes:
                if p.is_alive():
                    p.join(timeout=2.0)
                
                # 强制终止未响应的进程
                if p.is_alive():
                    p.terminate()
        
        # 清理队列
        self._clear_queue(self.task_queue)
        self._clear_queue(self.result_queue)
        
        # 重置状态
        self.processes = []
        self.active_workers.value = 0

    def _add_worker(self) -> None:
        """添加一个新的工作进程"""
        if self.active_workers.value >= self.max_workers:
            return
        
        p = mp.Process(
            target=self._worker_loop,
            daemon=True
        )
        p.start()
        self.processes.append(p)
        with self.active_workers.get_lock():
            self.active_workers.value += 1
    
    def _remove_worker(self) -> None:
        """减少一个工作进程"""
        if self.active_workers.value <= self.min_workers:
            return
        
        # 在任务中标记移除请求
        self.task_queue.put(("REMOVE_WORKER", (), {}))
        
        with self.active_workers.get_lock():
            if self.active_workers.value > self.min_workers:
                self.active_workers.value -= 1

    def _worker_loop(self) -> None:
        """工作进程主循环"""
        while not self.shutdown_event.is_set():
            try:
                # 设置获取任务的超时时间
                task_item = self.task_queue.get(timeout=1.0)
                
                # 检查是否收到移除指令
                if task_item[0] == "REMOVE_WORKER":
                    break
                
                func, args, kwargs = task_item
                
                # 记录开始时间
                start_time = time.time()
                
                # 执行任务并处理结果
                try:
                    result = func(*args, **kwargs)
                    self.result_queue.put(("SUCCESS", result))
                except Exception as e:
                    self.result_queue.put(("ERROR", str(e)))
                
                # 检查任务执行时间
                execution_time = time.time() - start_time
                if execution_time > self.task_timeout:
                    self.result_queue.put(("TIMEOUT", f"Task executed {execution_time:.2f}s > {self.task_timeout}s"))
                
                # 更新最后活动时间
                with self.last_activity_time.get_lock():
                    self.last_activity_time.value = time.time()
            
            except queue.Empty:
                # 队列为空时继续等待
                continue
            except Exception as e:
                self.result_queue.put(("CRITICAL", f"Worker error: {str(e)}"))
    
    def _monitor_pool(self) -> None:
        """监控线程，动态调整进程数量"""
        last_check_time = time.time()
        
        while self.running.value and not self.shutdown_event.is_set():
            current_time = time.time()
            
            # 定期检查状态（每秒一次）
            time.sleep(1)
            
            # 检查空闲状态
            idle_duration = current_time - self.last_activity_time.value
            if idle_duration > self.idle_timeout:
                with self.adjustment_lock:
                    self._remove_worker()
            
            # 定期打印状态（每10秒一次）
            if current_time - last_check_time > 10:
                last_check_time = current_time
                print(f"[Monitor] Workers: {self.active_workers.value}, "
                      f"Tasks: {self.task_queue.qsize()}, "
                      f"Results: {self.result_queue.qsize()}, "
                      f"Idle: {idle_duration:.1f}s")

    def _clear_queue(self, q: mp.Queue) -> None:
        """清空队列"""
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                break

    def get_results(self, timeout: float = 1.0) -> list:
        """获取所有可用结果（非阻塞）"""
        results = []
        while not self.result_queue.empty():
            try:
                results.append(self.result_queue.get(timeout=timeout))
            except queue.Empty:
                break
        return results

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)
import time
import random

def sample_task(task_id, duration):
    """模拟一个需要长时间执行的任务"""
    print(f"Starting task {task_id}, will run for {duration} seconds")
    time.sleep(duration)
    return f"Task {task_id} completed in {duration}s"

if __name__ == "__main__":
    # 创建进程池（最小1个进程，最大4个进程）
    with DynamicProcessPool(min_workers=1, max_workers=4) as pool:
        # 提交20个随机时长的任务
        for i in range(20):
            task_duration = random.uniform(0.5, 5.0)
            pool.submit(sample_task, i, task_duration)
        
        # 等待所有任务完成
        completed = 0
        while completed < 20:
            # 处理结果
            for status, result in pool.get_results():
                if status == "SUCCESS":
                    print(f"Completed: {result}")
                    completed += 1
                else:
                    print(f"Task failed: {result}")
            
            time.sleep(0.5)
    
    print("All tasks completed!")