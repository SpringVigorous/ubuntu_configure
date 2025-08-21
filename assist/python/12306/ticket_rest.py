from threading import Thread
import requests
import pandas as pd

import os
import time

import sys

from pathlib import Path
from datetime import datetime

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,arabic_numbers

from station_routine import *
from station_config import StationConfig
station_config=StationConfig(max_transfers=3)

from station_routine import TrainStationManager

station_manager=TrainStationManager()
@exception_decorator(error_state=False)
def str_to_time(time_str:str)->datetime:
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except:
        return 

@exception_decorator(error_state=False)
def rest_ticket_raw(from_station, to_station, date)->list[dict]:
    cookies = {
        '_uab_collina': '175550955572785146880319',
        '___rl__test__cookies': '1755665093121',
        'JSESSIONID': '7D7D874B1DF46F5EAE2CC1BBE6824E21',
        'guidesStatus': 'off',
        'highContrastMode': 'defaltMode',
        'cursorStatus': 'off',
        '_jc_save_wfdc_flag': 'dc',
        'BIGipServerotn': '1591279882.50210.0000',
        'BIGipServerpassport': '887619850.50215.0000',
        'route': 'c5c62a339e7744272a54643b3be5bf64',
        '_jc_save_toDate': date,
        '_jc_save_zwdch_fromStation': station_manager.city_cookie_param(from_station),
        '_jc_save_zwdch_cxlx': '0',
        '_c_WBKFRo': 'sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS',
        '_nb_ioWEgULi': '',
        'OUTFOX_SEARCH_USER_ID_NCOO': '742496979.536112',
        '_jc_save_fromStation': station_manager.city_cookie_param(from_station),
        '_jc_save_toStation': station_manager.city_cookie_param(to_station),
        '_jc_save_fromDate': date,
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': '_uab_collina=175550955572785146880319; ___rl__test__cookies=1755665093121; JSESSIONID=7D7D874B1DF46F5EAE2CC1BBE6824E21; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; _jc_save_wfdc_flag=dc; BIGipServerotn=1591279882.50210.0000; BIGipServerpassport=887619850.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_toDate=2025-08-20; _jc_save_zwdch_fromStation=%u56FA%u59CB%2CGXN; _jc_save_zwdch_cxlx=0; _c_WBKFRo=sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS; _nb_ioWEgULi=; OUTFOX_SEARCH_USER_ID_NCOO=742496979.536112; _jc_save_fromStation=%u897F%u5CE1%2CXIF; _jc_save_toStation=%u4FE1%u9633%2CXUN; _jc_save_fromDate=2025-08-29',
        'If-Modified-Since': '0',
        'Referer': 'https://www.12306.cn/index/index.html',
        'Referer': f'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={station_manager.city_url_param(from_station)}&ts={station_manager.city_url_param(to_station)}&date={date}&flag=N,N,Y',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'leftTicketDTO.train_date': date,
        'leftTicketDTO.from_station': station_manager.code_from_city(from_station),
        'leftTicketDTO.to_station': station_manager.code_from_city(to_station),
        'purpose_codes': 'ADULT',
    }

    response = requests.get('https://kyfw.12306.cn/otn/leftTicket/queryU', params=params, cookies=cookies, headers=headers)
    return response.json()

