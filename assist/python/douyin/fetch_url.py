import requests
#皮皮虾获取视频链接
import json
from dy_unity import dy_root
import os
cookies = {
    '__tins__21011011': '%7B%22sid%22%3A%201743688592897%2C%20%22vd%22%3A%201%2C%20%22expires%22%3A%201743690392897%7D',
    '__51cke__': '',
    '__51laig__': '1',
    'tokens': '7ccef9200186db6e11c8e9ad9832e1ea',
    'user_id': '822368',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # Requests sorts cookies= alphabetically
    # 'Cookie': '__tins__21011011=%7B%22sid%22%3A%201743688592897%2C%20%22vd%22%3A%201%2C%20%22expires%22%3A%201743690392897%7D; __51cke__=; __51laig__=1; tokens=7ccef9200186db6e11c8e9ad9832e1ea; user_id=822368',
    'Origin': 'http://tkqsy.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
    'X-Requested-With': 'XMLHttpRequest',
}

data = {
    'pageUrl': 'https://v.douyin.com/-YfTxhrmKrg/',
}

response = requests.post('http://tkqsy.com/v2/parse/pipi', cookies=cookies, headers=headers, data=data, verify=False)
data=response.json()
with open(os.path.join(dy_root.root_path,"water_url.json"),"w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=4)