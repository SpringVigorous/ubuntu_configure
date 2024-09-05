﻿import os
import asyncio
import threading
import multiprocessing
import requests
import queue
import aiohttp

# 定义采集协程
async def fetch_data(url_queue, data_queue, event):
    """从URL队列中获取URL并采集数据，放入数据队列"""
    while not event.is_set() or not url_queue.empty():
        try:
            url = await url_queue.get()  # 阻塞等待URL
            if url is not None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.text()
                            data_queue.put(data)
                        else:
                            print(f"请求错误: {response.status}")
                            data_queue.put(None)
                url_queue.task_done()  # 标记URL任务完成
        except Exception as e:
            print(f"采集数据时发生异常: {e}")

# 定义下载线程
def download_data(data_queue, file_path, file_queue, event):
    """从数据队列中获取数据并保存到指定路径"""
    while not event.is_set() or not data_queue.empty():
        try:
            data = data_queue.get(timeout=1)  # 阻塞等待数据
            if data is not None:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(data)
                    print(f"数据已保存到 {file_path}")
                except IOError as e:
                    print(f"写入文件错误: {e}")
                finally:
                    file_queue.put(file_path)  # 将文件路径放入文件队列
        except queue.Empty:
            continue
        except Exception as e:
            print(f"下载数据时发生异常: {e}")
        finally:
            data_queue.task_done()  # 标记数据任务完成

# 定义转换子进程
def transform_data(file_queue, event):
    """从文件队列中获取文件路径，并读取文件内容进行转换"""
    while not event.is_set() or not file_queue.empty():
        try:
            file_path = file_queue.get(timeout=1)  # 阻塞等待文件路径
            if file_path is not None:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 假设我们只是简单地将所有内容转为大写作为转换操作
                        transformed_content = content.upper()
                        print("转换后的数据:", transformed_content)
                except IOError as e:
                    print(f"读取文件错误: {e}")
        except queue.Empty:
            continue
        except Exception as e:
            print(f"转换数据时发生异常: {e}")
        finally:
            file_queue.task_done()  # 标记文件任务完成

# 主流程
async def main():
    # 创建队列
    url_queue = asyncio.Queue()
    data_queue = queue.Queue()
    file_queue = multiprocessing.Queue()

    # 创建事件
    fetch_event = asyncio.Event()
    download_event = threading.Event()
    transform_event = multiprocessing.Event()

    # 添加初始URL
    urls = ["http://example.com/data1.json", "http://example.com/data2.json", "http://example.com/data3.json"]
    for url in urls:
        await url_queue.put(url)

    # 创建协程任务
    fetch_task = asyncio.create_task(fetch_data(url_queue, data_queue, fetch_event))

    # 创建下载线程
    download_thread = threading.Thread(target=download_data, args=(data_queue, "data.txt", file_queue, download_event))
    download_thread.start()

    # 创建转换子进程
    transform_process = multiprocessing.Process(target=transform_data, args=(file_queue, transform_event))
    transform_process.start()

    # 动态添加新的URL
    new_urls = ["http://example.com/data4.json", "http://example.com/data5.json"]
    for url in new_urls:
        await url_queue.put(url)

    try:
        # 等待所有URL采集任务完成
        await url_queue.join()
    except Exception as e:
        print(f"等待URL采集任务完成时发生异常: {e}")

    try:
        # 设置采集信号
        fetch_event.set()  # 设置采集信号
    except Exception as e:
        print(f"设置采集信号时发生异常: {e}")

    try:
        # 等待所有数据下载任务完成
        data_queue.join()
    except Exception as e:
        print(f"等待数据下载任务完成时发生异常: {e}")

    try:
        # 设置下载和转换事件
        download_event.set()
        transform_event.set()
    except Exception as e:
        print(f"设置下载和转换事件时发生异常: {e}")

    try:
        # 等待下载线程完成
        download_thread.join()
    except Exception as e:
        print(f"等待下载线程完成时发生异常: {e}")

    try:
        # 等待转换子进程完成
        file_queue.join()
        transform_process.join()
    except Exception as e:
        print(f"等待转换子进程完成时发生异常: {e}")

    try:
        # 取消协程任务
        fetch_task.cancel()
        await fetch_task
    except Exception as e:
        print(f"取消协程任务时发生异常: {e}")

    print("所有任务已完成")

# 运行主流程
if __name__ == "__main__":
    asyncio.run(main())