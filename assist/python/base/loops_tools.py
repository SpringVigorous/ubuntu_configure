
from typing import Callable
from base.com_log import logger_helper,UpdateTimeType
from base.except_tools import except_stack,fatal_link_error

class RetryOperater:
    def __init__(self, retry_count, normal_func:Callable=None, failure_func:Callable=None):
        self.original_retry_count = retry_count
        self.retry_count = retry_count
        self.normal_func = normal_func
        self.failure_func = failure_func
        self._has_fatal_error:bool=False

    def reset(self, retry_count, normal_func:Callable=None, failure_func:Callable=None):
        self.original_retry_count = retry_count
        self.retry_count = retry_count 
        if normal_func:
            self.normal_func = normal_func
        if failure_func:
            self.failure_func = failure_func
            

            
    def success(self):
        
        logger=logger_helper(f"{self.original_retry_count}次重试")
        result=None
        if not self.normal_func:
            return result
        
        #如果是严重的错误，则不进行重试，直接退出；返回True 则代表 致命错误
        def failure_func():
            if fatal_link_error():
                self._has_fatal_error=True
                return True
            
            value= self.failure_func()
            self._has_fatal_error=value
            self.retry_count -= 1
            return value
        
        
        while self.retry_count > 0 and not self.fatal_error:
            logger.update_target(detail=f"当前剩余{self.retry_count}次" )
            try:
                result = self.normal_func()
                if result:
                    self.retry_count = self.original_retry_count
                    return result
                else:
                    logger.error("失败","再重试一次",UpdateTimeType.STAGE)
                    failure_func()

                    
            except Exception as e:
                logger.error("失败",f"{e}:\n{except_stack()}",UpdateTimeType.STAGE)
                failure_func()

        
        return result
    
    #致命错误
    @property
    def fatal_error(self):
        return self._has_fatal_error


