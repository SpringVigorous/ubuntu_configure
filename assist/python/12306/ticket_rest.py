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

from base import exception_decorator,logger_helper,UpdateTimeType,arabic_numbers,unique,pickle_dump,pickle_load,df_empty,singleton,add_df,RAIITool,wrapper_lamda
from station_config import StationConfig
station_config=StationConfig(max_transfers=3)
station_config.set_same_wait_time(1,200)
station_config.set_diff_wait_time(60,200)



from station_routine import *
from train_route_visualizer import TrainRouteVisualizer
from ticket_url import TicketUrl

from ticket_price import PriceManager
station_manager=TrainStationManager()

def whole_routine(from_city,to_city,interchanges:list|tuple):
    results=[from_city]
    if interchanges:
        if isinstance(interchanges,str):
            interchanges=[interchanges]
        results.extend(interchanges)
    results.append(to_city)
    return results


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



#列车信息表
@exception_decorator(error_state=False)
def df_to_train(df):
    train_name=[]
    train_no=None
    stations=[]
    logger=logger_helper("df_to_train")
    for index, row in df.iterrows():
        name=row["station_train_code"]
        train_name.append(name)
        try:
            train_no=row["train_no"]
            station_name = row['station_name']
            station_no=row['station_no']
            arrive_time=row["arrive_time"]
            start_time=row["start_time"]
            running_time=row["running_time"]
            stations.append(Station(station_name,str(arrive_time),str(start_time)))
        except Exception as e:
            logger.error("异常",f"{e}\n{row}\n",update_time_type=UpdateTimeType.STEP)
    train_name="/".join(unique(train_name))
    logger.update_target(detail=train_name)
    
    logger.trace("完成",update_time_type=UpdateTimeType.STAGE)
    return Train(train_name,stations,train_no)


@exception_decorator(error_state=False)
def dfs_to_trains(dfs):
    logger=logger_helper("dfs_to_trains")  
    trains=[]    
    for df in dfs:
        train=df_to_train(df)
        if train:
            trains.append(train)
    logger.trace("完成",update_time_type=UpdateTimeType.STAGE)
    return trains

@exception_decorator(error_state=False)
def _caculate_route(start_station,end_station,dfs):
    if not dfs:
        return
    trains=dfs_to_trains(filter(lambda x:x.iloc[0]["train_type"] not in ["G","D","C"] ,dfs))
    finder = TrainRouteFinder(trains)
    # 查找从上海虹桥站到广州南站的路线（最多换乘2次）

    logger=logger_helper("挑选路线",f"{start_station}->{end_station}")
    
    pic_path=station_config.result_pic_path(start_station=start_station,end_station=end_station)
    
    
    result_pkl_path=station_config.result_pkl_path(start_station=start_station,end_station=end_station)
    exist_cache=os.path.exists(result_pkl_path)
    org_routes = finder.find_transfer_routes(start_station, end_station, max_transfers=1) 
    logger.info("成功",f"共找到 {len(org_routes)} 条路线",update_time_type=UpdateTimeType.STAGE)

    return org_routes



#挑选路线车次
@exception_decorator(error_state=False)
def handle_routine(start_station,end_station,org_routes:list[Route])->list[Route]:
    if not org_routes:
        return

    # 查找从上海虹桥站到广州南站的路线（最多换乘2次）
    logger=logger_helper("处理路线结果",f"{start_station}->{end_station}")
    routes=TrainRouteFinder.classify_routes(org_routes)

    
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
    

    pic_path=station_config.result_pic_path(start_station=start_station,end_station=end_station)
    
    visualizer.draw(org_routes, title=f"{start_station}到{end_station}的列车路线方案",pic_path=pic_path)


    return org_routes

from train_route_info import TrainRouteManager,TrainInfoManager

