import asyncio
import concurrent.futures
import threading
from time import time
class MultiThreadCoroutine:
    def __init__(self, num_tasks, max_workers, max_concurrent_tasks_per_thread, coroutine_func):
        self.num_tasks = num_tasks
        self.max_workers = max_workers
        self.max_concurrent_tasks_per_thread = max_concurrent_tasks_per_thread
        self.coroutine_func = coroutine_func

    # 线程中的异步任务处理函数
    def run_coroutines_in_thread(self, task_ids, max_concurrent_tasks_per_thread, coroutine_func):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 在每个线程中创建独立的 Semaphore 对象
        semaphore = asyncio.Semaphore(max_concurrent_tasks_per_thread)
        
        tasks = [coroutine_func(task_id, semaphore) for task_id in task_ids]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        return results

    # 封装的主函数
    def run_tasks(self):
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 创建一个事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 将任务分配到线程池
            futures = []
            for i in range(0, self.num_tasks, self.max_concurrent_tasks_per_thread):
                batch = list(range(i, min(i + self.max_concurrent_tasks_per_thread, self.num_tasks)))
                future = loop.run_in_executor(executor, self.run_coroutines_in_thread, batch, self.max_concurrent_tasks_per_thread, self.coroutine_func)
                futures.append(future)
            
            # 等待所有任务完成
            results = loop.run_until_complete(asyncio.gather(*futures))
        
        # 打印结果
        for batch_results in results:
            print(batch_results)

# 定义一个协程函数
async def my_coroutine(task_id, semaphore):
    async with semaphore:
        await asyncio.sleep(1)  # 模拟异步操作
        print(f"Task {task_id} started in thread {threading.current_thread().name}")
        await asyncio.sleep(1)  # 模拟异步操作
        print(f"Task {task_id} finished in thread {threading.current_thread().name}")
        return f"Result of task {task_id}"

# 运行封装的主函数
if __name__ == "__main__":
    num_tasks = 1000
    max_workers = 10  # 线程池的最大线程数
    max_concurrent_tasks_per_thread = 30  # 每个线程的最大并发任务数
    cur_time=time()
    multi_thread_coroutine = MultiThreadCoroutine(num_tasks,max_workers, max_concurrent_tasks_per_thread,  my_coroutine)
    multi_thread_coroutine.run_tasks()
    print(f"Time taken: {time()-cur_time} seconds")