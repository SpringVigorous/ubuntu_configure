import logging
from logging.handlers import TimedRotatingFileHandler
from enum import Enum
import os
import json
import sys
import __init__
import threading
from time import time,sleep

from custom_log import CustomLogger

# 定义TRACE等级
TRACE_LEVEL_NUM = logging.DEBUG - 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)
        
        

logging.Logger.trace = trace
logger :CustomLogger=None

def record_detail(target:str,status:str,detail:str)->str:
    info=f"【{target}】-【{status}】"
    if detail:
        info+="详情：{}".format(detail)    
    return info

def usage_time(start_time:time)->str:
    return f"耗时：{time()-start_time:.3f}秒"


def record_detail_usage(target:str,status:str,detail:str,start_time:time)->str:
    
    lst=[detail,usage_time(start_time)]
    content=",".join(filter(lambda x:x,lst))
    return record_detail(target,status,content)



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
        base_formatter = CustomFormatter('%(asctime)s-%(levelname)s-Thread ID: %(thread_id)s-%(message)s')


        # 再创建一个handler，用于输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(str_to_level(console_level))
        console_handler.setFormatter(base_formatter)
        # 添加控制台Handler到日志器
        logger.addHandler(console_handler)

        # 创建文件Handler并设置日志级别与格式

        log_dir=os.path.join(os.getcwd(), 'logs',logger_name)
        os.makedirs(log_dir,exist_ok=True)
        
        detail_formatter = CustomFormatter('%(asctime)s-%(name)s-%(levelname)s- %(filename)s:%(lineno)d -%(funcName)s()-Thread ID: %(thread_id)s-%(message)s')
        def create_file_log(level_str:str,log_format:str):
            level_str=level_str.lower()
            
            log_path=os.path.join(log_dir, f'{logger_name}-{level_str}.log')
            
            # 创建一个 TimedRotatingFileHandler，每天创建一个新的日志文件
            file_handler = TimedRotatingFileHandler(log_path, when="midnight", encoding='utf-8-sig', interval=1, backupCount=30)
            file_handler.suffix = "%Y-%m-%d.log"
            
            # file_handler = logging.FileHandler(log_path, encoding='utf-8-sig')  # FileHandler将日志写入到指定的文件名中
            file_handler.setLevel(str_to_level(level_str))  # 文件处理器处理的日志级别设为INFO，可根据需求调整
            file_handler.setFormatter(log_format)  # 使用相同的格式化器
            # 添加文件Handler到日志器
            logger.addHandler(file_handler)
        
        log_less_warn= str_to_level(log_level)<str_to_level("warn")
        
        create_file_log(log_level,base_formatter if log_less_warn else detail_formatter)
        # create_file_log(log_level,detail_formatter)
        if log_less_warn:
            create_file_log("warn",detail_formatter)
        

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
 

class UpdateTimeType(Enum):
    NONE=(0,"无更新")
    STEP=(1,"步长更新")
    ALL=(2,"起始更新")
    STAGE=(3,"阶段更新")

    def __init__(self, code, description):
        self.code = code
        self.description = description

    def is_none(self):
        return self==UpdateTimeType.NONE
    
    def is_step(self):
        return self==UpdateTimeType.STEP
    
    def is_all(self):
        return self==UpdateTimeType.ALL
        
    def is_stage(self):
        return self==UpdateTimeType.STAGE
    
    @classmethod
    def from_update(cls, state=None):

        if not str(type(state))==str(cls):
            return cls.NONE
        
        return state


class logger_helper:
       
    def __init__(self,target:str=None,detail:str=None):
        self.reset_time()
        self.update_target(target,detail)
        
    #若是为空，则不更新
    def update_target(self,target:str=None,detail:str=None):
        if target:
            self._target=target
        elif not hasattr(self,"_target"):
            self._target=None
        if detail:
            self._detail=detail
        elif not hasattr(self,"_detail"):
            self._detail=None
        
    #仅更新 原始初始值
    def update_start(self):
        self._start_time=time()
    #仅更新 详细步骤初始值
    def update_step(self):
        self._step_time=time()

    #仅更新 阶段初始值
    def update_stage(self):    
        self._stage_time=time()
        
    def reset_time(self):
        self.update_start()
        self.update_step()
        self.update_stage()
       
    def state_time(self,state:UpdateTimeType):
        if state.is_step():
            return self._step_time
        elif state.is_stage():
            return self._stage_time
        elif state.is_all():
            return self._start_time
        else:
            return None
    def update_time(self,state:UpdateTimeType):
        if state.is_step():
            self.update_step()
        elif state.is_stage():
            self.update_step()
            self.update_stage()
        elif state.is_all():
            self.reset_time()
        else:
            pass
        
    def detail_content(self,detail_lat:str=None):
        return f"{self._detail},{detail_lat}" if detail_lat else self._detail
        
    #仅内容
    def content(self,status:str,detail_lat:str=None,update_time=None)->str:     
        return record_detail(self._target,status,self.detail_content(detail_lat))
    #内容+耗时
    def content_useage(self,status:str,detail_lat:str=None,update_time=None)->str:
        
        state=UpdateTimeType.from_update(update_time)
        cur_time=self.state_time(state) 
        return record_detail_usage(self._target,status,self.detail_content(detail_lat),cur_time)
    
    def _log_impl(self,mfunc,status:str,details:str=None,update_time_type=None):
        
        state=UpdateTimeType.from_update(update_time_type)
        pfunc=self.content_useage if not state.is_none() else self.content
        info=pfunc(status,details,state)
        self.update_time(state)           
        if logger is not None and mfunc is not None:
            mfunc(info)
        else:
            print(info)
    def debug(self,status:str,details:str=None,update_time_type=None):
        self._log_impl(debug,status,details,update_time_type)
    
    def info(self,status:str,details:str=None,update_time_type=None):
        self._log_impl(info,status,details,update_time_type)
    
    def warn(self,status:str,details:str=None,update_time_type=None):
        self._log_impl(warn,status,details,update_time_type)
        
    def error(self,status:str,details:str=None,update_time_type=None):
        self._log_impl(error,status,details,update_time_type)
        
    def trace(self,status:str,details:str=None,update_time_type=None):
        self._log_impl(trace,status,details,update_time_type)
    
    
    

        
if __name__ == "__main__":
    helper=logger_helper("test","test_detail")
    print(helper.content("成功","测试"))
    sleep(1)
    print(helper.content_useage("成功a","测试1"))