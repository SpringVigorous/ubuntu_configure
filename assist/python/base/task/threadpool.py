import threading
import queue
import time
import os
import sys
import os
from typing import Callable, Any
from collections.abc import Iterable



from base.com_log import logger_helper,UpdateTimeType
from base.com_decorator import exception_decorator

class ThreadPool:
    def __init__(self, num_threads:int=max(os.cpu_count()*2,1),ideal_time=5,root_thread_name:str=""):
        self._num_threads = num_threads if num_threads  else max(os.cpu_count()*2,1) # 线程数量
        self._task_queue = queue.Queue()  # 任务队列
        self._stop_event = threading.Event()  # 停止事件
        self._threads:list[threading.Thread] = []  # 线程列表
        self._ideal_time=ideal_time
        self._logger=logger_helper(f"{self.__class__.__name__}-{root_thread_name}")
        self._lock = threading.Lock()  # 保护线程列表的锁
        
        self._thread_index:int=1
        self._thread_name:str=root_thread_name
        
        self._error_lst = []  # 任务队列
        self._count:int=0
    @property
    def count(self):
        return self._count
    @property
    def add_count(self):
        self._count+=1
        return self.count
      
    @property
    def thread_name(self):
        name=self._thread_name if self._thread_name else "线程"
        return f"{name}_{self._thread_index:02}"
    
    @property
    def has_init_thread(self)->bool:
        return self._thread_index>=self._num_threads
    
    def _start(self):
        
        if self.has_init_thread:
            return
        logger=self._logger
        logger.update_target(detail="创建线程池")
        logger.update_time(UpdateTimeType.STAGE)
        """ 启动初始线程 """
        with self._lock:
            for _ in range(self._num_threads):
                self._start_thread()
                
        logger.debug("成功",f"共{len(self._threads)}个",update_time_type=UpdateTimeType.STAGE)

    def _start_thread(self):
        logger=self._logger
        logger.update_time(UpdateTimeType.STEP)
        """ 启动单个线程并加入列表 """
        try:
            thread = threading.Thread(target=self._worker_loop,name=self.thread_name)
            logger.stack_target(detail=f"添加线程:{thread.name}")
            
            thread.start()
            self._threads.append(thread)
            self._thread_index+=1
            
            logger.trace("成功",update_time_type=UpdateTimeType.STEP)
        except:
            pass
        finally:
            logger.pop_target()
            
        

    def submit(self, func, *args,callback: Callable[[Any, Exception], None] = None, **kwargs):
        #开启线程池
        if not self.has_init_thread:
            self._start()
        
        self._task_queue.put((func, args, kwargs,callback))
        
        # """ 提交任务到队列 """
        # if not self.stop_event.is_set():
        #     self.task_queue.put((func, args, kwargs,callback))
        # else:
        #     raise RuntimeError("Cannot submit tasks after shutdown")

    def _pop_data(self):
        try:
            # 非阻塞获取任务，最多等待1秒
            return self._task_queue.get(block=True, timeout=1)
        except queue.Empty:
            time.sleep(self._ideal_time)
              # 队列为空时继续循环
            return 

    def _worker_loop(self):
        """ 工作线程的循环逻辑 """
        
        logger=logger_helper(threading.current_thread().name)

        logger.trace("线程开始")
        cur_index:int=0
        while True:
            # 退出条件：停止事件被触发且队列为空
            if self._stop_event.is_set() and self._task_queue.empty():
                break

            data=self._pop_data()
            if not data:
                continue
            #必须要标记下状态
            self._task_queue.task_done()  # 标记任务完成
                
            # 非阻塞获取任务，最多等待1秒
            func, args, kwargs, callback = data
            
            def only_keywords(org_str:str):
                char_count=50
                
                
                if not org_str or len(org_str)<2*char_count+1:
                    return org_str
                
                return f"{org_str[:char_count]}...{org_str[-char_count:]}"
            
            args_str=f"{args}"
            kwargs_str=f"{kwargs}"
            cur_index+=1
            with logger.raii_target(detail=f"第{cur_index}/{self.add_count}个消息-func:{func.__name__},args:*{only_keywords(args_str)},kwargs:**{only_keywords(kwargs_str)}") as out_logger:
                out_logger.update_time(UpdateTimeType.STAGE)

                out_logger.trace("收到消息",update_time_type=UpdateTimeType.STAGE)
                result = None
                error = None
                try:
                    result=func(*args, **kwargs)  # 执行任务
                    out_logger.debug("完成",f"结果是：{result}",update_time_type=UpdateTimeType.STEP)
                except Exception as e:
                    out_logger.error("异常",f"Task execution failed: {e}",update_time_type=UpdateTimeType.STEP)
                    error=e
                    self._error_lst.append(data)
                finally:
                    # 如果有回调则执行回调
                    if callback is not None:

                        with out_logger.raii_target(detail=f"func:{callback.__name__},args:{(result,error)}") as in_logger:
                            in_logger.trace("回调开始",update_time_type=UpdateTimeType.STEP)
                            try:
                                callback(result, error)
                                in_logger.trace("回调完成",update_time_type=UpdateTimeType.STEP)
                            except Exception as e:
                                in_logger.error("回调异常",f"Callback failed: {e}")
                    
        logger.update_target(detail=f"当前线程共{cur_index}个消息")
        logger.info("线程结束",update_time_type=UpdateTimeType.ALL)

    def join_impl(self):
        
        for data in self._error_lst:
            self._task_queue.put(data)
        self._error_lst.clear()
        self._task_queue.join()
        
    
    @exception_decorator(error_state=False)
    def join(self, wait=True):
        """ 关闭线程池 """
        self._stop_event.set()  # 触发停止事件
        self._logger.update_target(detail="触发停止事件")
        
        self._logger.debug("进行中",update_time_type=UpdateTimeType.STAGE)
        if wait:
            self._task_queue.join()  # 等待所有任务完成

            for thread in self._threads:
                if thread.is_alive():
                    thread.join()  # 等待所有线程退出
                    
        self._logger.info("完成",f"共处理{self.count}消息",update_time_type=UpdateTimeType.ALL)

    @exception_decorator(error_state=False)
    def restart(self):
        """ 补充缺失的线程至目标数量 """
        
        
        logger=self._logger
        logger.update_target(detail="恢复线程池")
        logger.update_time(UpdateTimeType.STAGE)
        with self._lock:
            
            # 1. 清除停止事件（关键改动）
            self._stop_event.clear()
            # 清理已退出的线程对象
            self._threads = [t for t in self._threads if t.is_alive()]
            # 补充缺失的线程
            current_threads = len(self._threads)
            if current_threads < self._num_threads:
                for _ in range(self._num_threads - current_threads):
                    self._start_thread()
            logger.debug("成功",f"补充{len(self._threads)-current_threads}个",update_time_type=UpdateTimeType.STAGE)
        
    def force_stop(self):
        self._stop_event.set()  # 触发停止事件
        with self._lock:
            self._logger.update_target(detail="强制退出，清空队列")
            self._logger.debug("开始",f"任务列表剩余{len(self._task_queue)}个",update_time_type=UpdateTimeType.STAGE)
            self._task_queue.clear()
            self._task_queue.task_done()

            

