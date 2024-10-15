import pandas as pd
import os
import requests
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont
from abc import ABC, abstractmethod
from pathlib import Path
import logging
import configparser

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件读取配置项
download_dir_name = config.get('directories', 'download_dir')
final_dir_name = config.get('directories', 'final_dir')
max_download_workers = config.getint('threading', 'max_download_workers')
max_conversion_workers = config.getint('threading', 'max_conversion_workers')

# 定义下载函数
def download_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        with open(local_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"下载完成: {local_path}")
        return local_path
    except Exception as e:
        logging.error(f"下载失败: {url} -> {local_path}, 错误: {e}")
        return None

# 定义转换和添加文字的函数
def convert_and_add_text(src_path, final_path):
    try:
        # 读取图片
        img = Image.open(src_path).convert('RGBA')

        # 获取图片尺寸
        width, height = img.size

        # 提取文件名中的文本
        filename = os.path.basename(final_path)
        text = filename.split('_')[0].split('-')[1]

        # 设置字体和文字高度
        font_path = r"C:\Windows\Fonts\STKAITI.TTF"  # 华文楷体字体路径
        font = ImageFont.truetype(font_path, 30)

        # 计算文字的位置
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 确保文字宽度不超过图片宽度
        if text_width > width:
            font = ImageFont.truetype(font_path, int(20 * (width / text_width)))

        # 计算文字的位置
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = height - text_height - 15  # 文字距离底部的距离

        # 创建带有透明背景的新图像
        text_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)

        # 添加文字
        draw.text((0, 0), text, fill=(255, 255, 255, 255), font=font)

        # 将带有文字的透明图像与原始图像合并
        img.paste(text_img, (text_x, text_y), text_img)

        # 保存最终图片
        img = img.convert('RGB')
        img.save(final_path, format='JPEG')
        # os.remove(src_path)
        logging.info(f"转换并添加文字完成: {final_path}")
    except Exception as e:
        logging.error(f"转换并添加文字失败: {src_path} -> {final_path}, 错误: {e}")

# 定义基类
class BaseWorkerThread(Thread, ABC):
    def __init__(self, task_queue, max_workers):
        super().__init__()
        self.task_queue = task_queue
        self.max_workers = max_workers

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            self.execute_tasks(executor)

    @abstractmethod
    def execute_tasks(self, executor):
        pass

# 定义生产者基类
class ProducerThreadBase(BaseWorkerThread, ABC):
    def __init__(self, task_queue, max_workers, items):
        super().__init__(task_queue, max_workers)
        self.items = items

    def execute_tasks(self, executor):
        for item in self.items:
            self.execute_task(item, executor)

    @abstractmethod
    def execute_task(self, item, executor):
        pass

# 定义消费者基类
class ConsumerThreadBase(BaseWorkerThread, ABC):
    def execute_tasks(self, executor):
        while True:
            try:
                item = self.task_queue.get(timeout=1)
                self.execute_task(item, executor)
                self.task_queue.task_done()
            except Empty:
                break

    @abstractmethod
    def execute_task(self, item, executor):
        pass

# 定义生产者线程类
class CustomProducerThread(ProducerThreadBase):
    def __init__(self, urls, names, max_download_workers, download_dir, final_dir, task_queue):
        items = list(zip(urls, names))
        super().__init__(task_queue, max_download_workers, items)
        self.download_dir = download_dir
        self.final_dir = final_dir

    def execute_task(self, item, executor):
        url, name = item
        file_name = name + ".jpg"
        cur_path = os.path.join(self.download_dir, file_name)
        final_path = os.path.join(self.final_dir, file_name)

        if os.path.exists(final_path):
            logging.info(f"最终文件已存在: {final_path}")
            return

        if os.path.exists(cur_path):
            # 如果临时文件存在，则直接提交转换任务
            self.task_queue.put((cur_path, final_path))
        else:
            # 否则提交下载任务，并添加回调函数
            future = executor.submit(download_file, url, cur_path)
            future.add_done_callback(lambda f, q=self.task_queue, p=final_path: q.put((f.result(), p)) if f.result() is not None else None)

# 定义消费者线程类
class CustomConsumerThread(ConsumerThreadBase):
    def execute_task(self, item, executor):
        src_path, final_path = item
        executor.submit(convert_and_add_text, src_path, final_path)

# 设置线程池的最大线程数
def process_images(file_path, sheet_name):
    # 文件路径和目录设置
    cur_dir = os.path.dirname(file_path)
    download_dir = os.path.join(cur_dir, download_dir_name)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    final_dir = os.path.join(cur_dir, final_dir_name)
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    # 读取Excel文件
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # 获取URL和名称列
    urls = df['src'].tolist()
    names = df['dest_name'].tolist()

    # 创建任务队列
    task_queue = Queue()

    # 创建生产者线程
    producer_thread = CustomProducerThread(urls, names, max_download_workers, download_dir, final_dir, task_queue)
    producer_thread.start()

    # 创建消费者线程
    consumer_thread = CustomConsumerThread(task_queue, max_conversion_workers)
    consumer_thread.start()

    # 等待生产者线程完成
    producer_thread.join()

    # 等待消费者线程完成
    consumer_thread.join()

    # 确保所有任务完成
    task_queue.join()

    logging.info("所有任务已完成")

# 主程序入口
if __name__ == "__main__":
    # 文件路径和目录设置
    file_path = r"F:\教程\多肉\322种常见多肉植物，1分钟认全.xlsx"
    sheet_name = "多肉"  # 假设工作表的名字为“多肉”

    process_images(file_path, sheet_name)