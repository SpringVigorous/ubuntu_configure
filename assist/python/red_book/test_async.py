import os
import asyncio
import aiohttp
import queue

# 定义采集协程
async def fetch_data(url_queue, data_queue, event):
    """从URL队列中获取URL并采集数据，放入数据队列"""
    while not event.is_set():
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
        except queue.Empty:
            continue

# 定义下载协程
async def download_data(data_queue, file_path, event):
    """从数据队列中获取数据并保存到指定路径"""
    while not event.is_set():
        try:
            data = await data_queue.get()  # 阻塞等待数据
            if data is not None:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(data)
                    print(f"数据已保存到 {file_path}")
                except IOError as e:
                    print(f"写入文件错误: {e}")
                finally:
                    file_queue.put(file_path)  # 将文件路径放入文件队列
        finally:
            data_queue.task_done()  # 标记数据任务完成

# 定义转换协程
async def transform_data(file_queue, event):
    """从文件队列中获取文件路径，并读取文件内容进行转换"""
    while not event.is_set():
        try:
            file_path = await file_queue.get()  # 阻塞等待文件路径
            if file_path is not None:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 假设我们只是简单地将所有内容转为大写作为转换操作
                        transformed_content = content.upper()
                        print("转换后的数据:", transformed_content)
                except IOError as e:
                    print(f"读取文件错误: {e}")
        finally:
            file_queue.task_done()  # 标记文件任务完成

# 主流程
async def main():
    # 创建队列
    url_queue = asyncio.Queue()
    data_queue = asyncio.Queue()
    file_queue = asyncio.Queue()

    # 创建事件
    fetch_event = asyncio.Event()
    download_event = asyncio.Event()
    transform_event = asyncio.Event()

    # 添加初始URL
    urls = ["http://example.com/data1.json", "http://example.com/data2.json", "http://example.com/data3.json"]
    for url in urls:
        await url_queue.put(url)

    # 创建协程任务
    fetch_task = asyncio.create_task(fetch_data(url_queue, data_queue, fetch_event))
    download_task = asyncio.create_task(download_data(data_queue, "data.txt", download_event))
    transform_task = asyncio.create_task(transform_data(file_queue, transform_event))

    # 动态添加新的URL
    new_urls = ["http://example.com/data4.json", "http://example.com/data5.json"]
    for url in new_urls:
        await url_queue.put(url)

    # 设置采集信号
    fetch_event.set()  # 设置采集信号

    # 等待所有采集任务完成
    await url_queue.join()

    # 设置下载和转换事件
    download_event.set()
    transform_event.set()

    # 等待下载和转换任务完成
    await data_queue.join()
    await file_queue.join()

    # 取消协程任务
    fetch_task.cancel()
    download_task.cancel()
    transform_task.cancel()

    await fetch_task
    await download_task
    await transform_task

    print("所有任务已完成")

# 运行主流程
if __name__ == "__main__":
    asyncio.run(main())