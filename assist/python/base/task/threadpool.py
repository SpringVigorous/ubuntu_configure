import threading
import queue
import time
import os
import sys
import os
from typing import Callable, Any


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from com_log import logger_helper,UpdateTimeType

class ThreadPool:
    def __init__(self, num_threads=max(os.cpu_count()*2,1),ideal_time=5,thread_name:str=""):
        self.num_threads = num_threads  # 线程数量
        self.task_queue = queue.Queue()  # 任务队列
        self.stop_event = threading.Event()  # 停止事件
        self.threads:list[threading.Thread] = []  # 线程列表
        self.ideal_time=ideal_time
        self.logger=logger_helper("ThreadPool","ThreadPool")
        self.lock = threading.Lock()  # 保护线程列表的锁
        self._thread_index:int=1
        self._thread_name:str=thread_name
      
    def thread_name(self):
        name=self._thread_name if self._thread_name else "线程"
        return f"{name}_{self._thread_index:02}"
    
    @property
    def has_init_thread(self)->bool:
        return self._thread_index>=self.num_threads
    
    def start(self):
        """ 启动初始线程 """
        with self.lock:
            for _ in range(self.num_threads):
                self._start_thread()
                

    def _start_thread(self):
        """ 启动单个线程并加入列表 """
        thread = threading.Thread(target=self._worker_loop,name=self.thread_name())
        thread.start()
        self.threads.append(thread)
        self._thread_index+=1
        self.logger.trace("成功添加线程",thread.name)
        

    def submit(self, func, *args,callback: Callable[[Any, Exception], None] = None, **kwargs):
        self.task_queue.put((func, args, kwargs,callback))
        # """ 提交任务到队列 """
        # if not self.stop_event.is_set():
        #     self.task_queue.put((func, args, kwargs,callback))
        # else:
        #     raise RuntimeError("Cannot submit tasks after shutdown")

    def _pop_data(self):
        try:
            # 非阻塞获取任务，最多等待1秒
            return self.task_queue.get(block=True, timeout=1)
        except queue.Empty:
            time.sleep(self.ideal_time)
              # 队列为空时继续循环
            return 

    def _worker_loop(self):
        """ 工作线程的循环逻辑 """
        
        logger=logger_helper(threading.current_thread().name)

        logger.trace("线程开始",update_time_type=UpdateTimeType.ALL)
        while True:
            # 退出条件：停止事件被触发且队列为空
            if self.stop_event.is_set() and self.task_queue.empty():
                break

            data=self._pop_data()
            if not data:
                continue

                
            # 非阻塞获取任务，最多等待1秒
            func, args, kwargs, callback = data
            logger.update_target(detail=f"func:{func.__name__},args:*{args},kwargs:**{kwargs}")
            logger.update_time(UpdateTimeType.STAGE)

            logger.trace("收到消息",update_time_type=UpdateTimeType.STAGE)
            result = None
            error = None
            try:
                result=func(*args, **kwargs)  # 执行任务
                logger.info("完成",f"结果是：{result}",update_time_type=UpdateTimeType.STEP)
            except Exception as e:
                logger.error("异常",f"Task execution failed: {e}",update_time_type=UpdateTimeType.STEP)
                error=e
            finally:
                # 如果有回调则执行回调
                if callback is not None:

                    logger.update_target(detail=f"func:{callback.__name__},args:{(result,error)}")
                    logger.trace("回调开始",update_time_type=UpdateTimeType.STEP)
                    try:
                        callback(result, error)
                        logger.info("回调完成",update_time_type=UpdateTimeType.STEP)
                    except Exception as e:
                        logger.error("回调异常",f"Callback failed: {e}")
                        
                self.task_queue.task_done()  # 标记任务完成

        logger.info("线程结束",update_time_type=UpdateTimeType.ALL)

    def shutdown(self, wait=True):
        """ 关闭线程池 """
        self.stop_event.set()  # 触发停止事件
        self.logger.info("触发停止事件",update_time_type=UpdateTimeType.STAGE)
        if wait:
            self.task_queue.join()  # 等待所有任务完成
            for thread in self.threads:
                if thread.is_alive():
                    thread.join()  # 等待所有线程退出
    def restart(self):
        """ 补充缺失的线程至目标数量 """
        self.logger.info("恢复线程池",update_time_type=UpdateTimeType.STAGE)
        
        with self.lock:
            
            # 1. 清除停止事件（关键改动）
            self.stop_event.clear()
            # 清理已退出的线程对象
            self.threads = [t for t in self.threads if t.is_alive()]
            # 补充缺失的线程
            current_threads = len(self.threads)
            if current_threads < self.num_threads:
                for _ in range(self.num_threads - current_threads):
                    self._start_thread()

                
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
    pool.start()

    # 提交10个任务
    for i in range(20):
        pool.submit(example_task, i,callback=result_callback)

    # 关闭后重置
    time.sleep(0.5)
    print("\nShutting down pool...")
    pool.shutdown(wait=False)  # 非阻塞关闭

    time.sleep(2)
    print("Resetting pool...")
    pool.restart()  # 重置后线程池恢复可用

    # 提交新任务
    for i in range(10, 13):
        pool.submit(example_task, i, delay=0.5)

    # 再次关闭
    time.sleep(2)
    pool.shutdown()
    print("All tasks completed")