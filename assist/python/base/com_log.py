import logging
from enum import Enum
import os
import json
import sys
import __init__
import threading
from time import time
# 定义TRACE等级
TRACE_LEVEL_NUM = logging.DEBUG - 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)
logging.Logger.trace = trace
logger :logging.Logger=None

def record_detail(target:str,status:str,detail:str)->str:
    return f"【{target}】-【{status}】详情：{detail}"

def usage_time(start_time:time)->str:
    return f"耗时：{time()-start_time}秒"
def str_to_level(level_str:str)->int:
    
    #添加Trace
    if level_str.upper().strip()=="TRACE":
        return TRACE_LEVEL_NUM
    
    level= logging.getLevelName(level_str.upper())
    return level if isinstance(level, int) else TRACE_LEVEL_NUM

# 自定义日志格式器
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # 在日志记录中添加当前线程 ID
        record.thread_id = threading.current_thread().ident
        return super().format(record)

def create_logger(logger_name:str ,level:str="debug",log_level:str="trace",console_level:str="info"):
    global logger
    # 定义日志器名称
    if logger is None:
        is_exist= logger_name in logging.Logger.manager.loggerDict
        logger = logging.getLogger(logger_name)
        if is_exist:
            return logger
        logger.setLevel(str_to_level(level))# 设置日志级别，这里设置为DEBUG，可以根据需要修改
        # 创建一个处理器并设置其输出格式
        formatter = CustomFormatter('%(asctime)s-%(name)s-%(levelname)s- %(filename)s:%(lineno)d -%(funcName)s()-%(levelname)s-Thread ID: %(thread_id)s-%(message)s')


        # 再创建一个handler，用于输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(str_to_level(console_level))
        console_handler.setFormatter(formatter)
        # 添加控制台Handler到日志器
        logger.addHandler(console_handler)

        # 创建文件Handler并设置日志级别与格式
        log_dir=os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir,exist_ok=True)
        
        def create_file_log(level_str:str):
            level_str=level_str.lower()
            
            log_path=os.path.join(log_dir, f'{logger_name}-{level_str}.log')
            file_handler = logging.FileHandler(log_path, encoding='utf-8-sig')  # FileHandler将日志写入到指定的文件名中
            file_handler.setLevel(str_to_level(level_str))  # 文件处理器处理的日志级别设为INFO，可根据需求调整
            file_handler.setFormatter(formatter)  # 使用相同的格式化器
            # 添加文件Handler到日志器
            logger.addHandler(file_handler)
        
        
        create_file_log(log_level)
        create_file_log("warn")
        

        # 开始使用日志器记录信息
        logger.info(f'log file path: {log_dir}')

    return logger    

def force_create_logger(logger_name:str ,level:str="debug",log_level:str="trace",console_level:str="info"):
    global logger
    logger = None
    create_logger(logger_name, level, log_level, console_level)

            
    
    
# from config import settings
# log_config= settings.log
# if logger is None:
#     create_logger(log_config.log_name, log_config.level, log_config.log_level, log_config.console_level)

#先默认取值,后续若想改，还可以用 force_create_logger(...)
if logger is None:
    create_logger(os.path.splitext(os.path.basename(sys.argv[0]))[0] , "trace","trace","info")
    

def __log_impl__(mfunc, msg: object, *args: object):
    if logger is not None and mfunc is not None:
        mfunc(msg, *args)
    else:
        print(msg, *args)


def info(msg: object, *args: object):
    __log_impl__(logger.info,msg, *args) 
 
def trace(msg: object, *args: object):
    __log_impl__(logger.trace,msg, *args) 
 
def debug(msg: object, *args: object):
    __log_impl__(logger.debug,msg, *args) 
 
def warn(msg: object, *args: object):
    __log_impl__(logger.warn,msg, *args) 
 
def info(msg: object, *args: object):
    __log_impl__(logger.info,msg, *args) 
 
def error(msg: object, *args: object):
    __log_impl__(logger.error,msg, *args) 
 




    
    
    
    
    # logger.debug("Debugging information")
    # logger.info("Normal information message")
    # logger.warning("Warning occurred")
    # logger.error("An error happened")
    # logger.critical("Critical error")

    # folder= os.path.dirname(os.path.dirname(__file__))
    # with open(os.path.join(folder,"config/log_config.json"), "r",encoding="utf-8-sig") as f:
    #     log_config = json.load(f)
    # log_name=log_config.get("log_name","info")
    # level=log_config.get("level","debug")
    # log_level = log_config.get("log_level","debug")
    # console_level = log_config.get("console_level","debug")

    # create_logger(log_name, level, log_level, console_level)
    