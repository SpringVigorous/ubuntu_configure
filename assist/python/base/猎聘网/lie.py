import requests
from prettytable import PrettyTable
from urllib.parse import unquote
import json
import pandas as pd

cookies = {
    'XSRF-TOKEN': 'b-DyulFzSZ2szRPcAKPexw',
    '__gc_id': '2ff22fd1bc494047a75fd969ad2523b9',
    '_ga': 'GA1.1.1701275434.1731680710',
    '__uuid': '1731680709817.39',
    'Hm_lvt_a2647413544f5a04f00da7eee0d5e200': '1731680710',
    'HMACCOUNT': 'D55DFEF59F0F3227',
    '__tlog': '1731680709829.72%7C00000000%7C00000000%7C00000000%7C00000000',
    'acw_tc': 'ac11000117316807606304735e00e1f51be773b0afe201c19761aa343a32f2',
    'Hm_lpvt_a2647413544f5a04f00da7eee0d5e200': '1731680747',
    '_ga_54YTJKWN86': 'GS1.1.1731680709.1.1.1731681126.0.0.0',
    '__session_seq': '9',
    '__tlg_event_seq': '139',
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'XSRF-TOKEN=b-DyulFzSZ2szRPcAKPexw; __gc_id=2ff22fd1bc494047a75fd969ad2523b9; _ga=GA1.1.1701275434.1731680710; __uuid=1731680709817.39; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1731680710; HMACCOUNT=D55DFEF59F0F3227; __tlog=1731680709829.72%7C00000000%7C00000000%7C00000000%7C00000000; acw_tc=ac11000117316807606304735e00e1f51be773b0afe201c19761aa343a32f2; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1731680747; _ga_54YTJKWN86=GS1.1.1731680709.1.1.1731681126.0.0.0; __session_seq=9; __tlg_event_seq=139',
    'Origin': 'https://www.liepin.com',
    'Referer': 'https://www.liepin.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
    'X-Client-Type': 'web',
    'X-Fscp-Bi-Stat': '{"location": "https://www.liepin.com/zhaopin/?inputFrom=www_index&workYearCode=0&key=BIM&scene=input&ckId=mqqw7vti0mhl5kiwbiuuh4fzdn3hb4u9&dq="}',
    'X-Fscp-Fe-Version': '',
    'X-Fscp-Std-Info': '{"client_id": "40108"}',
    'X-Fscp-Trace-Id': '0a13dedc-93c7-48f3-b63e-d7def794a850',
    'X-Fscp-Version': '1.1',
    'X-Requested-With': 'XMLHttpRequest',
    'X-XSRF-TOKEN': 'b-DyulFzSZ2szRPcAKPexw',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}


def get_job_data(key,years,sallay_killow,city,page):
    json_data = {
        'data': {
            'mainSearchPcConditionForm': {
                'city': city,
                'dq': city,
                'pubTime': '',
                'currentPage': page,
                'pageSize': 40,
                'key': 'BIM',
                'suggestTag': '',
                'workYearCode': "$".join(map(str,years)),
                'compId': '',
                'compName': '',
                'compTag': '',
                'industry': '',
                'salary': '',
                'jobKind': '',
                'compScale': '',
                'compKind': '',
                'compStage': '',
                'eduLevel': '',
                'otherCity': '',
            },
            'passThroughForm': {
                'scene': 'page',
                'ckId': '45yr3eblffp4izoq81nt06x8f0ubikdb',
                'skId': 'uxbuxzsis9m43a3rvukwf0j6ul1v0x3a',
                'fkId': 'sc0helhbpdsegzym81ldh82neg97l4zb',
                'sfrom': 'search_job_pc',
            },
        },
    }

    response = requests.post('https://api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job', cookies=cookies, headers=headers, json=json_data)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应内容为 JSON 格式
        data = response.json().get("data").get("data").get("jobCardList")
        return data
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
def get_job_datas(key,years,sallay_killow,city,page):
    
    datas=[]
    for i in range (1,page+1):
        data=get_job_data(key,years,sallay_killow,city,i)
        if data:
            datas.extend(data)
        else:
            break
    return datas

    
def handle_data(data,file_path):
        
    dest=[]
    
    for datas in data:
        datas["dataInfo"]=json.loads(unquote(datas["dataInfo"]))
        datas["dataParams"]=json.loads(datas["dataParams"])
        
        item={
        "company":datas.get("comp").get("compName"), #公司
        "company_scale":datas.get("comp").get("compScale"), #公司规模
        "company_recruitment_page":datas.get("comp").get("link"), #公司招聘页
        "company_industry":datas.get("comp").get("compIndustry"), #公司领域
        "recruiter":datas.get("recruiter").get("recruiterName"), #招聘人
        "recruiter_position":datas.get("recruiter").get("recruiterTitle"), #招聘人职位
        "label":datas.get("job").get("labels"), #标签
        "region":datas.get("job").get("dq"), #区域
        "update_time":datas.get("job").get("refreshTime"), #更新时间
        "salary":datas.get("job").get("salary"), #薪资
        "position":datas.get("job").get("title"), #职位
        "position_detail_page":datas.get("job").get("link"), #职位详情页
        "experience":datas.get("job").get("requireWorkYears"), #经验
        "education_level":datas.get("job").get("requireEduLevel"), #学历
        "company_status":datas.get("comp").get("compStage"), #公司状态

        }
        dest.append(item)
    
    # print(json.dumps(data, ensure_ascii=False, indent=4))
    
    # pd.json_normalize(data,max_level=10).to_excel("jobs.xlsx")
    header=[ "公司", "公司规模", "公司招聘页", "公司领域", "招聘人", "招聘人职位", "标签", "区域", "更新时间", "薪资", "职位", "职位详情页", "经验", "学历", "公司状态"]
    pd.json_normalize(dest,max_level=10).to_excel(file_path,header=header)
    
    
    
if __name__ == '__main__':
    data=get_job_datas("BIM",(5,10),0,"020",10)
    handle_data(data,"dest_jobs.xlsx")
