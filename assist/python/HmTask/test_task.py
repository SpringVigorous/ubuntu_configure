
import asyncio
import threading
import multiprocessing
import queue
import aiohttp
from base_task import *



class FetchData(CoroutineTask):


    async def handle_data(self, data):
        # 示例异步处理逻辑
        async with aiohttp.ClientSession() as session:
            async with session.get(data) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"请求错误: {response.status}")
                    return None

class DownloadData(ThreadTask):
    def __init__(self, data_queue, file_path, file_queue, event):
        super().__init__(data_queue, file_queue, event)
        self.file_path = file_path

    def handle_data(self, data):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(data)
                print(f"数据已保存到 {self.file_path}")
                return self.file_path
        except IOError as e:
            print(f"写入文件错误: {e}")
            return None

class TransformData(ProcessTask):
    def handle_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 假设我们只是简单地将所有内容转为大写作为转换操作
                transformed_content = content.upper()
                print("转换后的数据:", transformed_content)
                return transformed_content
        except IOError as e:
            print(f"读取文件错误: {e}")
            return None

class MainWorkflow:
    def __init__(self):
        self.url_queue = asyncio.Queue()
        self.data_queue = queue.Queue()
        self.file_queue = multiprocessing.Queue()

        self.fetch_event = asyncio.Event()
        self.download_event = threading.Event()
        self.transform_event = multiprocessing.Event()
    async def run(self):
        # 添加初始URL
        urls = ["http://example.com/data1.json", "http://example.com/data2.json", "http://example.com/data3.json"]
        for url in urls:
            await self.url_queue.put(url)

        # 创建协程任务
        fetcher = FetchData(self.url_queue, self.data_queue, self.fetch_event)
        fetch_task = asyncio.create_task(fetcher.run())

        # 创建下载线程
        downloader = DownloadData(self.data_queue, "data.txt", self.file_queue, self.download_event)
        downloader.start()

        # 创建转换子进程
        transformer = TransformData(self.file_queue, self.transform_event)
        transformer.start()

        # 动态添加新的URL
        new_urls = ["http://example.com/data4.json", "http://example.com/data5.json"]
        for url in new_urls:
            await self.url_queue.put(url)

        try:
            # 等待所有URL采集任务完成
            await self.url_queue.join()
        except Exception as e:
            print(f"等待URL采集任务完成时发生异常: {e}")

        try:
            # 设置采集信号
            self.fetch_event.set()  # 设置采集信号
        except Exception as e:
            print(f"设置采集信号时发生异常: {e}")

        try:
            # 等待所有数据下载任务完成
            self.data_queue.join()
        except Exception as e:
            print(f"等待数据下载任务完成时发生异常: {e}")

        try:
            # 设置下载和转换事件
            self.download_event.set()
            self.transform_event.set()
        except Exception as e:
            print(f"设置下载和转换事件时发生异常: {e}")

        try:
            # 等待所有文件转换任务完成
            self.file_queue.join()
        except Exception as e:
            print(f"等待文件转换任务完成时发生异常: {e}")

# 运行主工作流
asyncio.run(MainWorkflow().run())