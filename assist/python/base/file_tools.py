import string_tools as st
import path_tools as pt
import com_decorator as cd 
from com_log import logger_helper,UpdateTimeType
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
from collect_tools import unique
# 使用chardet模块检测文件的编码
def detect_encoding(file_path)->str:
    detect_logger= logger_helper("检测文件编码",file_path)
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    if not result:
        return ReturnState.FAILED
    detect_logger.trace("成功",result,update_time_type=UpdateTimeType.ALL)
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
        
        content_logger=logger_helper("操作文件内容",f"{source_path} -> {dest_path}")
        same_path_encoding= st.equal_ignore_case(source_encoding,dest_encoding) and pt.path_equal(source_path,dest_path)
        if same_path_encoding and not operate_fun:
            content_logger.trace("忽略", "路径相同，编码相同，未指定操作函数,跳过后续处理")
            return ReturnState.IGNORE
            
    
        content=read_content_by_encode(source_path,source_encoding)
        if not content :
            return content
        
        is_same=True
        if operate_fun:
            result_content=operate_fun(content)
            if result_content ==content:
                if content_logger:
                    content_logger.trace("忽略","内容未被修改,保留原始内容")
            else:
                is_same=False
                content=result_content

        if same_path_encoding and is_same:
            content_logger.trace("忽略","路径相同，编码相同，指定操作后内容未修改,跳过后续处理")
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
    as_write= mode.find("w")>=0
    operator="写入" if as_write else "读取"

    encode_val=f",encoding:{encoding}" if encoding else ""
    
    async_logger=logger_helper(f"异步{operator}->{dest_path}",f"mode:{mode}{encode_val}")

    # async_logger.trace("开始")
    
    try:
        async with  aiofiles.open(dest_path,mode,encoding=encoding) as f:
            if as_write:
                await f.write(data)
            else:
                data=await f.read()
            # async_logger.trace("完成",update_time_type=UpdateTimeType.ALL)
            return True if as_write else data
    except:
        async_logger.error("失败",update_time_type=UpdateTimeType.ALL)
        return False

#同步读、写文件
def read_write_sync(data, dest_path, mode="w", encoding=None):
    # 检查模式是否包含写入操作
    is_write = 'w' in mode
    operation = "写入" if is_write else "读取"

    # 格式化日志信息
    log_message = f"mode:{mode},encoding:{encoding}"
    sync_logger = logger_helper(f"同步{operation}->{dest_path}", log_message)

    # sync_logger.trace("开始")

    try:
        with open(dest_path, mode, encoding=encoding) as f:
            if is_write:
                f.write(data)
                result = True
            else:
                result = f.read()
            # sync_logger.trace("完成", update_time_type=UpdateTimeType.ALL)
            return result
    except Exception as e:
        # 记录具体的错误信息
        sync_logger.error(f"失败: {str(e)}", update_time_type=UpdateTimeType.ALL)
        return False


async def read_async(dest_path,mode="r",encoding=None):
    return await read_write_async(None,dest_path,mode,encoding)

async def write_async(data,dest_path,mode="w",encoding=None):
    return await read_write_async(data,dest_path,mode,encoding)

def read_sync(dest_path,mode="r",encoding=None):
    return read_write_sync(None,dest_path,mode,encoding)

def write_sync(data,dest_path,mode="w",encoding=None):
    return read_write_sync(data,dest_path,mode,encoding)



async def __fetch_async(url ,session,max_retries=3,**args):
    async_logger=logger_helper("异步获取资源",url)
    retries = 0
    while retries < max_retries:
        try:
            async with session.get(url,**args) as response:
                if response.status == 200:
                    content_length = int(response.headers.get('Content-Length', 0))
                    received_data = await response.read()
                    if len(received_data) == content_length:
                        async_logger.trace("成功", update_time_type=UpdateTimeType.ALL)
                        return received_data
                    else:
                        raise aiohttp.ClientError(
                            response.status,
                            "Not enough data for satisfy content length header."
                        )
                else:
                    raise Exception(f"HTTP error: {response.status}")
        except aiohttp.ClientError as e:
            async_logger.error("失败",  f"{retries+1} times,Request failed: {except_stack()}",UpdateTimeType.ALL)
            retries += 1
            await asyncio.sleep(5)  # 等待 5 秒后重试
    return None
    # raise Exception("Max retries exceeded")


async def _download_async(session:aiohttp.ClientSession,url,dest_path,lat_fun=None,covered=False,**kwargs):
    if os.path.exists(dest_path) and not covered:
        return True

    async_logger=logger_helper("异步下载文件",f"{url} -> {dest_path}")
    # async_logger.trace("开始")
    start_time=time.time()
    # content=await __fetch_async(url,session,3,timout=timout,**kwargs)
    content=await __fetch_async(url,session,3,**kwargs)
    if not content:
        async_logger.error("失败",update_time_type=UpdateTimeType.ALL)
        return False
        # count=len(content)
        content=lat_fun(content)
        # async_logger.trace(f"pre-{count},latter-{len(content)}" )
        
    await read_write_async(content,dest_path,mode="wb")
        
    # async_logger.trace("完成",update_time_type=UpdateTimeType.ALL)
    return True
        
async def download_async(url,dest_path,lat_fun=None,covered=False,**kwargs):
    
    async with aiohttp.ClientSession() as session:
        result= await _download_async(session,url,dest_path,lat_fun,covered,**kwargs)
        return result



