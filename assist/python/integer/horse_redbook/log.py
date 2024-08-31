import logging
from logging.handlers import TimedRotatingFileHandler
import time


def get_logger(self):
	self.logger = logging.getLogger(__name__)
	# 日志格式
	formatter = '[%(asctime)s-%(filename)s][%(funcName)s-%(lineno)d]--%(message)s'
	# 日志级别
	self.logger.setLevel(logging.DEBUG)
	# 控制台日志
	sh = logging.StreamHandler()
	sh.setFormatter(formatter)
	sh.setLevel(logging.DEBUG)
	self.logger.addHandler(sh)
 
	log_formatter = logging.Formatter(formatter, datefmt='%Y-%m-%d %H:%M:%S')
	# info日志文件名
	info_file_name = time.strftime("%Y-%m-%d") + '.log'
	# 将其保存到特定目录
	case_dir = r'./logs/'
	info_handler = TimedRotatingFileHandler(filename=case_dir + info_file_name,
										when='MIDNIGHT',
										interval=1,
										backupCount=7,
										encoding='utf-8')
 
	info_handler.setFormatter(log_formatter)
 	info_handler.setLevel(logging.INFO)
	self.logger.addHandler(info_handler)
 
 
	return self.logger