@exception_decorator(error_state=False)
def train_info(train_no,date)->list[dict]:
        
    cookies = {
        # 'JSESSIONID': '7D7D874B1DF46F5EAE2CC1BBE6824E21',
        # 'guidesStatus': 'off',
        # 'highContrastMode': 'defaltMode',
        # 'cursorStatus': 'off',
        # '_jc_save_wfdc_flag': 'dc',
        # 'BIGipServerotn': '1591279882.50210.0000',
        # 'BIGipServerpassport': '887619850.50215.0000',
        # 'route': 'c5c62a339e7744272a54643b3be5bf64',
        # '_jc_save_toDate': '2025-08-20',
        # '_jc_save_zwdch_fromStation': '%u56FA%u59CB%2CGXN',
        # '_jc_save_zwdch_cxlx': '0',
        # '_c_WBKFRo': 'sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS',
        # '_nb_ioWEgULi': '',
        # '_jc_save_fromDate': '2025-08-29',
        # 'OUTFOX_SEARCH_USER_ID_NCOO': '742496979.536112',
        # '_jc_save_fromStation': '%u897F%u5CE1%2CXIF',
        # '_jc_save_toStation': '%u4FE1%u9633%2CXUN',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'JSESSIONID=7D7D874B1DF46F5EAE2CC1BBE6824E21; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; _jc_save_wfdc_flag=dc; BIGipServerotn=1591279882.50210.0000; BIGipServerpassport=887619850.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_toDate=2025-08-20; _jc_save_zwdch_fromStation=%u56FA%u59CB%2CGXN; _jc_save_zwdch_cxlx=0; _c_WBKFRo=sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS; _nb_ioWEgULi=; _jc_save_fromDate=2025-08-29; OUTFOX_SEARCH_USER_ID_NCOO=742496979.536112; _jc_save_fromStation=%u897F%u5CE1%2CXIF; _jc_save_toStation=%u4FE1%u9633%2CXUN',
        'Referer': 'https://kyfw.12306.cn/otn/queryTrainInfo/init',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'leftTicketDTO.train_no': train_no,
        'leftTicketDTO.train_date': date,
        'rand_code': '',
    }

    response = requests.get('https://kyfw.12306.cn/otn/queryTrainInfo/query', params=params, cookies=cookies, headers=headers)

    return response.json()["data"]["data"]


def _train_type(train_name):
    train_type=train_name[0] 
    if arabic_numbers(train_type):
        train_type="0"
    return train_type


