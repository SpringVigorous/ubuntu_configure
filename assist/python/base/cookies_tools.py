from DrissionPage import WebPage
import json
import os

__cookies_dir=r"F:\worm_practice\cookies"
os.makedirs(__cookies_dir, exist_ok=True)

def url_to_filename(url):
    return url.replace('/', '_').replace(':', '_').replace('.', '_') + '.json'

def __cache_path(url):
    return os.path.join(__cookies_dir, url_to_filename(url))
    

def get_cookies(page:WebPage):

    cookies = page.driver.execute_script("""
        var cookies = document.cookie.split('; ').reduce(function (cookies, cookie) {
            var parts = cookie.split('=');
            cookies[parts.shift()] = parts.join('=');
            return cookies;
        }, {});
        return cookies;
    """)
    return cookies

def exist_cookies(url):
    return os.path.exists(__cache_path(url))

def add_cookies(page:WebPage,cookies:dict):
    # 将 cookies 设置到当前页面
    for key, value in cookies.items():
        page.driver.execute_script(f'document.cookie="{key}={value}";')

def save_cookies(page:WebPage, url:str):
    # cookies = page.driver.get_cookies()
    cookies= get_cookies(page)
    with open(__cache_path(url), 'w') as file:
        json.dump(cookies, file)

def load_cookies(page:WebPage, url:str):
    with open(__cache_path(url), 'r') as file:
        cookies = json.load(file)
        
    add_cookies(page, cookies)
    # for cookie in cookies:
    #     page.driver.add_cookie(cookie)

def load_save_cookies(page:WebPage, url:str):
    if exist_cookies(url):
        load_cookies(page, url)
    else:
        save_cookies(page, url)
