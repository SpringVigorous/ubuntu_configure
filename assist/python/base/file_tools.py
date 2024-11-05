import string_tools as st
import path_tools as pt
import com_decorator as cd 
from com_log import logger,record_detail,usage_time,logger_helper,record_detail_usage,UpdateTimeType
from except_tools import except_stack
import chardet
import asyncio
import aiohttp
import aiofiles
import requests
import time
import os
from state import ReturnState
import shutil
# 使用chardet模块检测文件的编码
def detect_encoding(file_path)->str:
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    if not result:
        return ReturnState.FAILED
    logger.trace(f" {file_path} 检测到文件编码：{result}")
    # 返回检测到的编码
    encoding=result['encoding']
    if encoding:
        return encoding.lower()
    else:
        return ReturnState.FAILED



#读入文件
@cd.exception_decorator()
def read_content_by_encode(source_path,source_encoding):
    
        with open(source_path, 'r',encoding=source_encoding,errors="ignore") as file:
            content = file.read()
            return content

    
# 写到文件
@cd.exception_decorator()
def write_content_by_encode(dest_path,dest_encoding,content):
    #不存在时 就创建
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w',encoding=dest_encoding) as file:
        file.write(content)
    return ReturnState.SUCCESS


# @cd.details_decorator
# @cd.timer_decorator
@cd.exception_decorator()
def  operate_content_diff_encode( source_path,dest_path,source_encoding,dest_encoding="",operate_fun=None):
        if not dest_encoding:
            dest_encoding=source_encoding
        
        same_path_encoding= st.equal_ignore_case(source_encoding,dest_encoding) and pt.path_equal(source_path,dest_path)
        if same_path_encoding and not operate_fun:
            logger.trace(f"{source_path}路径相同，编码相同，未指定操作函数,跳过后续处理")
            return ReturnState.IGNORE
            
    
        content=read_content_by_encode(source_path,source_encoding)
        if not content :
            return content
        
        is_same=True
        if operate_fun:
            result_content=operate_fun(content)
            if result_content ==content:
                if logger:
                    logger.trace(f"{source_path}:内容未被修改,保留原始内容")
            else:
                is_same=False
                content=result_content

        if same_path_encoding and is_same:
            logger.trace(f"{source_path}路径相同，编码相同，指定操作后内容未修改,跳过后续处理")
            return ReturnState.IGNORE
            
        # 将处理后的content保存到B.txt文件中
        return write_content_by_encode(dest_path,dest_encoding,content)

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
    if not source_encoding:
        return None
    
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
            logger.trace(record_detail(target,"完成",f"{detail},{usage_time(start_time)}"))
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
            logger.trace(record_detail(target,"完成",f"{detail},{usage_time(start_time)}"))
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



        
async def download_async(url,dest_path,timout=60,**kwargs):
    
    target="异步下载文件"
    detail=f"{url} -> {dest_path}"
    logger.trace(record_detail(target,"开始",detail))
    start_time=time.time()
    
    
    async with aiohttp.ClientSession() as session:
        content=await __fetch_async(url,session,5,timout=timout,**kwargs)
        if not content:
            logger.error(record_detail(target,"失败",f"{detail},{usage_time(start_time)}"))
            return False
            
        await read_write_async(content,dest_path,mode="wb")
        
    logger.trace(record_detail(target,"完成",f"{detail},{usage_time(start_time)}"))
    return True
def fetch_sync(url ,max_retries=5,timeout=60,**args):
    """
    从给定的 URL 获取内容，支持重试机制和超时设置。

    :param url: 要请求的 URL
    :param timeout: 请求超时时间，默认为 60 秒
    :param max_retries: 最大重试次数，默认为 5
    :return: 请求的响应内容
    """
    fetch_logger=logger_helper("同步获取资源",url)
    fetch_logger.trace("开始")
    retries = 0
    while retries < max_retries:
        try:
            with requests.get(url,timeout=timeout,**args) as response:

                if response.status_code == 200:
                    hearders=response.headers
                    content_length=int(hearders.get('Content-Length', 0))
                    received_data =  response.content
                    if (content_length == 0) or (len(received_data) == content_length):
                        fetch_logger.trace("成功", update_time_type=UpdateTimeType.ALL)
                        return received_data
                    else:
                        raise requests.exceptions.ConnectionError(
                            response.status,
                            "Not enough data for satisfy content length header."
                        )
                else:
                    raise Exception(f"HTTP error: {response.status}")
                
                
                
        except requests.exceptions.ConnectionError as e:
            fetch_logger.error("失败",  f"{retries} times,Request failed: {except_stack()}",update_time_type=UpdateTimeType.STEP)
            retries += 1
            time.sleep(5)  # 等待 5 秒后重试
            timeout+=30
            
    fetch_logger.error("失败",  f"{retries} times,Request failed: {except_stack()}",update_time_type=UpdateTimeType.ALL)
    return None
        
def download_sync(url,dest_path,covered=False,**kwargs):
    if os.path.exists(dest_path) and not covered:
        return True
    download_logger= logger_helper("同步下载文件",f"{url} -> {dest_path}")
    

    download_logger.trace("开始")

    start_time=time.time()
    content=__fetch_sync(url,5,timeout=60,**kwargs)
    if not content:
        download_logger.error("失败",update_time_type=UpdateTimeType.ALL)
        return False
        
    read_write_sync(content,dest_path,mode="wb")
        
    download_logger.trace("完成",update_time_type=UpdateTimeType.ALL)
    return True


def move_file(source_file,destination_file):
    move_logger= logger_helper("移动文件",f"{source_file} -> {destination_file}")
    # 移动文件
    try:
        shutil.move(source_file, destination_file)
        move_logger.trace("成功")
    except FileNotFoundError:
        move_logger.error("失败",f"{source_file} 不存在")
    except PermissionError:
        move_logger.error("失败",f"{source_file} 权限不够")
    except Exception as e:
        move_logger.error("失败",except_stack())    


if __name__ == '__main__':

    replace_tuples=[
    ('法撒', 'A'),
    ('潍坊', 'CDE')
    ]



    replace_content_same_encode(r'F:\test_data\gbk.cpp',r'F:\test_data_output\gbk.cpp', "utf-8-sig", replace_tuples)
