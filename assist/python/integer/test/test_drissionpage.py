
from DrissionPage import WebPage,ChromeOptions,SessionOptions
import platform

import getpass

import time
system= platform.system()
if system.startswith('Windows'):
    EXEC_DIR_PATH = f'c: /Users/{getpass.getuser()}/AppData/Local/Google/chrome/Application/chrome.exe'
    USER_DIR_PATH = f'c:/Users/{getpass.getuser()}/AppData/Local/Google/chrome/User Data'
elif system.startswith('Apple'):
    EXEC_DIR_PATH = f'/Users/{getpass.getuser()}/Library/Application Support/Google/chrome/Application/
    chrome'
    USER_DIR_PATH = f'/Users/{getpass.getuser()}/Library/Application support/Google/chrome/user_ Data'
elif system.startswith('Linux'):
    EXEC_DIR_PATH = f'/home/{getpass.getuser()}/AppData/Local/Google/chrome/Application/chrome'
    USER_DIR_PATH = f'/home/{getpass.getuser()}/AppData/Local/Google/chrome/User Data'
    
    
    
def get_browser_1()-> WebPage:
    co = ChromeOptions()
    co.set_headless(False)
    co.set_argument('--start-maximized')
    co.remove_argument('--enable-automation')
    
    
    
    
    
    
    
    
    #浏览器配置对象
    options=ChromeOptions()
        #禁用白动化栏
    options.add_experimental_option('excludeswitches',['enable-automation'])
    #屏蔽保存密码提示框
    options.add_experimental_option('prefs',{
    'credentials enable service': False,
    'profile.password manager enabled': False
    })
    #窗口最大化
    # options.add_argument("--start-maximized")
    #无界面运行(无窗口)，也叫无头浏览器
    # options.add_argument("--headless")
    #禁用GPU，防止无头模式出现莫名的bug
    # options.add_argument("--disable-gpu")
    #禁用启用Blink运行时
    options.add_argument('--disable-blink-features=Automationcontrolled')
    #使用本地浏览器用户数据

    options.add_argument("--qser-data-dir=" + USER_DIR_PATH)
    # options.binary location=EXEC DIR PATH
    # service

    driver_path =f'F:\Projects
    Dev\python\demo2\chromedriver.exe'

    service =service(executable_path=driver_path)
    driver = WebPage.Chrome(options=options,
    service=service)
    
    
    
    
    co.set_paths(browser_path=EXEC_DIR_PATH, user_data_path=USER_DIR_PATH)
    return WebPage(driver_or_options=co)
    
    
    
def get_browser_2()-> WebPage:

    import subprocess
    import time

    """--remote-debugging-port=9999 是指定运行端口，只要没被占用就行
    --user-data-dir 指定运行浏览器的运行数据，新建一个干净目录，不影响系统原来的 数据
    --incognito 隐私模式打开
    --start-maximized 窗日最大化
    --new-window 直接打开网址"""

    # 启动命令
    command =f'{EXEC_DIR_PATH}--remote-debugging-port=9999    --remote-allow-origins=*    --start-maximized'
    subprocess.Popen(command,shell=True)
    time.sleep(1)
    co =ChromeOptions()
    co.set_headless(False)
    co.set_argument('--start-maximized')
    co.remove_argument('--enable-automation')
    co.set_paths(browser_path=EXEC_DIR_PATH, user_data_path=USER_DIR_PATH, local_port=9999)
    return WebPage(driver_or_options=co)

def close_browser(browser: WebPage):
    print('退出程序')
    browser.quit()
    
if __name__ == '__main__':
    browser = get_browser_2()
    browser.get('https://www.baidu.com')
    time.sleep(2)
    close_browser(browser)