import sys
import traceback
import time
from functools import wraps
from com_log import logger as global_logger

def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if global_logger:
            global_logger.debug("function {} run time: {}".format(func.__name__, elapsed_time))
        return result
    return wrapper

# 定义一个装饰器
def exception_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
        # 这个except块会处理上述try块中的任何异常
            # 获取当前的异常信息
            _, exc_value, exc_traceback = sys.exc_info()

        if global_logger:
            global_logger.warning(f"\n发现异常：{exc_value}")
            # 打印异常堆栈信息，其中包含了函数调用的文件信息
            traceback.print_tb(exc_traceback.tb_next)



    return wrapper

def details_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 这里是前置操作，例如打印函数调用信息
        if global_logger:
            global_logger.debug(f"开始执行函数: {func.__name__}")
        
        # 执行原始函数，并获取结果
        result = func(*args, **kwargs)
        
        # 虽然这里不是严格意义上的“前置”，但可以在此处添加函数执行后的操作
        if global_logger:
            global_logger.debug(f"完成执行函数: {func.__name__}")

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