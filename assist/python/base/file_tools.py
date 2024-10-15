import string_tools as st
import com_decorator as cd 
from com_log import logger,record_detail,usage_time
import chardet
import asyncio
import aiohttp
import aiofiles
import requests
import time
import os

# 使用chardet模块检测文件的编码
def detect_encoding(file_path)->str:
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

# logger.trace(content)



#读入文件
@cd.exception_decorator()
def read_content_by_encode(source_path,source_encoding):
    
        with open(source_path, 'r',encoding=source_encoding,errors="ignore") as file:
            content = file.read()
            return content
        return None
    
# 写到文件
@cd.exception_decorator()
def write_content_by_encode(dest_path,dest_encoding,content):
    #不存在时 就创建
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w',encoding=dest_encoding) as file:
        file.write(content)


# @cd.details_decorator
# @cd.timer_decorator
@cd.exception_decorator()
def  operate_content_diff_encode( source_path,dest_path,source_encoding,dest_encoding="",operate_fun=None):
        content=read_content_by_encode(source_path,source_encoding)
        if content is None:
            return 
        
        is_same=True
        if operate_fun:
            result_content=operate_fun(content)
            if result_content ==content:
                if logger:
                    logger.trace(f"{source_path}:内容未被修改,保留原始内容")
            else:
                is_same=False
                content=result_content

        if dest_encoding=="":
            dest_encoding=source_encoding
        # 将处理后的content保存到B.txt文件中
        write_content_by_encode(dest_path,dest_encoding,content)

def replace_content_diff_encode( source_path,dest_path,source_encoding, dest_encoding="",replace_list_tuple=None):

    def replace_content(content:str)->str:
        return st.replace_list_tuple_str(content,replace_list_tuple)
    if dest_encoding=="":
        dest_encoding=source_encoding 
    operate_content_diff_encode(source_path, dest_path,source_encoding,dest_encoding,replace_content)

def operate_content_same_encode( source_path,dest_path,encoding, operate_fun):
    operate_content_diff_encode(source_path, dest_path,encoding, encoding,operate_fun)

def replace_content_same_encode( source_path,dest_path,encoding, replace_list_tuple):
    replace_content_diff_encode(source_path, dest_path,encoding,encoding,replace_list_tuple)


def convert_encode(source_path,dest_path,source_encoding,dest_encoding):
    operate_content_diff_encode(source_path, dest_path,source_encoding,dest_encoding,None)

#按推断的编码读入文件
def read_content(source_path):
    source_encoding = detect_encoding(source_path)
    with open(source_path, 'r',encoding=source_encoding) as file:
        content = file.read()
        return content
    return None



#异步读、写文件
async def read_write_async(data,dest_path,mode="w",encoding=None):
    operator="写入" if mode.find("w")>=0 else "读取"

    
    target=f"异步{operator}文件,mode:{mode},encoding:{encoding}"
    detail=f"{dest_path}"
    start_time=time.time()
    logger.trace(record_detail(target,"开始",detail))
    
    try:
        async with  aiofiles.open(dest_path,mode,encoding=encoding) as f:
            await f.write(data)
            logger.trace(record_detail(target,"完成",f"{usage_time(start_time)}, {detail}"))
            return True
    except:
        return False

#同步读、写文件
def read_write_sync(data,dest_path,mode="w",encoding=None):
    operator="写入" if mode.find("w")>=0 else "读取"

    
    target=f"同步{operator}文件,mode:{mode},encoding:{encoding}"
    detail=f"{dest_path}"
    start_time=time.time()
    logger.trace(record_detail(target,"开始",detail))
    
    try:
        with  open(dest_path,mode,encoding=encoding) as f:
            f.write(data)
            logger.trace(record_detail(target,"完成",f"{usage_time(start_time)}, {detail}"))
            return True
    except:
        return False



async def __fetch_async(url ,session,max_retries=3,**args):
    retries = 0
    while retries < max_retries:
        try:
            async with session.get(url,**args) as response:
                if response.status == 200:
                    content_length = int(response.headers.get('Content-Length', 0))
                    received_data = await response.read()
                    if len(received_data) == content_length:
                        return received_data
                    else:
                        raise aiohttp.ClientError(
                            response.status,
                            "Not enough data for satisfy content length header."
                        )
                else:
                    raise Exception(f"HTTP error: {response.status}")
        except aiohttp.ClientError as e:
            logger.error(record_detail(f"异步获取资源{url}" ,"失败",  f"{retries} times,Request failed: {e}"))
            retries += 1
            await asyncio.sleep(5)  # 等待 5 秒后重试
    return None
    # raise Exception("Max retries exceeded")



        
async def download_async(url,dest_path,**kwargs):
    
    target="异步下载文件"
    detail=f"{url} -> {dest_path}"
    logger.trace(record_detail(target,"开始",detail))
    start_time=time.time()
    
    
    async with aiohttp.ClientSession() as session:
        content=await __fetch_async(url,session,5,**kwargs)
        if not content:
            logger.error(record_detail(target,"失败",f"{usage_time(start_time)}, {detail}"))
            return False
            
        await read_write_async(content,dest_path,mode="wb")
        
    logger.trace(record_detail(target,"完成",f"{usage_time(start_time)}, {detail}"))
    return True
def __fetch_sync(url ,max_retries=3,**args):
    retries = 0
    while retries < max_retries:
        try:
            with requests.get(url,**args) as response:

                if response.status_code == 200:
                    hearders=response.headers
                    content_length=int(hearders.get('Content-Length', 0))
                    received_data =  response.content
                    if (content_length == 0) or (len(received_data) == content_length):
                        return received_data
                    else:
                        raise requests.exceptions.ConnectionError(
                            response.status,
                            "Not enough data for satisfy content length header."
                        )
                else:
                    raise Exception(f"HTTP error: {response.status}")
        except requests.exceptions.ConnectionError as e:
            logger.error(record_detail(f"同步获取资源{url}" ,"失败",  f"{retries} times,Request failed: {e}"))
            retries += 1
            time.sleep(5)  # 等待 5 秒后重试
    return None
        
def download_sync(url,dest_path,**kwargs):
    
    target="同步下载文件"
    detail=f"{url} -> {dest_path}"
    logger.trace(record_detail(target,"开始",detail))

    start_time=time.time()
    content=__fetch_sync(url,5,**kwargs)
    if not content:
        logger.error(record_detail(target,"失败",f"{usage_time(start_time)}, {detail}"))
        return False
        
    read_write_sync(content,dest_path,mode="wb")
        
    logger.trace(record_detail(target,"完成",f"{usage_time(start_time)}, {detail}"))
    return True



if __name__ == '__main__':

    replace_tuples=[
    ('法撒', 'A'),
    ('潍坊', 'CDE')
    ]



    replace_content_same_encode(r'F:\test_data\gbk.cpp',r'F:\test_data_output\gbk.cpp', "utf-8-sig", replace_tuples)