def pool_executor(callable_lst:Iterable[Iterable],thread_count:int=0):
    #线程池
    pool=ThreadPool(thread_count)
    for item in callable_lst:
        pool.submit(*item)
    pool.join()

    
import random
# 使用示例
if __name__ == "__main__":
    def example_task(task_id, delay=1):
        print(f"Task {task_id} started")
        time.sleep(delay)
        print(f"Task {task_id} completed")
        
        val=random.randint(1,1000)
        if val % 2 == 0:
            raise Exception(f"random error:{val}")
        return 1
        
    # 回调函数处理结果
    def result_callback(result, error):
        if error:
            print(f"Task failed: {str(error)}")
        else:
            print(f"Task completed: {result}")
            
            
            
            
    # 创建包含3个线程的线程池
    pool = ThreadPool()
    pool._start()

    # 提交10个任务
    for i in range(20):
        pool.submit(example_task, i,callback=result_callback)

    # 关闭后重置
    time.sleep(0.5)
    print("\nShutting down pool...")
    pool.join(wait=False)  # 非阻塞关闭

    time.sleep(2)
    print("Resetting pool...")
    pool.restart()  # 重置后线程池恢复可用

    # 提交新任务
    for i in range(10, 13):
        pool.submit(example_task, i, delay=0.5)

    # 再次关闭
    time.sleep(2)
    pool.join()
    print("All tasks completed")