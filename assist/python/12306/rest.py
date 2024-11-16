from threading import Thread
import requests
import pandas as pd
import json
import os
import re

#导入城市
f2 = open(os.path.join(os.path.dirname(__file__), 'city.json'),"r",encoding="utf-8")
city2code = json.load(f2)
f2.close()
code2city = {v: k for k, v in city2code.items()}

#查询函数
def chaxun(city):

    #判断出发地
    while True:
        in_start = input("请输入出发地：\n")
        if in_start not in city.keys():
            print("输入的城市有误，请重新输入：")
            continue
        else:
            break
    #判断目的地
    while True:
        in_end = input("请输入目的地：\n")
        if in_end not in city.keys():
            print("输入的城市有误，请重新输入：")
            continue
        else:
            break
    # 判断输入时间格式
    while True:
        time = input("请输入时间（格式：xxxx.xx.xx)：\n")
        if (len(time.split(".")) != 3 or len(time.split(".")[0]) != 4
                or len(time.split(".")[1]) != 2 or len(time.split(".")[2]) != 2):
            print("输入的时间有误，请重新输入：")
            continue
        else:
            break
    
    # time = '2024.11.25'
    # in_start = '上海'
    # in_end = '南京'
        
    time = time.replace('.', '-')
    in_start = city[in_start]
    in_end = city[in_end]
    chaxun_list = [in_start, in_end, time]
    return chaxun_list

#动车类型函数
def the_kind():
    # return '全部'
    #输入动车类型
    kind_list = ['高铁', '火车', '全部']
    while True:
        kind = input("请输入要查询的类型（高铁/火车/全部）：\n")
        if kind in kind_list:
            break
        else:
            continue
    return kind

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Cookie": ("_uab_collina=172794751299674187369334; JSESSIONID=A531711E4376E392850CED44B2076EE6; _jc_save_fromDate=2024-10-15; _jc_save_fromStation=%u957F%u6C99%2CCSQ; _jc_save_toDate=2024-10-15; _jc_save_toStation=%u6B66%u6C49%2CWHN; _jc_save_wfdc_flag=dc; guidesStatus=off; route=6f50b51faa11b987e576cdb301e545c4; cursorStatus=off; highContrastMode=defaltMode; BIGipServerotn=1978138890.64545.0000; BIGipServerpassport=954728714.50215.0000")
}

def train_time():
    url="https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=55000G703272&from_station_telecode=SHH&to_station_telecode=NJH&depart_date=2024-11-25"
    data={
        'train_no':'55000G703272',
        'from_station_telecode':'SHH',
        'to_station_telecode':'NJH',
        'depart_date':'2024-11-25',
    }
    
    front_content = requests.get(url, params=data, headers=header)
    front_content.encoding = "utf-8"
    front_content.close()    #关闭requests
    result = front_content.json()['data']['data']    #返回json字典数据
    print(result)

#爬取并输出函数
def func(time, start, end, kind):

    front_url = "https://kyfw.12306.cn/otn/leftTicket/query"
    data = {
       "leftTicketDTO.train_date": time,
       "leftTicketDTO.from_station": start,
       "leftTicketDTO.to_station": end,
       "purpose_codes": "ADULT"
    }


    front_content = requests.get(front_url, params=data, headers=header)
    front_content.encoding = "utf-8"
    front_content.close()    #关闭requests
    result = front_content.json()['data']['result']    #返回json字典数据
    # print(result)
    lst_G = [] #高铁信息
    lst_KTZ = [] #火车信息
    lst_all = [] #全部信息

    org_list=[]
    for it in result:
        info_list = it.split("|")  #切割数据，中文转英文
        citys=info_list[4:8]
        info_list[4:8] = [code2city[i] for i in citys]
        
        org_list.append(info_list)
        
        beg_city=info_list[4]   #始发站
        end_city=info_list[5]   #终点站
        
        start_city=info_list[6] #出发站
        dest_city=info_list[7] #到达站
        
        num = info_list[3]
        start = info_list[8]        #启动时间
        arrive = info_list[9]       #到达时间
        time = info_list[10]        #经历时长
        business_seat = info_list[32]   #商务座
        first_seat = info_list[31]      #一等座
        second_seat = info_list[30]     #二等座
        soft_sleeper = info_list[23]       #软卧
        hard_sleeper = info_list[28]       #火车硬卧
        soft_seat = info_list[27]         #火车软座
        hard_seat = info_list[29]        #火车硬座
        none_seat = info_list[26]         #无座
        high_soft=info_list[21]     #高级软卧
        special_seat=info_list[25] #特等座
        
        has_seat=1 if info_list[11]=="Y" else 0 #是否有票
        
        dic = {
               "车次": num,
               "出发站":start_city,
               "到达站":dest_city,
               "始发站":beg_city,
               "终点站":end_city,
               "启动时间": start,   # 启动时间
               "到达时间": arrive,      #到达时间
               "中途时长": time,        #经历时长
               "商务座": business_seat,  #商务座
               "一等座": first_seat,      #一等座
               "二等座": second_seat,    #二等座
               "软卧": soft_sleeper,       #火车软卧
               "硬卧": hard_sleeper,       #火车硬卧
               "软座": soft_seat,         #火车软座
               "硬座": hard_seat,        #火车硬座
               "无座": none_seat  ,       #无座
               "高级软卧": high_soft,     #高级软卧
               "特等座": special_seat,   #特等座
               "是否有票": has_seat,      #是否有票
        }

    #进行三种分类
        lst_all.append(dic)
        if 'G' in num:
            lst_G.append(dic)
        else:
            lst_KTZ.append(dic)

    #dataframe格式设置
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 100)

    #三种类型票 高铁 火车 全部
    content_G = pd.DataFrame(lst_G).sort_values(by=["是否有票","启动时间"],ascending=[False,True])
    content_KTZ = pd.DataFrame(lst_KTZ).sort_values(by=["是否有票","启动时间"],ascending=[False,True])
    content_all = pd.DataFrame(lst_all).sort_values(by=["是否有票","启动时间"],ascending=[False,True])

    if kind == '高铁':
        with pd.ExcelWriter("火车票查询.xlsx",mode="w") as w:
            content_G.to_excel(w, sheet_name="高铁票", index=False)
    elif kind == '火车':
        with pd.ExcelWriter("火车票查询.xlsx", mode="w") as w:
            content_KTZ.to_excel(w, sheet_name="火车票", index=False)
    else:
        with pd.ExcelWriter("火车票查询.xlsx", mode="w") as w:
            content_all.to_excel(w, sheet_name="全部票", index=False)
            
            
    # 将原始结果输出到Excel文件
    # df = pd.DataFrame(org_list)
    # header=['简拼','站名','编码','全拼','缩称','站编号','城市编码','城市','国家拼音','国家','英文']
    # df.to_excel("org.xlsx", index=False, header=False)
    

if __name__ ==  '__main__':
    in_start,in_end,time = chaxun(city2code)
    kind = the_kind()
    func(time, in_start, in_end, kind)
    

