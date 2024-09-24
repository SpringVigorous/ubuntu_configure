import os
import time
import json

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from selenium.common import TimeoutException 
from selenium.webdriver import Chrome,ChromeOptions,ActionChains,ChromeService

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import *



class SeleniumHelper(Chrome):

    
    def __init__(self,driver_path:str=r"D:\Tool\chromedriver-win64\chromedriver.exe",wait=0,is_headless=False):

        options = ChromeOptions()
        options.add_argument("user-data-dir="+ self.get_user_data_dir())
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-infobars")
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--nn-sandbox")
        if is_headless:
            options.add_argument('--headless')
        # 设置偏好设置
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "download.default_directory": "/path/to/download/directory"
        }

        service = ChromeService(executable_path=driver_path)
        super().__init__(options=options, service=service)
        # super().__init__(options=options)
        self.execute_cdp_cmd("Page.addSeriptToEvaluataNewDo")
        # 隐式等待
        self.implicitly_wait(wait)

    
    @property
    def page_height(self):
        """ 获取页面的高度 """
        height = self.execute_script("return document.body.scrollHeight;")
        # print(f"页面高度: {height}")
        return height
        
    def scroll_page(self, position=0):
        """ 滚动页面到指定位置，默认为底部 """
        if position == 0:
            self.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        else:
            self.execute_script(f"window.scrollBy(0, {position});")
            
    def scroll_to_element(self, element):
        """ 滚动到指定元素 """
        self.execute_script("arguments[0].scrollIntoView();", element)
        
    def wait_presence_of_element(self, by:By, value:Any, timeout:float=5, interval:float=0.5)->WebElement:
        """ 等待单个元素在规定时间内可用 """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                element = self.find_element(by, value)
                return element
            except:
                time.sleep(interval)
        return None
    
    def wait_presence_of_elements(self,by:By, value:Any, timeout:float=5, interval:float=0.5)->list[WebElement]:
        """ 等待多个元素在规定时间内可用 """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                elements = self.find_elements(by, value)
                if elements:
                    return elements
            except:
                pass
            time.sleep(interval)
        return []
    def wait_presence_of_elements_until_last(self,by:By, value:Any, timeout:float=5, interval:float=0.5)->list[WebElement]:
        
        items=self.wait_presence_of_elements(by,value,timeout,interval)
        count=len(items)
        while count >0:
            self.scroll_to_element(items[-1])
            time.sleep(interval*3)
            
            items=self.wait_presence_of_elements(by,value,timeout,interval)
            if len(items)==count:
                break
            count=len(items)
        return items

    def wait_leave_of_element(self, by:By, value:Any, timeout:float=5, interval:float=0.5)->WebElement:
        """ 等待单个元素在规定时间内不可用 """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                self.find_element(by, value)
            except:
                return True
            time.sleep(interval)
        return False
    
    def wait_leave_of_elements(self,by:By, value:Any, timeout:float=5, interval:float=0.5)->list[WebElement]:
        """ 等待多个元素在规定时间内不可用 """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                elements = self.find_elements(by, value)
                if not elements:
                    return True
            except:
                return True
            time.sleep(interval)
        return False
    
    #可以代替 self.get()
    def wait_url_contains(self,url, substring, timeout:float=5, interval:float=0.5):
        """ 检查是否重定向到了登录页面 """
        self.get(url)
        
        
        """ 检查当前 URL 是否包含某个字符 """
        try:
            # 等待页面加载完成
            WebDriverWait(self, timeout).until(
                url_contains(substring)
            )
            print("当前 URL 包含 'login'，登录窗口已弹出")
            return True
        except TimeoutException:
            print("当前 URL 不包含 'login'，登录窗口未弹出")
            return False   
        except:     
            return False
    
    
    
    def execute_cdp_cmd(self, cmd, params=None):
        """ 执行 Chrome DevTools Protocol (CDP) 命令 """
        resource = f"/session/{self.session_id}/chromium/send_command_and_get_result"
        url = self.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = self.command_executor._request('POST', url, body)
        return response.get('value')
    
    def add_script_to_evaluate_on_new_document(self, source):
        """ 添加脚本以在新文档加载时执行 """
        return self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {'source': source})
    
    def wait_title_contains(self, substring, timeout=5, interval=0.5):
        """ 等待页面标题包含特定字符串 """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            title = self.title
            if substring in title:
                return True
            time.sleep(interval)
        return False
    
    def get_user_data_dir(self):
        """ 获取当前工作目录 """
        home_dir =  os.path.expanduser("~")
        dest_dir=os.path.join(home_dir, ".chrome")
        
        return dest_dir

# 示例使用
if __name__ == "__main__":
    # 初始化 SeleniumHelper 实例并使用 with 语法
    with SeleniumHelper() as helper:
        # 打开网页
        helper.get('https://www.example.com')

        # 滚动到页面底部
        helper.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 等待单个元素出现
        element = helper.wait_presence_of_element(By.ID, 'some_id', timeout=5, interval=0.5)
        if element:
            print("元素已找到:", element.text)
        else:
            print("元素未在规定时间内找到")

        # 等待多个元素出现
        elements = helper.wait_presence_of_elements(By.CLASS_NAME, 'some_class', timeout=5, interval=0.5)
        if elements:
            for elem in elements:
                print("元素已找到:", elem.text)
        else:
            print("元素未在规定时间内找到")

        # 等待单个元素不在页面上
        if helper.wait_presence_of_element_not_present(By.ID, 'another_id', timeout=5, interval=0.5):
            print("元素不在页面上")
        else:
            print("元素仍在页面上")

        # 等待多个元素不在页面上
        if helper.wait_leave_of_element(By.CLASS_NAME, 'another_class', timeout=5, interval=0.5):
            print("元素不在页面上")
        else:
            print("元素仍在页面上")

        # 检查当前 URL 是否包含某个字符
        if helper.current_url_contains('example'):
            print("URL 包含 'example'")
        else:
            print("URL 不包含 'example'")

        # 添加脚本以在新文档加载时执行
        script_source = "console.log('Hello from injected script!');"
        result = helper.add_script_to_evaluate_on_new_document(script_source)
        print("脚本添加结果:", result)

        # 等待页面标题包含特定字符串
        if helper.wait_title_contains('Example', timeout=5, interval=0.5):
            print("页面标题包含 'Example'")
        else:
            print("页面标题不包含 'Example'")

        # 获取当前工作目录
        user_data_dir = helper.get_user_data_dir()
        print("当前工作目录:", user_data_dir)