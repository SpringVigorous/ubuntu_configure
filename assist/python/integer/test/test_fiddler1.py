import requests
from pprint import pprint
import warnings
warnings.filterwarnings("ignore")


for i in range(1, 100):
    url = f"https://qifu-api.baidubce.com/ip/geo/v1/district?ip={i}.114.153.250"
    breakpoint()
    respond = requests.get(url, verify=False)
    if respond.status_code != 200:
        continue
    data= respond.json()
    print( f"url:{url}  country: {data["data"]["country"]}")
    if i==36:
        pprint(respond.json())    

