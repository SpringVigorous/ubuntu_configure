import time
from DrissionPage import WebPage
from typing import Callable

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing import TypeVar, Union, Literal
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement



D = TypeVar("D", bound=Union[WebDriver, WebElement])
T = TypeVar("T")


class WebPageHelper(WebPage):
    """ WebPage的辅助类 """
    def __init__(self,time_out:float=2,interval:float=0.2):
        
        
        
        super().__init__(browser='chrome')
        self.set_timeout(time_out,interval)
        
    def set_timeout(self,timeout,interval):
        
        driver=self.driver
        
        # if not hasattr(driver,"current_url"):
        #     setattr(driver,"current_url", driver.url) 
        
        self.__waiter=WebDriverWait(driver,timeout,poll_frequency=interval)
        
    def wait_until(self,method: Callable[[D], Union[Literal[False], T]]):
        
        self.locator
        return self.__waiter.until(method)
    
    
    def until_not(self, method: Callable[[D], T]) -> Union[T, Literal[True]]:
        return self.__waiter.until_not(method)
    
    @property
    def page_height(self):
        """ 获取页面的高度 """
        height = self.run_js("return document.body.scrollHeight;")
        # print(f"页面高度: {height}")
        return height
        
    def scroll_page(self, position=0):
        """ 滚动页面到指定位置，默认为底部 """
        if position == 0:
            self.run_js("window.scrollBy(0, document.body.scrollHeight);")
        else:
            self.run_js(f"window.scrollBy(0, {position});")
            
    def scroll_to_element(self, element):
        """ 滚动到指定元素 """
        self.run_js("arguments[0].scrollIntoView();", element)
        
    def wait_presence_of_element(self, by:By, value):
        element = self.wait_until(EC.presence_of_element_located((By.ID, value)))
        return element


    def wait_presence_of_elements(self, by:By, value):
        
        element = self.wait_until(EC.presence_of_all_elements_located((By.ID, value)))

        return element
    def wait_presence_of_elements_until_last(self,  by:By, value):
        locator=(By.ID, value)
        items=self.wait_presence_of_elements(locator)
        if not items:
            return
        interval=self.__waiter._poll
       
        count=len(items)
        while count >0:
            self.scroll_to_element(items[-1])
            time.sleep(interval*3)

            items=self.wait_presence_of_elements(locator)
            if len(items)==count:
                break
            count=len(items)
        return items


    #获取某个元素或者整个网页的 html代码
    def html_code(self,node=None):
        
        html=""
        if node:
            html=self.run_js("return arguments[0].outerHTML;", node) 
        else:
             html= self.run_js("return document.documentElement.outerHTML;")
              
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html, 'lxml')

        # 格式化 HTML
        return soup.prettify(formatter="html5")

    def wait_until_title_contains(self, substring):
        return self.wait_until(EC.title_contains(substring))
    
    def wait_until_title_is(self, title):
        return self.wait_until(EC.title_is(title))
    
    def wait_until_url_contains(self, substring):
        return self.wait_until(EC.url_contains(substring))
    
    def wait_until_url_matches(self, pattern):
        return self.wait_until(EC.url_matches(pattern))
    
    def wait_until_url_to_be(self, url):
        return self.wait_until(EC.url_to_be(url))
    
    def wait_until_url_changes(self, url):
        return self.wait_until(EC.url_changes(url))
    
    
    
