import abc
import asyncio
import threading
import multiprocessing
import queue
import aiohttp

class BaseTask(metaclass=abc.ABCMeta):
    def __init__(self, input_queue, output_queue, event):
        self.event = event
        self.input_queue = input_queue
        self.output_queue = output_queue

    @abc.abstractmethod
    def handle_data(self, data):
        raise NotImplementedError("Subclasses must implement this method")

    @abc.abstractmethod
    async def async_handle_data(self, data):
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def stop(self):
        return  not self.event or self.event.is_set()
    def _imp_run(self):
        while not(self.stop and  self.input_queue.empty()):
            input_data = self.pop_data()
            if input_data is None:
                continue
            output_data = self.handle_data(input_data)
            if output_data:
                self.push_data(output_data)

    async def _imp_async(self):
        while not self.event.is_set() or not self.input_queue.empty():
            input_data = await self.async_pop()
            if input_data is None:
                continue
            output_data = await self.async_handle_data(input_data)
            if output_data:
                await self.async_push(output_data)

    async def async_run(self):
        while not self.event.is_set() or not self.input_queue.empty():
            try:
                await self._imp_async()
            except Exception as e:
                print(f"处理数据时发生异常: {e}")

    def run(self):
        while not self.event.is_set() or not self.input_queue.empty():
            try:
                self._imp_run()
            except Exception as e:
                print(f"处理数据时发生异常: {e}")

    def pop_data(self):
        try:
            data = self.input_queue.get(timeout=1)  # 阻塞等待数据
            self.input_queue.task_done()  # 标记数据任务完成
            return data
        except queue.Empty:
            return None
        except Exception as e:
            print(f"获取输入数据时发生异常: {e}")
            return None

    def push_data(self, data):
        try:
            self.output_queue.put(data)
        except Exception as e:
            print(f"输出数据时发生异常: {e}")

    async def async_pop(self):
        try:
            data = await self.input_queue.get()  # 阻塞等待数据
            self.input_queue.task_done()  # 标记数据任务完成
            return data
        except Exception as e:
            print(f"获取输入数据时发生异常: {e}")
            return None

    async def async_push(self, data):
        try:
            await self.output_queue.put(data)
        except Exception as e:
            print(f"输出数据时发生异常: {e}")

class AsyncTask(BaseTask):
    async def async_handle_data(self, data):
        # 示例异步处理逻辑
        await asyncio.sleep(1)  # 模拟耗时操作
        return f"Processed: {data}"

class ThreadTask(BaseTask, threading.Thread):
    def handle_data(self, data):
        # 示例同步处理逻辑
        return f"Processed: {data}"

class ProcessTask(BaseTask, multiprocessing.Process):
    def handle_data(self, data):
        # 示例同步处理逻辑
        return f"Processed: {data}"

class FetchData(AsyncTask):
    def __init__(self, url_queue, data_queue, event):
        super().__init__(url_queue, data_queue, event)
        self.url_queue = url_queue
        self.data_queue = data_queue

    async def _imp_async(self):
        try:
            url = await self.async_pop()
            if url is not None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.text()
                            await self.async_push(data)
                        else:
                            print(f"请求错误: {response.status}")
                            await self.async_push(None)
        except Exception as e:
            print(f"采集数据时发生异常: {e}")

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
        fetch_task = asyncio.create_task(fetcher.async_run())

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