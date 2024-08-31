import requests
from lxml import etree
import hashlib
def  md5_str(s:str)->str:
        # 创建 MD5 哈希对象
    hash_object = hashlib.md5(s.encode())
    
    # 获取哈希值
    hash_hex = hash_object.hexdigest()
    
    return hash_hex

Cookie='abRequestId=d8822acc-588e-51e0-a66a-fa4295796ddb; xsecappid=xhs-pc-web; a1=19184f87a2e6lgpru2k76wxnt636hyu9jou7tt4zq50000531117; webId=a82def829567835580b2fcf67b385896; gid=yjyY4if8SqVfyjyY4iYW0l94JdK1kUF7JTWK7uAECI9KqW28Kxv7j98882qyyyW8d42SKS20; webBuild=4.31.6; acw_tc=6578a1de231739652d1b93993f7e0ee35340ed4e1731adc2055dd265a27014b0; web_session=040069b26ead56dc3c1f5cc3f8344b7fc0a87c; unread={%22ub%22:%2266cc0a3a000000001f03bd74%22%2C%22ue%22:%2266aa0ea90000000005032629%22%2C%22uc%22:24}; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=d96f1cc4-4a2b-49b4-8e4b-7e2af703c999'
def search_notes(theme:str):
    url="https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
    headers={
	'Origin': 'https://www.xiaohongshu.com',
	'Referer': 'https://www.xiaohongshu.com/',
	'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
	'Sec-Ch-Ua-Mobile': '?0',
	'Sec-Ch-Ua-Platform': '"Windows"',
	'Sec-Fetch-Dest': 'empty',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Site': 'same-site',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
	'X-B3-Traceid': 'e322ac9e13077379',
	'X-S': 'XYW_eyJzaWduU3ZuIjoiNTQiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6Ijc4ZTI2ZjBmNjNjNGNkY2MxYzFhZDc4NWU2NTljYzUxYzA1ZGUwYzQ2OTczMWFmNzExYjM5M2IwZGMzYjAxYWI0MmZjMGIzYzE3ZTY3MTIxMTVkZGYyYmRiMWJlMmYxYTcwYTE1NmZjZWIyNDFmMjUzYjk2YzY2YWQ0ZGU0MjQ2OTQwNGIyOWI1YjAwNWMwMzBlZTIzZTdkMDBlNjU1NDcyNjc0OTJiYThhZjVlNWFkZDBhNGNiMzJiMjViOGMzNmIxNDlkYmYyMzc0MzkxZGY3ZjczNWU1MjJiZDIwMGRhZGZlM2RkYzdjY2NiNmVkY2VmM2U3NTg0OTYxNTNjNDQyNmY2MWQ3MDliZWE4NjRhMTczZGYyZGU3NzU4OTQ2ZDQxNDFjOTlkYTY1NjEzY2U1NjE0Y2RjYWM0MDcyNGRhNmU4YmI2NDQ1YTQxOTIzZDBiZTEyODJkMWExM2RkMzUyZGVmNjM3MzBmMWJiZmU2YmE3ZTdmNjhiMzQzMDRkNjkxOTQ2MGE1ODBlMmMzNGE0MjllNGNlOGY5NzI2NjAxIn0=',
	'X-S-Common': '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',
	'X-T': '1724746525981',
    "Cookie":Cookie,
    }

    pyload = {
        "keyword": theme,
        "page": 1,
        "page_size": 20,
        # "search_id": md5_str(theme), #"2dolw14gv0t7i8qdwt6je",
        "search_id": "2dolw14gv0t7i8qdwt6je",
        "sort": "general",
        "note_type": 0,
        "ext_flags": [],
        "image_formats": ["jpg", "webp", "avif"]
    }
    
    responds=requests.post(url,headers=headers,json=pyload)
    if responds.status_code!=200:
        return 
    responds.encoding='utf-8'
    html=etree.HTML(responds.text)
    notes=html.xpath('//data/items')
    for note in notes:
        xsec_token=note.xpath('xsec_token/text()')[0]
        note_id=note.xpath('id/text()')[0]
        title=note.xpath('title/text()')[0]
        model_type=note.xpath('model_type/text()')[0]
    
if __name__ == '__main__':
    # print(md5_str("8fbc004f-6fe9-4b01-afc7-b2f19ce94ad6#1724769122454"))
    search_notes("四神汤")