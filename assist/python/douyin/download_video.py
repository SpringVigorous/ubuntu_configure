import requests

headers = {
    'authority': 'v3-default.365yg.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Tue, 25 Mar 2025 23:23:11 GMT',
    'if-none-match': '"1BFFA1B0094CFFC79E0666A566D872C9"',
    'range': 'bytes=0-1048575',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
}

params = {
    'a': '2011',
    'ch': '0',
    'cr': '0',
    'dr': '0',
    'er': '0',
    'lr': 'unwatermarked',
    'net': '5',
    'cd': '0|0|0|0',
    'cv': '1',
    'br': '5918',
    'bt': '5918',
    'cs': '0',
    'ds': '4',
    'ft': 'k7Fz7VVywSyRKJ8kmo~pK7pswApcKemZvrKLO~ycdo0g3cI',
    'mime_type': 'video_mp4',
    'qs': '0',
    'rc': 'ZTQ1Omg0OWVnPGk8ZWU0ZUBpM3ZrZXk5cjdleTMzNGkzM0A1MS5gMDA2NWAxMDNfMTNgYSMuXl9sMmQ0cWVgLS1kLWFzcw==',
    'btag': '80000e00010000',
    'dy_q': '1743689501',
    'feature_id': '46a7bb47b4fd1280f3d3825bf2b29388',
    'l': '2025040322114101C8394A49CD5CD99B89',
}

response = requests.get('https://v3-default.365yg.com/9e54a0ac2c825052284887c7fb36ae3c/67eea542/video/tos/cn/tos-cn-ve-15c001-alinc2/o4QaEw84g6f9AIcxnPEHtEFIAVAiNrf2BcQCD1/', params=params, headers=headers)
with open("1.mp4","wb") as f:
    f.write(response.content)