@exception_decorator(error_state=False)
def fetch_train_routine(from_city: str, to_city: str, date: str="2025.08.26", kind:str="全部",transfer_cities:list[str|tuple]=[]):

    date=date.replace('.', '-')
    
    #换乘站
    option_citys=[
       whole_routine(from_city,to_city,citys)  for   citys in transfer_cities
    ]
    
    dfs:dict={}
    route_manager=TrainRouteManager()
    info_manager=TrainInfoManager()
    price_manager=PriceManager()
    logger=logger_helper("获取车次信息表",f"{from_city}->{to_city}:{date}")
    
    for index,cities in enumerate(option_citys):
        count=len(cities)
        index+=1
        for i in range(1,count):
            
            cur_start_city,cur_end_city=cities[i-1],cities[i]
            
            with RAIITool(wrapper_lamda(logger.stack_target,detail=f"{cur_start_city}->{cur_end_city}:{date}"),
                          wrapper_lamda(logger.pop_target)) :
                
                # logger.stack_target(detail=f"{cur_start_city}->{cur_end_city}:{date}")
                route_df=route_manager.train_route(cur_start_city, cur_end_city, date)
                price_df=price_manager.query_df(cur_start_city, cur_end_city)
                
                def train_names(df):
                    return   ",".join(sorted(df["车次"])) if not df_empty(df) else ""
                route_name=train_names(route_df)
                price_name=train_names(price_df)
                if route_name!=price_name:
                    logger.trace("车次差异",f"\ntrain_route:{route_name}\ntiket_price:{price_name}\n")
                
                #车次时刻表，总是有误;合并用
                df=add_df(route_df,price_df,"编号")
                if df_empty(df):
                    # logger.pop_target()
                    continue
                for _, row in df.iterrows():
                    # train_no,type,train_name =row["编号"],row["类型"],row["车次"]
                    train_no,type,train_name =row["编号"],row["类型"],row["车次"]
                    if train_no in dfs:
                        logger.trace("忽略",f"{train_name}重复")
                        continue
                    cur_df=info_manager.train_info(train_no,date)
                    if df_empty(cur_df):
                        continue
                    cur_df["train_type"]=type
                    dfs[train_no]=(cur_df)
                    
                # logger.pop_target()
            
    logger.info("完成",f"共获取 {len(dfs)} 条车次信息表",update_time_type=UpdateTimeType.STAGE)
    return list(dfs.values())
@exception_decorator(error_state=False)

def find_routine(start_station,end_station,date:str,transfer_cities):
    logger=logger_helper("火车票路线",f"{start_station}->{end_station}:{date}")
    #获取车次信息表，包含 各车站、出发时间、到达时间、时长信息
    #此过程耗时较长，若是获取过一次，可跳过此步骤
    result_pkl_path=station_config.result_pkl_path(start_station=start_station,end_station=end_station)
    exist_cache=os.path.exists(result_pkl_path)
    # 读取缓存
    org_routes = pickle_load(result_pkl_path)  if exist_cache else None
    if not org_routes:
        logger.stack_target(detail="获取车次信息表")
        dfs=[]
        dfs=fetch_train_routine(start_station,end_station,date=date,kind="全部",transfer_cities=transfer_cities)
        logger.info("完成",f"{len(dfs)}条",update_time_type=UpdateTimeType.STAGE)
        logger.pop_target()
        #获取推荐车次结果表
        org_routes=_caculate_route(start_station,end_station,dfs)
        pickle_dump(org_routes,result_pkl_path)

    routes=handle_routine(start_station,end_station,org_routes)
    if routes:
        logger.info("完成",f"共{len(routes)}条可选路线",update_time_type=UpdateTimeType.ALL)
           
@exception_decorator(error_state=False) 
def main():
    start_station = "上海"
    end_station = "西峡"
    transfer_cities=[
        ("南阳"),
        ("杭州"),
        ("合肥"),
        ("信阳"),
    ]

    # station_config.clear_result_cache()
    # station_config.clear_train_info_df()
    # station_config.clear_train_route_df()
    # station_config.clear_price_df()
    
    logger=logger_helper("火车票路线筛选")
    days_latter=3
    date=days_latter_format(offset=days_latter)
    #单例初始化
    price=PriceManager(date)
    #单程
    find_routine(start_station,end_station,date,transfer_cities)
    #返程
    find_routine(end_station,start_station,date,transfer_cities)
    
    logger.info("完成",update_time_type=UpdateTimeType.STAGE)
    
    station_config.save_xlsx()
    
    
if __name__ ==  '__main__':    
    main()
