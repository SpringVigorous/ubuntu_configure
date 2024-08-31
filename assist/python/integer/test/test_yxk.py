import requests


url="https://video.gzfeice.com/b7554d95vodtranscq1254019786/ad0c5a001397757891907864196/1444917_2_334.ts"
params={
'encdomain':'cmv1',
'sign':'b56f3e550e021060a7d0a3d241b6618e',
't':'66d38fd6',
}
headers={
    
'Connection':'keep-alive',
'Host':'video.gzfeice.com',
'Origin':'https://haokeyouxuanedu.edu.gzfeice.com',
'Referer':'https://haokeyouxuanedu.edu.gzfeice.com/',
'sec-ch-ua':'";Not A Brand";v="99", "Chromium";v="94"',
'sec-ch-ua-mobile':'?1',
'sec-ch-ua-platform':'"Android"',
'Sec-Fetch-Dest':'empty',
'Sec-Fetch-Mode':'cors',
'Sec-Fetch-Site':'same-site',
'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
}

def get_video():
    responses=requests.get(url,params=params,headers=headers)
    if responses.status_code!=200:
        return
    
    with open("1.mp4","wb") as f:
        f.write(responses.content)
        
    print("done")    

# print(responses.content)

if __name__ == '__main__':
    get_video()