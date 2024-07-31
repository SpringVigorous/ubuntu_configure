import chardet
from com_log import logger as logger
# 使用chardet模块检测文件的编码
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    logger.trace(f" {file_path} 检测到文件编码：{result}")
    # 返回检测到的编码
    return result['encoding'].lower()

# 获取文件路径
# file_path = r'F:\test_data\gbk.txt'

# 检测编码
# encoding = detect_encoding(file_path)

# # 使用检测到的编码打开文件
# with open(file_path, 'r', encoding=encoding) as f:
#     content = f.read()

# logger.info(content)