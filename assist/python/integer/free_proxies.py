"""
https://www.zdaye.com/free/2/



/html/body/div[3]/div/table

1-'ip': '  /html/body/div[3]/div/table/tbody/tr[1]/td[1]     <td>47.92.143.92</td>',
2-端口：/html/body/div[3]/div/table/tbody/tr[1]/td[2]     <td>80</td>
3-类型：/html/body/div[3]/div/table/tbody/tr[1]/td[3]     <td>透明</td>
4-地址：

5-上次验证时间： /html/body/div[3]/div/table/tbody/tr[3]/td[5] <td>57秒前</td> 
6-  是否支持https： /html/body/div[3]/div/table/tbody/tr[1]/td[6] <td>否</td>'https': ' 否 /html/body/div[3]/div/table/tbody/tr[1]/td[6]',
                是 /html/body/div[3]/div/table/tbody/tr[5]/td[6]/div    <div class="iyes"></div>
7- post
8-响应时间：/html/body/div[3]/div/table/tbody/tr[1]/td[8]/div/span    <span style="color:#42464b">&nbsp;2056</span>
9-存活时间
<a class="layui-btn layui-btn-xs" title="最后页" href="/free/10/">10</a>


总条数：  /html/body/div[3]/div/div[7]/font/b  <b>186</b>
每页个数：/html/body/div[3]/div/div[7]/text()[2]   个，每页20个 &nbsp;1
最后页： /html/body/div[3]/div/div[7]/a[9]    <a class="layui-btn layui-btn-xs" title="最后页" href="/free/10/">10</a>


ip,port,type,pos,last_verify_time,https,post,response_time,live_time = row.xpath('./td/text()')


"""

import requests

from lxml import etree
import json

def get_url(index:int = 1):
    base_url="https://www.zdaye.com/free/"
    return f"{base_url}{index}/"



def handle_page(proxies:list,idnex :int = 1):
    headers={   
        'Host': 'www.zdaye.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': '___rl__test__cookies=1724927749135; __51vcke__20L1wEeeGTFXijbh=872e2620-446c-50d1-b7d4-9fd0f1c52dcb; __51vuft__20L1wEeeGTFXijbh=1723908970857; __root_domain_v=.zdaye.com; _qddaz=QD.355423908971031; lastSE=baidu; ASPSESSIONIDAEDSBASA=LBHBJNBAKMFEFEJIKIDEAKHO; __51uvsct__20L1wEeeGTFXijbh=2; Hm_lvt_dd5f60791e15b399bf200ae217689c2f=1723908971,1724926778; HMACCOUNT=03AD22591AF7EB0C; _qdda=3-1.1; _qddab=3-fsf0dj.m0f4v7zr; OUTFOX_SEARCH_USER_ID_NCOO=1954324170.0822732; __vtins__20L1wEeeGTFXijbh=%7B%22sid%22%3A%20%227cdbb30d-de1f-51b7-81a8-004ac17cd515%22%2C%20%22vd%22%3A%208%2C%20%22stt%22%3A%20975059%2C%20%22dr%22%3A%202905%2C%20%22expires%22%3A%201724929552759%2C%20%22ct%22%3A%201724927752759%7D; Hm_lpvt_dd5f60791e15b399bf200ae217689c2f=1724927753',
        }

    
    
    response = requests.get(get_url(),headers=headers)
    if response.status_code != 200:
        return
    response.encoding= 'utf-8'
    html = etree.HTML(response.text)
    
    rows = html.xpath('//table/tbody/tr')
    for row in rows:
        row_data=row.xpath('./td/')
        #['39.102.213.50', '3128', '高匿', '北京市 阿里云', '15秒前', '35天8小时']
        
        # ip,port,type,pos,last_verify_time,https,post,response_time,live_time = row.xpath('./td/text()')[1:5]
        
        index=list(range(1,6))
        index.extend([7,9])
        
        ip,port,type,pos,last_verify_time,post,live_time=list(map(lambda x:row_data[x].text(), index )) 
        https= 0 if  row_data[6].xpath('.//div/@class') is None else 1
        response_time = row_data[8].xpath('.//div/span/text()')[0]
        
        item={
            'ip':ip,
            'port':port,
            'type':type,
            'pos':pos,
            'last_verify_time':last_verify_time,
            'https':https,
            'post':post,
            'response_time':response_time,
            'live_time':live_time,
            }
        
        list.append(item)
    
    
    
    
    if( idnex == 1):
        nums=html.xpath('//a[@title="最后页"]/text()')
        count=int(nums[0]) if nums else 1        
        return count

def read_cache(file_path):
    poxiex=[]
    try:
        with open(file_path,'r',encoding="utf-8") as f:
            poxiex=json.load(f,ensure_ascii=False,indent=4)
    except:
        pass
    return poxiex

def write_cache(file_path, proxies:list):
    with open(file_path,'w',encoding="utf-8") as f:
        json.dump(proxies,f,ensure_ascii=False,indent=4)

def free_proxies():
    cache_path=r"F:\cache\proxies.json"
    
    proxies=read_cache(cache_path)
    if not proxies:
        proxies=[]
        count=handle_page(proxies)
        if not count:
            return []
        for i in range(1,count+1):
            handle_page(proxies,i+1)
        if proxies: 
            write_cache(cache_path,proxies)
    
    return proxies


if __name__ == '__main__':
    print(free_proxies()) 

    
    