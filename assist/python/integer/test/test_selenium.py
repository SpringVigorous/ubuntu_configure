from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# 发送翻页键进行页面滑动
from selenium.webdriver.common.action_chains import ActionChains


import time


browser = webdriver.Chrome()
browser.implicitly_wait(5) #等待时间

 # 模拟滚动
def scroll_down(browser , times=5, interval=1):
    # 执行 JavaScript 代码模拟滚动
    js_scroll_down = """
        var totalScrollHeight = document.body.scrollHeight;
        var currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var scrollStep = 100;  // 每次滚动的距离

        function scrollByStep(step) {
            window.scrollBy(0, step);
        }

        for (var i = 0; i < times; i++) {
            scrollByStep(scrollStep);
            console.log("Scrolling down...");
            if (currentScrollTop + scrollStep >= totalScrollHeight) {
                break;
            }
            currentScrollTop += scrollStep;
            // 等待一段时间让页面加载
            setTimeout(function() {}, interval * 1000);
        }
    """
    browser.execute_script(js_scroll_down)


try:
    browser.get('https://www.baidu.com')

    input = browser.find_element(By.ID, 'kw')
    input.send_keys('Python')
    input.send_keys(Keys.ENTER)
    """文本： .send_keys
    点击： .click
    选择：
    s=Select(item)
    s.select_by_index(1)
    s.select_by_value('value')
    s.select_by_visible_text('text')
    
    
    """
    
    
    """切换窗口
    browser.switch_to.window('window_name')  #iframe名
    或者 brower.swith_to.frame(element)
    ……
    
    #回到原页面
    browser.switch_to.default_content()
    """
    
    """跳转页面  网页地址发生变化，或者打开了新的标签页，需要切换回去
    for window in browser.window_handles:
        browser.switch_to.window(window)
        if browser.title == 'XXX': 
            break
    
    
    """
    
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'content_left')))
    
    #滚轮向下滑动
    # scroll_down(browser,times=1,interval=.2)
    # browser.scroll(0, 1000)

    ActionChains(browser).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
    time.sleep(0.2)
    #调用页面js页面滚动，部分重新写的滚动条可能无法生效
    js="var q=document.documentElement.scrollTop=1000"
    browser.execute_script(js)
    # browser.execute_script("window.scrollTo(0,"+ str(i * 40) + ");")
    # 跳转到指定元素的位置
    # browser.find_element_by_xpath(xpath路径).location_once_scrolled_into_view
    
    browser.find_element(By.XPATH, '//*[@id="1"]/h3/a').click()
    
    print(browser.current_url)
    print(browser.get_cookies())
    print(browser.page_source)
    val=input("请输入文本")
finally:
    browser.close()
    
    
    
