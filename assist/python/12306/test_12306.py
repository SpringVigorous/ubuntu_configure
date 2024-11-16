import requests
from lxml import etree

start_pos = "杭州"
end_pos = "上海"
date = "2024-11-16"

def train_url(start_pos, end_pos, date):
    url= f'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={start_pos}&ts={end_pos}&date={date}&flag=N,N,Y'
    print(url)
    url="https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2024-11-23&leftTicketDTO.from_station=SHH&leftTicketDTO.to_station=HZH&purpose_codes=ADULT"
    return url

# 发送请求
response = requests.get(train_url(start_pos, end_pos, date))

# 检查请求是否成功
if response.status_code == 200:
    # 解析 HTML 内容
    print(response.text)
    exit(0)
    html = etree.HTML(response.text)
    print(etree.tostring(html, encoding='unicode'))
    
    # 查找指定的 table 元素
    tables = html.xpath('//*[@id="t-list"]/table')
    
    # 打印 table 内容
    if tables:
        table=tables[0]
        # print(etree.tostring(table, encoding='unicode'))
    else:
        print("未找到指定的 table 元素")
else:
    print(f"请求失败，状态码: {response.status_code}")