#爬取并输出函数
@exception_decorator(error_state=False)
def rest_tickets(date, from_city, to_city, kind,name_prefix=None):
    logger=logger_helper("获取余票信息",f"{date} {from_city}->{to_city} {kind}")
    raw_data=rest_ticket_raw(from_city,to_city,date)
    if not raw_data:
        logger.error("失败","可能不存在直达车次",update_time_type=UpdateTimeType.ALL)
        return

    
    result = raw_data['data']['result']    #返回json字典数据
    # print(result)
    lst_G = [] #高铁信息
    lst_KTZ = [] #火车信息
    lst_all = [] #全部信息

    org_list=[]
    for it in result:
        info_list = it.split("|")  #切割数据，中文转英文
        train_num=info_list[2]
        citys=info_list[4:8]
        info_list[4:8] = [station_manager.city_from_code(i) for i in citys]
        
        org_list.append(info_list)
        num = info_list[3]
        
        beg_city=info_list[4]   #始发站
        end_city=info_list[5]   #终点站
        
        start_city=info_list[6] #出发站
        dest_city=info_list[7] #到达站
        
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
        train_type=_train_type(num)

        dic = {
               "车次": num,
               "编号":train_num,
               "出发站":start_city,
               "到达站":dest_city,
               "始发站":beg_city,
               "终点站":end_city,
               "启动时间": str_to_time(start),   # 启动时间
               "到达时间": str_to_time(arrive),      #到达时间
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
               "类型":train_type,
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
    pd.set_option('display.width', 200)


    logger.info("成功",f"共{len(lst_all)}个车次",update_time_type=UpdateTimeType.STAGE)

    #三种类型票 高铁 火车 全部
    
    def _write_excel(lst,name):
        
        pre_name=f"{date}_" +(f"{name_prefix}_" if name_prefix is not None else "") 
        cur_name=f"{pre_name}{from_city}-{to_city}.xlsx"
        cur_path=station_config.data_dir/cur_name
        
        dfs=[]
        
        with pd.ExcelWriter(cur_path,mode="w") as w:
            train_df = pd.DataFrame(lst).sort_values(by=["是否有票","启动时间"],ascending=[False,True])
            train_df.to_excel(w, sheet_name=f"{name}票", index=True)
            

            for _,row in train_df.iterrows():
                train_no=row["编号"]
                info = train_info(train_no,date)
                if not info: continue
            
                cur_df=pd.DataFrame(info)
                train_name=cur_df["station_train_code"][0]
                logger.stack_target(f"获取{train_name}车次信息")
                logger.trace(f"成功",update_time_type=UpdateTimeType.STEP)
                
                #只保留部分列
                retain_cols=[
                    "station_no","station_name","arrive_time","start_time","running_time"
                    ]
                try:
                    cur_df=cur_df[retain_cols]
                    cur_df["train_no"]=train_no
                    cur_df["train_name"]=train_name
                    dfs.append(cur_df)
                    
                    # cur_df["start_time"]=cur_df["start_time"].apply(lambda x:str_to_time(x))
                    # cur_df["arrive_time"]=cur_df["arrive_time"].apply(lambda x:str_to_time(x))
                except Exception as e:
                    logger.error(f"切片错误，不存在指定的列名,当前列名{cur_df.columns.names}，指定列名{retain_cols}",f"{e}",update_time_type=UpdateTimeType.STEP)
                    pass
                
                cur_df.to_excel(w, sheet_name=train_name, index=False)
                logger.pop_target()
        return cur_path,dfs
            
    kind_map={"高铁":lst_G,"火车":lst_KTZ,"全部":lst_all}
    
    dest_path,dfs=_write_excel(kind_map.get(kind),kind)
    logger.stack_target(f"输出{dest_path}")
    logger.info("完成",update_time_type=UpdateTimeType.STAGE)
    logger.pop_target()
    
    logger.info("完成",update_time_type=UpdateTimeType.ALL)
            
    # 将原始结果输出到Excel文件
    # df = pd.DataFrame(org_list)
    # header=['简拼','站名','编码','全拼','缩称','站编号','城市编码','城市','国家拼音','国家','英文']
    # df.to_excel("org.xlsx", index=False, header=False)
    return dfs

def whole_routine(from_city,to_city,interchanges:list|tuple):
    results=[from_city]
    if interchanges:
        if isinstance(interchanges,str):
            interchanges=[interchanges]
        results.extend(interchanges)
    results.append(to_city)
    return results

import pickle
# 2. 序列化到本地文件
# ------------------------------
def serialize_df_list(df_list, file_path):
    """将DataFrame列表序列化到本地文件"""
    with open(file_path, 'wb') as f:
        # 使用pickle.dump序列化对象
        pickle.dump(df_list, f)
    print(f"已将DataFrame列表序列化到 {file_path}")

# # 保存到本地（推荐使用.pkl作为文件后缀）
# serialize_df_list(df_list, 'df_list.pkl')

# ------------------------------
# 3. 反序列化（从本地文件恢复）
# ------------------------------
def deserialize_df_list(file_path):
    """从本地文件反序列化DataFrame列表"""
    with open(file_path, 'rb') as f:
        # 使用pickle.load反序列化
        df_list = pickle.load(f)
    print(f"已从 {file_path} 反序列化DataFrame列表")
    return df_list



def unique_df_lst(df_list):
    
        
        # 初始化存储结果的列表和记录已出现标识的集合
    unique_dfs = []
    seen_train_nos = set()

    # 遍历列表中的每个DataFrame
    for df in df_list:
        # 跳过空DataFrame或不含'train_no'列的DataFrame（避免报错）
        if df.empty or 'train_no' not in df.columns:
            continue
        
        # 获取当前DataFrame中'train_no'列的第一个值
        first_train_no = df['train_no'].iloc[0]  # iloc[0]取第一行的值
        
        # 如果该标识未出现过，则保留当前DataFrame并记录标识
        if first_train_no not in seen_train_nos:
            seen_train_nos.add(first_train_no)
            unique_dfs.append(df)

    
    return unique_dfs


def dfs_to_trains(dfs):
            
    trains=[]    
    for df in dfs:
        train_name=None
        train_no=None
        
        stations=[]
        
        for index, row in df.iterrows():
            if not train_name:
                train_name=row["train_name"]
            if not train_no:
                train_no=row["train_no"]
            station_name = row['station_name']
            station_no=row['station_no']
            arrive_time=row["arrive_time"]
            start_time=row["start_time"]
            running_time=row["running_time"]

            stations.append(Station(station_name,str(arrive_time),str(start_time)))
        trains.append(Train(train_name,stations))
    
    return trains

#挑选路线车次
def handle_routine(start_station,end_station):
    
    bin_path=station_config.train_routines_path
    
    dfs=deserialize_df_list(station_config.train_routines_path)
    trains=dfs_to_trains(filter(lambda x:_train_type(x["train_name"][0]) not in ["G","D","C"] ,dfs))
    finder = TrainRouteFinder(trains)
    # 查找从上海虹桥站到广州南站的路线（最多换乘2次）

    logger=logger_helper("路线",f"{start_station}->{end_station}")
    org_routes = finder.find_transfer_routes(start_station, end_station, max_transfers=1)
    routes=TrainRouteFinder.classify_routes(org_routes)
    logger.info("成功",f"共找到 {len(routes)} 条路线",update_time_type=UpdateTimeType.STAGE)
    
    # 输出路线信息
    out_txt_path=station_config.result_txt_path(start_station=start_station,end_station=end_station)
    with open(out_txt_path,"w",encoding='utf-8-sig') as f:
        f.write(f"从 {start_station} 到 {end_station} 共找到 {len(routes)} 条路线：\n")
        for i,train_no in enumerate(routes,1):
            f.write(f'{"*" * 40}\n')
            
            cur_routes=routes[train_no]
            cur_count=len(cur_routes)
            f.write(f"路线 {i:02}:{'->'.join(train_no)},共{cur_count}个分线, 总耗时: {cur_routes[0].get_total_duration()}\n")

            f.write(f'{"-" * 20}\n')
                
            for j,route in enumerate(cur_routes,1):
                f.write(f"第{i:02}-{j}个分线：{route}")
                if j < cur_count:
                    f.write(f'{"-" * 20}\n')
            
    logger.info(f"已保存结果到 {out_txt_path}",update_time_type=UpdateTimeType.STAGE)
    # 可视化路线
    visualizer = TrainRouteVisualizer(figsize=(16, 30))
    visualizer.draw(org_routes, title=f"{start_station}到{end_station}的列车路线方案",pic_path=station_config.result_pic_path(start_station=start_station,end_station=end_station))
    pass

def fetch_train_routine(from_city: str, to_city: str, date: str="2025.08.26", kind:str="全部",transfer_cities:list[str|tuple]=[]):

    date=date.replace('.', '-')
    #换乘站
    option_citys=[
       whole_routine(from_city,to_city,citys)  for   citys in transfer_cities
    ]
    
    # print(option_citys)
    dfs=[]
    for index,cities in enumerate(option_citys):
        count=len(cities)
        index+=1
        for i in range(1,count):
            dfs.extend(rest_tickets(date, cities[i-1], cities[i], kind,f"0_{index}_{i}"))
            # time.sleep(1)
            dfs.extend(rest_tickets(date, cities[i], cities[i-1], kind,f"1_{index}_{count-i}"))
            time.sleep(1)
            
    serialize_df_list(dfs,station_config.train_routines_path)
            
def main():
    
    start_station = "上海"
    end_station = "西峡"
    transfer_cities=[
        ("南阳"),
        ("杭州"),
        ("合肥"),
        ("信阳"),
    ]
    #获取车次信息表，包含 各车站、出发时间、到达时间、时长信息
    #此过程耗时较长，若是获取过一次，可跳过此步骤
    # fetch_train_routine(start_station,end_station,date="2025.08.26",kind="全部",transfer_cities=transfer_cities)
    
    
    #获取推荐车次结果表
    #单程
    handle_routine(start_station,end_station)
    #返程
    handle_routine(end_station,start_station)
    
if __name__ ==  '__main__':    
    main()
    

