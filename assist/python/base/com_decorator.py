import sys

import time
from functools import wraps
from com_log import logger as logger
from output_agent import OutputAgent
from state import ReturnState
from except_tools import except_stack


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if logger:
            logger.debug("function {} run time: {}".format(func.__name__, elapsed_time))
        return result
    return wrapper


    
# 定义一个装饰器
def exception_decorator(error_callback:callable=None,error_state=True):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if error_callback:
                    error_callback()
                
            # 这个except块会处理上述try块中的任何异常
                # 获取当前的异常信息


                if logger:
                    logger.error(f"\n发现异常：\n{except_stack()}")
                #卸载代理
                    # agent.uninstall()
                #异常时 返回空值
                return ReturnState.EXCEPT if error_state else None



        return wrapper
    return decorator
def details_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 这里是前置操作，例如打印函数调用信息
        if logger:
            logger.debug(f"开始执行函数: {func.__name__}")
        
        # 执行原始函数，并获取结果
        result = func(*args, **kwargs)
        
        # 虽然这里不是严格意义上的“前置”，但可以在此处添加函数执行后的操作
        if logger:
            logger.debug(f"完成执行函数: {func.__name__}")

        return result
    return wrapper



def dynamic_wrapper(*functions):
    def wrapper(*args, **kwargs):
        results = {}
        for func in functions:
            try:
                result = func(*args, **kwargs)
                results[func.__name__] = result
            except Exception as e:
                print(f"Error calling function {func.__name__}: {e}")
        return results

    return wrapper


def singleton(cls):
    """单例装饰器"""
    # 用于缓存类的实例
    instances = {}
    
    def wrapper(*args, **kwargs):
        # 如果类未实例化，则创建实例并缓存
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        # 返回缓存的实例
        return instances[cls]
    
    return wrapper


class Ref:
    """优雅的引用式包装类，支持属性代理和直观赋值"""
    def __init__(self, value):
        self._value = value  # 用下划线标识内部存储
    
    def set(self, new_value):
        """设置新值（替代直接赋值变量本身）"""
        self._value = new_value
    
    @property
    def value(self):
        """获取原始值（可选，用于显式访问）"""
        return self._value
    
    # 核心：代理内部对象的所有属性访问
    def __getattr__(self, name):
        """当访问不存在的属性时，转发给内部对象"""
        return getattr(self._value, name)
    
    # 让打印更直观
    def __repr__(self):
        return f"Ref({self._value!r})"
    
    def __str__(self):
        return str(self._value)

# # 假设我们有多个函数
# def add(x, y):
#     return x + y

# def multiply(x, y):
#     return x * y

# # 使用装饰器包装这两个函数
# combined_function = dynamic_wrapper(add, multiply)

# # 现在调用这个组合函数
# result = combined_function(2, 3)
# print(result)  # 输出: {'add': 5, 'multiply': 6}