async def downloads_async(urls,dest_paths,lat_fun=None,covered=False,**kwargs):
    
    async with aiohttp.ClientSession() as session:
        tasks = [_download_async(session,url, dest_path, lat_fun,covered,**kwargs) for url, dest_path in zip(urls, dest_paths)]
        await asyncio.gather(*tasks)

def fetch_sync(url ,max_retries=5,timeout=300,**args):
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
                            response.status_code,
                            "Not enough data for satisfy content length header."
                        )
                else:
                    raise Exception(f"HTTP error: {response.status_code}")
                
                
                
        except requests.exceptions.ConnectionError as e:
            fetch_logger.error("失败",  f"{retries+1} times,Request failed: {except_stack()}",update_time_type=UpdateTimeType.STEP)
            retries += 1
            time.sleep(5)  # 等待 5 秒后重试
            timeout+=30
        except:
            pass
            
    fetch_logger.error("失败",  f"{retries+1} times,Request failed: {except_stack()}",update_time_type=UpdateTimeType.ALL)
    return None
        
def download_sync(url,dest_path,lat_fun=None,covered=False,**kwargs):
    if os.path.exists(dest_path) and not covered:
        return True
    download_logger= logger_helper("同步下载文件",f"{url} -> {dest_path}")
    

    download_logger.trace("开始")

    start_time=time.time()
    content=fetch_sync(url,2,timeout=300,**kwargs)
    if not content:
        download_logger.error("失败",update_time_type=UpdateTimeType.ALL)
        return False
    if lat_fun:
        content=lat_fun(content)
    read_write_sync(content,dest_path,mode="wb")
        
    download_logger.info("完成",update_time_type=UpdateTimeType.ALL)
    return True


def move_file(source_file,destination_file):
    move_logger= logger_helper("移动文件",f"{source_file} -> {destination_file}")
    # 移动文件
    try:
        result= shutil.move(source_file, destination_file)
        move_logger.info("成功")
    except FileNotFoundError:
        move_logger.error("失败",f"{source_file} 不存在")
    except PermissionError:
        move_logger.error("失败",f"{source_file} 权限不够")
    except Exception as e:
        move_logger.error("失败",except_stack())    

def copy_file(source_file:str|list[str],destination_file:str|list[str]):
    
    if isinstance(source_file,str):
        source_file=[source_file]
        
    if isinstance(destination_file,str):
        destination_file=[destination_file]*len(source_file)
    logger= logger_helper("拷贝参数",f"{"\n".join(unique(source_file))}\n -> \n{"\n".join(unique(destination_file))}\n")
    logger.trace("开始")
    for file,dest in zip(source_file,destination_file):
        copy_logger= logger_helper("拷贝文件",f"{file} -> {dest}")
        # 拷贝文件
        try:
            result= shutil.copy2(file, dest)
            copy_logger.trace("成功")
        except FileNotFoundError:
            copy_logger.error("失败",f"{file} 不存在")
        except PermissionError:
            copy_logger.error("失败",f"{file} 权限不够")
        except Exception as e:
            copy_logger.error("失败",except_stack())    
    logger.info("完成",update_time_type=UpdateTimeType.ALL)


def priority_read(file_path,readfunc,operator_func=None,writefunc=None):
    data=None
    if os.path.exists(file_path) and readfunc:
        data=readfunc(file_path)
        print(type(data))
        if data is not None:
            return data
    data=operator_func()  if operator_func else None
     
    if writefunc :
        writefunc(file_path,data)
    return data

def write_dataframe_excel(file_path,data,sheet_name=None):
    import pandas as pd
    
    if not isinstance(data,pd.DataFrame):
        data=pd.DataFrame(data)
    if sheet_name:
        return data.to_excel(file_path,sheet_name=sheet_name)
        
    return data.to_excel(file_path)

def write_to_json(file_path,data,**file_kwargs):
    import json

    return json.dump(data,open(file_path,"w",**file_kwargs),indent=4,ensure_ascii=False)


def write_to_txt(file_path,data,**file_kwargs):
    return open(file_path,"w",**file_kwargs).write(data)


def priority_read_excel_by_pandas(file_path,operator_func=None,sheet_name=None):
    import pandas as pd
    
    readfunc=lambda file_path:pd.read_excel(file_path,sheet_name=sheet_name) if sheet_name else pd.read_excel(file_path)
    writeFunc=lambda file_path,df : write_dataframe_excel(file_path,df,sheet_name=sheet_name)

    return priority_read(file_path,readfunc,operator_func,writeFunc)



def priority_read_json(file_path,operator_func=None,**file_kwargs):
    import json
    readfunc=lambda file_path:json.load(open(file_path,"r",**file_kwargs))
    writefunc=lambda file_path,data :write_to_json(file_path,data,**file_kwargs)
    return priority_read(file_path,readfunc,operator_func,writefunc)

def priority_read_txt(file_path,operator_func=None,**file_kwargs):
    readfunc=lambda file_path:open(file_path,"r",**file_kwargs).read()


    writefunc=lambda file_path,data :write_to_txt(file_path,data,**file_kwargs)
    return priority_read(file_path,readfunc,operator_func,writefunc)
    
    

if __name__ == '__main__':

    replace_tuples=[
    ('法撒', 'A'),
    ('潍坊', 'CDE')
    ]



    # replace_content_same_encode(r'F:\test_data\gbk.cpp',r'F:\test_data_output\gbk.cpp', "utf-8-sig", replace_tuples)
    
    
