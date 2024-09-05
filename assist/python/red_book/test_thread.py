import os
import threading
import requests
import queue

# 定义采集函数
def fetch_data(urls, queue, event):
    """从给定URL列表获取数据，并放入队列"""
    while not event.is_set():
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  # 检查请求是否成功
                queue.put(response.text)
            except requests.RequestException as e:
                print(f"请求错误: {e}")
                queue.put(None)
        event.clear()  # 清除事件标志，等待下一次信号

# 定义下载函数
def download_data(queue, file_path, event):
    """从队列中获取数据并保存到指定路径"""
    while not event.is_set():
        try:
            data = queue.get(timeout=1)  # 阻塞等待数据
            if data is not None:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(data)
                    print(f"数据已保存到 {file_path}")
                except IOError as e:
                    print(f"写入文件错误: {e}")
        finally:
            queue.task_done()  # 标记任务完成

# 定义转换函数
def transform_data(queue, file_path, event):
    """从队列中获取文件路径，并读取文件内容进行转换"""
    while not event.is_set():
        try:
            file_path = queue.get(timeout=1)  # 阻塞等待文件路径
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
            queue.task_done()  # 标记任务完成

# 主流程
if __name__ == "__main__":
    import queue

    urls = ["http://example.com/data1.json", "http://example.com/data2.json", "http://example.com/data3.json"]
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # 创建队列
    data_queue = queue.Queue()
    file_queue = queue.Queue()

    # 创建事件
    fetch_event = threading.Event()
    download_event = threading.Event()
    transform_event = threading.Event()

    # 创建线程
    fetch_thread = threading.Thread(target=fetch_data, args=(urls, data_queue, fetch_event))
    fetch_thread.start()

    download_thread = threading.Thread(target=download_data, args=(data_queue, os.path.join(output_dir, "data.txt"), download_event))
    download_thread.start()

    transform_thread = threading.Thread(target=transform_data, args=(file_queue, os.path.join(output_dir, "data.txt"), transform_event))
    transform_thread.start()

    # 控制采集信号
    fetch_event.set()  # 设置采集信号

    # 等待所有采集任务完成
    data_queue.join()

    # 设置下载和转换事件
    download_event.set()
    transform_event.set()

    # 等待下载和转换线程完成
    file_queue.join()

    download_thread.join()
    transform_thread.join()

    # 清除事件标志
    fetch_event.clear()
    download_event.clear()
    transform_event.clear()

    print("所有任务已完成")