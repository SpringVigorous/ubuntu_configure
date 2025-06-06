﻿import asyncio

import functools


import concurrent.futures
import threading
from time import time
import operator
from com_log import logger_helper,UpdateTimeType
from com_decorator import  exception_decorator
from except_tools import except_stack
import random

    
# 转换为协程函数
# @functools.wraps(func)
async def as_coroutine(func,*args, **kwargs):
    
    result = await asyncio.to_thread(func,*args, **kwargs)
    return result

    # return func(*args, **kwargs)


# 转换为普通函数
def as_normal(func,*args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    restult = loop.run_until_complete(func(*args, **kwargs))
    loop.close()
    return restult
    

    # result = asyncio.run(func(*args, **kwargs))
    # return result



class MultiThreadCoroutine:
    def __init__(self, coroutine_func, args_list:list[list|tuple],threads_count:int=10, concurrent_task_count:int=100, semaphore_count:int=20):
        # 使用 shuffle() 函数对列表进行随机排列,避免某一项出现异常，导致 对应的线程退出（多重复几次）
        self.args_list = args_list.copy()
        random.shuffle(self.args_list)

        
        
        self.thread_count = threads_count
        self.concurrent_task_count = concurrent_task_count
        self.coroutine_func = coroutine_func
        self.semaphore_count = semaphore_count
        self.result=[]
        self._reset_count()
    def _reset_count(self):
        count=self.tasks_count
        
        while count/self.concurrent_task_count<self.thread_count and count>0:
            temp:int=max(1,int(count/self.thread_count) )
            dest:int=max(1, int(temp/3))
            
            result=dest if dest>1 else temp
            
            self.concurrent_task_count= result
            if result<10:
                break
            pass
        
        
        
        
        
    @property
    def tasks_count(self):
        return len(self.args_list)
    
    
    @property
    def success(self)->bool:
        for result in self.result:
            for item in result:
                if isinstance(item,Exception):
                    return False
        return bool(self.result)
    @property
    @exception_decorator(error_state=False)
    def _fail_info(self):
        if self.success:
            return []
        info=[]

        for  i,result in enumerate(self.result):
            for j,item in enumerate(result):
                if isinstance(item,Exception):
                    index=self.index(i,j)
                    if  index<0 or index>=len(self.args_list):
                        continue
                    info.append((index,self.args_list[index],item))

        return info
    
    

    def index(self,i,j):
        return i*self.concurrent_task_count+j
    @property
    def fail_infos(self):
        infos=self._fail_info
        errors=[f"Task {index} failed with args {args} and error {error}"   for index,args,error in infos]
        return f"失败{len(infos)}个：\n{'\n'.join(errors)}\n" 
    
    # 线程中的异步任务处理函数
    def run_coroutines_in_thread(self, args_list, concurrent_task_count, coroutine_func):
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results=[]
        try:
            # 在每个线程中创建独立的 Semaphore 对象
            semaphore = asyncio.Semaphore(concurrent_task_count)
            
            tasks = [coroutine_func(semaphore,args) for args in args_list]
            results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        finally:
            loop.close()
            pass
        # return results[1] if len(results)>1 else results[0]
        return results

    # 封装的主函数
    async def run_tasks(self):
        results =[]
        task_logger =logger_helper("多线程-协程",f"共{self.tasks_count}个")
        task_logger.trace("开始")
        if self.tasks_count<1:
            task_logger.trace("没有任务")
            return results
        
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            futures = []
            # 创建一个事件循环
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)

            # 将任务分配到线程池
            try:
                for i in range(0, self.tasks_count, self.concurrent_task_count):
                    last_index=min(i + self.concurrent_task_count, self.tasks_count)
                    
                    batch = self.args_list[i:last_index]
                    
                    
                    # future = loop.run_in_executor(executor, self.run_coroutines_in_thread, batch, self.semaphore_count, self.coroutine_func)
                    future =executor.submit( self.run_coroutines_in_thread, batch, self.semaphore_count, self.coroutine_func)
                    futures.append(future)
                
                # 等待所有任务完成
                # results = await asyncio.gather(*futures, return_exceptions=True)
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            except Exception as e:
                task_logger.error("异常",except_stack(),update_time_type=UpdateTimeType.ALL)
            finally:
                # loop.close()
                pass
        self.result=results
        return self.result





