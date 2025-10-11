from DrissionPage import WebPage
import threading
import time
from base.com_log import logger_helper,UpdateTimeType
from base.except_tools import except_stack
from base.com_decorator import exception_decorator


class UrlChangeWatcher:
    def __init__(self, page: WebPage, initial_interval=0.3):
        self.set_poll_interval(initial_interval)
        self.page = page
        self._stop_event = threading.Event()
        self._callbacks = []
        self._last_url = None
        self._lock = threading.Lock()
        self.logger=logger_helper(self.__class__.__name__,"监控url变化")
    def set_poll_interval(self, interval):
        """动态设置轮询间隔"""
        self.poll_interval = max(0.1, interval)  # 最小0.1秒
    def add_callback(self, callback):
        """添加URL变化回调函数"""
        with self._lock:
            self._callbacks.append(callback)

    def start(self):
        """启动监听线程"""
        self._last_url = self.page.url
        threading.Thread(target=self._watch_loop, daemon=True,name=self.__class__.__name__).start()

    def stop(self):
        """停止监听"""
        self._stop_event.set()

    @exception_decorator(error_state=False)
    def _notify_callbacks(self, old_url, new_url):
        """线程安全地通知所有回调"""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(old_url, new_url)
                except Exception as e:
                    self.logger.error("回调执行失败",except_stack())

    @exception_decorator(error_state=False)
    def _watch_loop(self):
        """核心监控循环"""
        while not self._stop_event.is_set():
            try:
                if self.page._is_loading:  # 假设有页面加载状态检查
                    time.sleep(self.poll_interval)
                    continue
                current_url = self.page.url
                if current_url != self._last_url:
                    old_url = self._last_url
                    self._last_url = current_url
                    self._notify_callbacks(old_url, current_url)
                time.sleep(self.poll_interval)  # 根据需求调整轮询间隔
            except Exception as e:
                self.logger.error("监控异常",except_stack())
                



# 使用示例
def url_change_handler(old_url, new_url):
    print(f"URL变化: {old_url} → {new_url}")

if __name__ == '__main__':
    page = WebPage()
    page.get("https://www.example.com")
    
    watcher = UrlChangeWatcher(page)
    watcher.add_callback(url_change_handler)
    watcher.start()  # 启动监听

    # 模拟触发URL变化的操作
    page.ele('a').click()  # 点击一个链接

    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()