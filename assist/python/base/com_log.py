﻿import logging
from enum import Enum
import os
from pathlib import Path
import json
import sys



logger :logging.Logger=None
def str_to_level(level_str:str)->int:
    level= logging.getLevelName(level_str.upper())
    return level if isinstance(level, int) else logging.DEBUG
def create_logger(logger_name:str ,level:str="debug",log_level:str="debug",console_level:str="info"):
    global logger
    if logger is None:
# 定义日志器名称
        logger = logging.getLogger(logger_name)
        logger.setLevel(str_to_level(level))# 设置日志级别，这里设置为DEBUG，可以根据需要修改
        # 创建一个处理器并设置其输出格式
        formatter = logging.Formatter('%(asctime)s-%(filename)s:%(lineno)d-%(funcName)s()-%(levelname)s-%(message)s')


        # 再创建一个handler，用于输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(str_to_level(console_level))
        console_handler.setFormatter(formatter)
        # 添加控制台Handler到日志器
        logger.addHandler(console_handler)

        # 创建文件Handler并设置日志级别与格式
        os.makedirs("logs",exist_ok=True)
        file_handler = logging.FileHandler(f'logs/{logger_name}.log')  # FileHandler将日志写入到指定的文件名中
        file_handler.setLevel(str_to_level(log_level))  # 文件处理器处理的日志级别设为INFO，可根据需求调整
        file_handler.setFormatter(formatter)  # 使用相同的格式化器
        # 添加文件Handler到日志器
        logger.addHandler(file_handler)

        # 开始使用日志器记录信息

    return logger    


project_root =str(Path(__file__).resolve().parent.parent)
if not project_root in sys.path:
    sys.path.insert(0,project_root)
from config import settings
log_name=settings.get("log_name","info")
level=settings.get("level","debug")
log_level = settings.get("log_level","debug")
console_level = settings.get("console_level","debug")

create_logger(log_name, level, log_level, console_level)


if __name__ == "__main__":
    
    file_name=os.path.basename(__file__)
    create_logger(file_name, "debug", "debug", "warning")
    logger.debug("Debugging information")
    logger.info("Normal information message")
    logger.warning("Warning occurred")
    logger.error("An error happened")
    logger.critical("Critical error")

    # folder= os.path.dirname(os.path.dirname(__file__))
    # with open(os.path.join(folder,"config/log_config.json"), "r",encoding="utf-8-sig") as f:
    #     log_config = json.load(f)
    # log_name=log_config.get("log_name","info")
    # level=log_config.get("level","debug")
    # log_level = log_config.get("log_level","debug")
    # console_level = log_config.get("console_level","debug")

    # create_logger(log_name, level, log_level, console_level)
    