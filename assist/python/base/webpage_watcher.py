from abc import ABCMeta, abstractmethod
from DrissionPage import WebPage
import threading
import time
from typing import Callable
from base.com_log import logger_helper, UpdateTimeType
from base.except_tools import except_stack
from base.com_decorator import exception_decorator

class WebWatcher(metaclass=ABCMeta):
    """抽象浏览器观察者基类（增强版）"""
    def __init__(self, page: WebPage, poll_interval: float = 0.3):
        self.page = page
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._callbacks = []
        self._lock = threading.Lock()
        self.logger = logger_helper(self.__class__.__name__, "监控器")
        self._init_watcher()

    def _init_watcher(self):
        """初始化监视器状态（可被子类覆盖）"""
        pass

    @property
    @abstractmethod
    def watch_name(self):
        return self.__class__.__name__

    #返回值：true  表示继续运行，false 表示停止运行
    @abstractmethod
    def _watch_loop_imp(self)->bool:
        """监控循环抽象方法（必须实现）"""
        raise NotImplementedError("子类必须实现监控逻辑")


    def _watch_loop(self):
        """监控循环抽象方法（必须实现）"""
        while not self._stop_event.is_set():
            if self._watch_loop_imp():
                continue
            self.stop()


    def add_callback(self, callback: Callable):
        """添加事件回调（线程安全）"""
        with self._lock:
            self._callbacks.append(callback)

    def start(self):
        """启动监控线程"""
        if not self._stop_event.is_set():
            self._stop_event.clear()
        threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name=f"{self.__class__.__name__}_Thread"
        ).start()

    def stop(self):
        """停止监控"""
        self._stop_event.set()

    def _notify_callbacks(self, *args, **kwargs):
        """统一回调通知（带异常隔离）"""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.error("回调执行失败", except_stack())
class UrlChangeMonitor(WebWatcher):
    """URL变化监视器"""
    def _init_watcher(self):
        self._last_url = self.page.url
    @property
    def watch_name(self):
        return self.__class__.__name__
    def _watch_loop_imp(self):
        try:
            if self.page._is_loading:
                time.sleep(self.poll_interval)
                return True

            current_url = self.page.url
            if current_url != self._last_url:
                old_url = self._last_url
                self._last_url = current_url
                self._notify_callbacks(old_url, current_url)
            
            time.sleep(self.poll_interval)
        except Exception as e:
            self.logger.debug("URL监控异常", except_stack())
        finally:
            return True

class BrowserClosedMonitor(WebWatcher):
    
    @property
    def watch_name(self):
        return self.__class__.__name__
    """浏览器关闭状态监视器"""
    def _watch_loop_imp(self):

        try:
            # 通过主动获取属性触发异常检测
            _ = self.page.title
            time.sleep(self.poll_interval)
        except Exception as e:

            self._notify_callbacks()
            return False

        return True


# 示例用法
if __name__ == "__main__":
    # 初始化浏览器
    page = WebPage()
    page.get("https://www.example.com")

    # 创建监视器
    url_watcher = UrlChangeMonitor(page)
    close_watcher = BrowserClosedMonitor(page)

    # 定义回调函数
    def on_url_changed(old_url, new_url):
        print(f"URL变化: {old_url} -> {new_url}")

    def on_browser_closed():
        print("浏览器已关闭，执行清理操作...")

    # 注册回调
    url_watcher.add_callback(on_url_changed)
    close_watcher.add_callback(on_browser_closed)

    # 启动监视
    url_watcher.start()
    close_watcher.start()

    # 模拟操作
    time.sleep(5)
    page.quit()