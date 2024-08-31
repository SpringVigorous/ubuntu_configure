from DrissionPage import WebPage
from DrissionPage.common import Actions
from pprint import pprint
import os
import time
import json
from requests.structures import CaseInsensitiveDict
import requests
import sys


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd


url='https://m.client.10010.com/serviceimportantbusiness/queryNetWork/queryNetWorkDetailContent'

headers={
'cookie':'JSESSIONID=80E7E99EA1F03EFE3568649C76C2A7CD; ecs_cook=150c0e8040e0f92e39fdcd976692a8eb; mallcity=31|310; selectedProvince=031; arialoadData=false; piw=%7B%22login_name%22%3A%22185****0795%22%2C%22nickName%22%3A%22%E5%AD%9F%E7%9C%9F%E7%9C%9F%22%2C%22rme%22%3A%7B%22ac%22%3A%22%22%2C%22at%22%3A%22%22%2C%22pt%22%3A%2201%22%2C%22u%22%3A%2218516760795%22%7D%2C%22verifyState%22%3A%22%22%7D; JUT=O/Xy+RFHjAOHmG5fJ1Lx8zN7fbu7gbHPjeUykfZpTDE4ueD8X28PjBPlxKCrLKYlkt9/TuPEhfshHScN623QnpuIXj1M0iVX/Ur0UWP8Lc/U8kE3hKnVOJkRPJssUPrr0eg9GuHNlr2t6vAp6v8JDxhaVK1j1xLdXybYtv3WehxL1pQSPzc39vWvLfLdJcB38LnfvZkU8Bw2XE6zAZ5a7KKscNqQMej21tmLKrYADXIgIB7wl+P6ktp5/HIrvomQPtVub17p8uZ2vWxn1GbNHqYWvooFT/KDOpooAo8b5sJuc/BtDXAi0Xy+6KwMjhnJjqPSc4l8RHHtcvYOWF6eK4cPnICzWJzskX3Y37q0mLnqL3uQy7c6N4FOAlsZV5Zuy0HoaEP4cUeJYL3yYRFMnXl2ALcjdI8JfsZ6JtV9W7S3Emyit+2hluVygx13VYCNfBp8g/TGTVNcu6R3CWXW3Bx3CEO9LpmqPBvrDOPnq0Ua3xBalEsFTSoTXZWSHO8lENW6xZ4XBXtjlHVk+wmsK+LmZ+Tt/4W39J3IVTZ0cs7nLlmGf2lCXrDXzFVt9bNm3bUYkzIUOdUPAOpQfIImk88+caGF5a49senLaHc3ecvk62LIG5BzDENapZTWOOpjJDLIGJvCUUU=YWboIwkYCsSY97wEK4Prtw==; _uop_id=af3a434b997b15a753e50667c01de32c; WT=185****0795; u_account=AWK3fgw2skqgiU7Lc8bZQw%253D%253D; acw_tc=2760823017250290655788129ea8c9d35f1e1d525f187c8ab9b6aba59955dd; loginflag=true; userprocode=031; citycode=310; city=031|',
'origin':'https://img.client.10010.com',
'priority':'u=1, i',
'referer':'https://img.client.10010.com/',
'sec-ch-ua':'"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
'sec-ch-ua-mobile':'?0',
'sec-ch-ua-platform':'"Windows"',
'sec-fetch-dest':'empty',
'sec-fetch-mode':'cors',
'sec-fetch-site':'same-site',
'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}

data={
'menuId':'000200030004',
't':'2024-8-24 22:57:29',
'YYYY':'2024',
'MM':'08',
'DD':'24',
'queryMonthAndDay':'day',
'currNum':'1',
'fistrow':'150',
'sms':'ZgkSPh/PIuR9ipgNEnsBBiqj7IwupCj1/c/guunFVzi2Nz6htRpvdwofABluaznuzKbqlett1gh2vWmyIynkUdI5jy1xSyJzQeU5emKc4+vXbdG+CCEDr362iu9x+ejBdaZwVwkSGKDElfEXmbDnPJyG8ZJZ3FlpIEOTkB9q6qM=',
'duanlianjieabc':'',
'channelCode':'',
'serviceType':'',
'saleChannel':'',
'externalSources':'',
'contactCode':'',
'version': 'WT'
    
}

# response=requests.get(url,headers=headers,params=data)
# response.encoding='utf-8'
# print(response.status_code)

# with open('phone_cusumer.html','w',encoding='utf-8') as f:
#     f.write(response.text)


def read_json_data(data):
    
    key_word="netWorkList"
    if not key_word in data.keys():
        return None
    pf = pd.json_normalize(
    data["netWorkList"],meta_prefix="sec.", max_level=10, errors="ignore")
    return pf


def main():        
    wp=WebPage()
    ac=Actions(wp)
    
    
    wp.get('https://iservice.10010.com/e4/miniservice/query/detailQuery.html')
    
    """    //*[@id="summary"]/div[1]/div/div[3]/input
        <input type="text" autocomplete="off" name="" placeholder="请选择" class="el-input__inner">
        <input type="text" autocomplete="off" name="" placeholder="请选择" class="el-input__inner">
    """
    time.sleep(1)

    search_inputs = wp.eles('xpath://input[@class="el-input__inner"]')

    search_inputs[1].input('2024-08-1\n')
    search_inputs[2].input('2024-08-30\n')
    time.sleep(.4)
    """
    //*[@id="summary"]/div[1]/div/div[5]
        <div data-v-6bd49b8d="" class="selected">确定</div>
    """
    seach_button=wp.ele('xpath://div[@class="selected"]')
    if not seach_button:
        sys.exit(0)
    seach_button.click()
    wp.listen.start(['queryNetWork/queryNetWorkDetailContent',]) 

    # //*[@id="middle"]/div[2]/div[3]/div[1]/div[1]
    """
    <div role="button" tabindex="0" aria-expanded="false" class="van-cell van-cell--clickable van-collapse-item__title">
<div class="van-cell__title">
    <img data-v-5cd232ba="" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAtCAMAAADflBjwAAAAllBMVEUAAADnACfnACjoACfnACfnACfpACnrACn/AD3tACvnACjnACjnACjpACj7ADbnACfnACfnACnpACrrACvmACfoACjoACnqAC3oACjoACjpACnpACnrACrnACfnACfoACjpACrnACfmACfoACfnACfnACfoACjqACvmACfnACfnACjnACfnACfmACjoACfqACrnACfmACc5TtEzAAAAMXRSTlMAgZdB7PxQMgUNrtOZRwnzw148HflrVhV1WkQ4Gdh7Zinoz8qQiU0j5N+9taSGYi6exZXIfQAAAiZJREFUSMfNkumOozAQhA3BweY+Qkg4cgdyJ37/l9vuBs1EgpmxtCPt1g/0Yapsd9PsXetTlHZ0P90CgsDZHtlXyrlSHlGplFoTZUDJV4GNUvxKtATbnegINB9ag+Zyrp0LfNw6qD1QTVQD7Z1rvT/64sMuFpbS0PbBOlWR4joBrm50iHTxRcfft+SGb2cjm9hTgMhGrYBeRC+ghW0njUHXbhizFSap6S2Qw1AYNYgMoClRHsEpO8YOuC3rBJd7dB9DxUuikisrZ6Q0BGvLav75Z+S66CnNnj3ZWcp6mRCIGcR4wLS0xnoYPCymJ6rsvw6UB88zl4SV4XnecUNcmLDcjATSmUJRYkdoSUBbkYphwFekA6DgHdvAjw4Xw0BQ44fQRvbIFAnA/ESHtYMAJCa+X/RT8PR9vxSEEpfl77RVSPkxI1JK0WMAy6OBGwfcVTQ0IeDsgCiuVI4cBiaKdEdT2PEGeNlhNgw83/q37bj67HY8cqVs77quGSAmF8BoTsurnevujuKfDN9mZRhGQSjXgIuU2MblciRQda2ZIkeE2wC3oZnkyS8Mn6Qpm9FWDplcAZhaiOFmpIZ8HsfLllAUcRw3krhawnL6N13icKBmYA6BFTvDM9cLrGioHJo4LeHg+nQO93X8CXYxYMLlis8M8aN/YkG5JgZnkFDhxTO/08tVYAtTKh4SWuJ8zkjlWWlFQvSTRLb/2W55FXuTfE6+VdL2bfkDquySjbdcFykAAAAASUVORK5CYII=" alt="">
        <span data-v-5cd232ba="">8月30日</span>
    </div>
    <i class="van-icon van-icon-arrow van-cell__right-icon"></i>
</div>

    """
    date_buttons=wp.eles('xpath://div[@class="van-cell van-cell--clickable van-collapse-item__title"]')
    pfs=[]
    
    for index,date_button in enumerate(date_buttons) :
        date_button.click()
        time.sleep(.4)

    
        packet = wp.listen.wait()
        request=packet.request

        request_url=request.url
        request_headers=dict(request.headers.items())
        request_datas=request.postData

        # request_cookies=  "; ".join([f'{item["name"]}={item["value"]}'  for item in request.cookies]) 
        response=packet.response
        data=response.body
        with open(f'temp/phone_cusumer_{index}.json','w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False,indent=4)
            # f.write(response.body.decode('utf-8'))
            
        pfs.append(read_json_data(data))
    merge_frames(pfs)

def merge_frames(pfs):
    # 使用 concat 合并所有 DataFrame
    filtered_list =[item for item in pfs if item is not None]
    
    merged_df = pd.concat(filtered_list, ignore_index=True)
    outPath = f"temp/phone_cusumer-tab.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        merged_df["pertotalsm"]=merged_df["pertotalsm"].astype(float)
        merged_df["totalfee"]=merged_df["totalfee"].astype(float)
        
        merged_df.to_excel(writer, sheet_name="calalog")

        
        grouped_df = merged_df.groupby(["begindate","billtype"])[["pertotalsm", "totalfee"]].sum()
        grouped_df["pertotalsm"]=grouped_df["pertotalsm"]/1024
        grouped_df=grouped_df.sort_values(by=["begindate","pertotalsm"], ascending=[True, False]).reset_index()
        grouped_df.to_excel(writer, sheet_name="total")
        
        
        project_df=merged_df.groupby(["billtype"])[["pertotalsm", "totalfee"]].sum().reset_index()
        project_df["pertotalsm"]=project_df["pertotalsm"]/1024
        project_df=project_df.sort_values(by=["pertotalsm"], ascending=[ False]).reset_index()
        project_df.to_excel(writer, sheet_name="project")
    
def merge_from_files():
    dir_path = 'temp'
    pfs=[]
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.json'):
            with open(os.path.join(dir_path, file_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                pf = read_json_data(data)
                pfs.append(pf)
    
    merge_frames(pfs)
    
            
        
if __name__ == '__main__':
    # main()
    merge_from_files()
    pass        