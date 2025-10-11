import requests
import pandas as pd
import sys

from pathlib import Path
from datetime import datetime
import os



from base import exception_decorator,logger_helper,UpdateTimeType,df_empty,arabic_numbers,unique,whole_url
from train_station import TrainStationManager
from station_config import StationConfig
class TicketUrl:
    
    @exception_decorator(error_state=False)
    @staticmethod
    def add_date(df:pd.DataFrame,date:str)->pd.DataFrame:
        if not df_empty(df):
            df["date"]=date

        return df
    @exception_decorator(error_state=False)
    @staticmethod
    def query_prices(from_station, to_station, train_date)->pd.DataFrame:
        train_date=train_date.replace(".","-")
        
        logger=logger_helper("url获取票价",f"{from_station}->{to_station} {train_date}")
        
        
        station_manager=TrainStationManager()
        from_url_cookie=station_manager.city_cookie_param(from_station)
        to_url_cookie=station_manager.city_cookie_param(to_station)
        from_station_no =station_manager.code_from_city(from_station)  # 北京西
        to_station_no = station_manager.code_from_city(to_station)     # 上海虹桥
        cookies = {
            'JSESSIONID': '32AA71172EAC0D2A681FA19A5D0AA4C5',
            '_jc_save_wfdc_flag': 'dc',
            '_jc_save_zwdch_fromStation': from_url_cookie,
            '_jc_save_zwdch_cxlx': '0',
            '_c_WBKFRo': 'sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS',
            'OUTFOX_SEARCH_USER_ID_NCOO': '742496979.536112',
            'BIGipServerotn': '1658388746.24610.0000',
            'BIGipServerpassport': '820510986.50215.0000',
            'guidesStatus': 'off',
            'highContrastMode': 'defaltMode',
            'cursorStatus': 'off',
            'route': 'c5c62a339e7744272a54643b3be5bf64',
            '_jc_save_toDate': train_date,
            '_jc_save_fromStation': from_url_cookie,
            '_jc_save_toStation': to_url_cookie,
            '_jc_save_fromDate': train_date,
            '_jc_save_fromStation': from_url_cookie,
            '_jc_save_toStation': to_url_cookie,
            '_jc_save_fromDate': train_date,
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': 'JSESSIONID=32AA71172EAC0D2A681FA19A5D0AA4C5; _jc_save_wfdc_flag=dc; _jc_save_zwdch_fromStation=%u56FA%u59CB%2CGXN; _jc_save_zwdch_cxlx=0; _c_WBKFRo=sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS; OUTFOX_SEARCH_USER_ID_NCOO=742496979.536112; BIGipServerotn=1658388746.24610.0000; BIGipServerpassport=820510986.50215.0000; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_toDate=2025-09-08; _jc_save_fromStation=%u897F%u5CE1%2CSNH; _jc_save_toStation=%u5408%u80A5%2CHFH; _jc_save_fromDate=2025-09-10; _jc_save_fromStation=%u897F%u5CE1%2CSNH; _jc_save_toStation=%u5408%u80A5%2CHFH; _jc_save_fromDate=2025-09-10',
            'Referer': 'https://kyfw.12306.cn/otn/view/queryPublicIndex.html',
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
            'leftTicketDTO.train_date': train_date,
            'leftTicketDTO.from_station': from_station_no,
            'leftTicketDTO.to_station': to_station_no,
            'purpose_codes': 'ADULT',
        }

        response = requests.get(
            'https://kyfw.12306.cn/otn/leftTicketPrice/queryAllPublicPrice',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        datas=[item["queryLeftNewDTO"] for item in response.json()["data"]]
        
        df=TicketUrl.add_date(pd.DataFrame(datas),train_date)
        if df_empty(df): 
            return df
        
        
        df["train_type"]=df["station_train_code"].apply(lambda x:x[0])
        StationConfig().add_route_key_to_df(from_station,to_station,df)
        
        name=",".join(unique(df["station_train_code"].tolist()))
        logger.info("完成",f"共{len(df)}个车次，车次如下\n{name}\n",update_time_type=UpdateTimeType.ALL)
        return df
            
    @exception_decorator(error_state=False)
    @staticmethod
    def query_train_info(train_no,date)->pd.DataFrame:
        logger=logger_helper(f"url途径信息:{train_no} {date}")
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
        url=whole_url('https://kyfw.12306.cn/otn/queryTrainInfo/query', params=params)
        logger.update_target(detail=url)
        response = requests.get(url, cookies=cookies, headers=headers)
        logger.trace(response.reason)

        df= TicketUrl.add_date(pd.DataFrame(response.json()["data"]["data"]),date)
        if df_empty(df):
            logger.warn("异常",f"获取信息为空，详情{response.url}",update_time_type=UpdateTimeType.STAGE)
            
            return df
        df["train_no"]=train_no
        
        col_name="station_train_code"
        name= "/".join(unique(df["station_train_code"].tolist())) if col_name in df.columns else ""
        logger.info("完成",f"{name}车次，共{len(df)}站",update_time_type=UpdateTimeType.STAGE)
        return df
    @exception_decorator(error_state=False)
    @staticmethod    
    def __handle_rest_ticket(info_list:list)->dict:
        station_manager=TrainStationManager()
        def _train_type(train_name):
            train_type=train_name[0] 
            if arabic_numbers(train_type):
                train_type="0"
            return train_type
        
        @exception_decorator(error_state=False)
        def str_to_time(time_str:str)->datetime:
            try:
                return datetime.strptime(time_str, "%H:%M").time()
            except:
                return 

        train_num=info_list[2]
        citys=info_list[4:8]
        info_list[4:8] = [station_manager.city_from_code(i) for i in citys]


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
        return dic
        
    @exception_decorator(error_state=False)
    @staticmethod
    def query_rest_ticket(from_station, to_station,date)->pd.DataFrame:
        logger=logger_helper(f"url获取火车票信息:{from_station}->{to_station}:{date}")
        
        
        station_manager=TrainStationManager()
        from_url_cookie=station_manager.city_cookie_param(from_station)
        to_url_cookie=station_manager.city_cookie_param(to_station)
        cookies = {
            '_uab_collina': '175550955572785146880319',
            'JSESSIONID': 'FE73B0D030B4CC4547040A94A81D5E12',
            '_jc_save_wfdc_flag': 'dc',
            '_jc_save_zwdch_cxlx': '0',
            '_c_WBKFRo': 'sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS',
            'OUTFOX_SEARCH_USER_ID_NCOO': '742496979.536112',
            'guidesStatus': 'off',
            'highContrastMode': 'defaltMode',
            'cursorStatus': 'off',
            'route': '495c805987d0f5c8c84b14f60212447d',
            'BIGipServerotn': '1356398858.24610.0000',
            'BIGipServerpassport': '887619850.50215.0000',
            '_jc_save_zwdch_fromStation': from_url_cookie,
            '_jc_save_fromStation': from_url_cookie,
            '_jc_save_toStation': to_url_cookie,
            '_jc_save_fromDate': date,
            '_jc_save_toDate': date,
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Cookie': '_uab_collina=175550955572785146880319; ___rl__test__cookies=1755665093121; JSESSIONID=7D7D874B1DF46F5EAE2CC1BBE6824E21; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; _jc_save_wfdc_flag=dc; BIGipServerotn=1591279882.50210.0000; BIGipServerpassport=887619850.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_toDate=2025-08-20; _jc_save_zwdch_fromStation=%u56FA%u59CB%2CGXN; _jc_save_zwdch_cxlx=0; _c_WBKFRo=sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS; _nb_ioWEgULi=; OUTFOX_SEARCH_USER_ID_NCOO=742496979.536112; _jc_save_fromStation=%u897F%u5CE1%2CXIF; _jc_save_toStation=%u4FE1%u9633%2CXUN; _jc_save_fromDate=2025-08-29',
            'If-Modified-Since': '0',
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
        url=whole_url('https://kyfw.12306.cn/otn/leftTicket/queryG', params=params)
        logger.update_target(detail=url)
        response = requests.get(url, cookies=cookies, headers=headers)
        logger.trace(response.reason,update_time_type=UpdateTimeType.STAGE)   
        logger.stack_target("解析响应结果")    
        lst=[]
        for item in response.json()['data']['result']:
            if not item:
                continue
            info_list=item.split("|")
            result=TicketUrl.__handle_rest_ticket(info_list)
            if not result:
                continue
            lst.append(result) 
        logger.pop_target()
        df=TicketUrl.add_date(pd.DataFrame(lst),date) if lst else None
        StationConfig().add_route_key_to_df(from_station,to_station,df)
        
        logger.info("完成",f"共{len(lst)}条，车次详情：\n{','.join(df["车次"].to_list())}\n",update_time_type=UpdateTimeType.ALL)   
        return df
    
    @exception_decorator(error_state=False)
    @staticmethod
    def query_station_map()->pd.DataFrame:
        
        code_url = r"https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
        logger=logger_helper("url获取车站代码表信息",code_url)
        
        
        response = requests.get(code_url)
        response.encoding = 'utf-8'
        code_data = response.text
        # 处理每个匹配项，按 | 分割
        ls=code_data.split("@")[1:]
        # 处理每个匹配项，按 | 分割
        result = [match.split('|') for match in ls if match]
        df = pd.DataFrame(result)
        header=['简拼','站名','编码','全拼','缩称','站编号','城市编码','城市','国家拼音','国家','英文']
        df.columns = header
        logger.info("完成",f"共{len(df)}个",update_time_type=UpdateTimeType.ALL)
        return df
    
if __name__ == '__main__':
    from_city="上海"
    to_city="南阳"
    date="2025-09-20"
    kind="全部"
    name_prefix=""
    df=TicketUrl.query_station_map()
    print(f"\n站点代码表\n{df}")
    df=TicketUrl.query_train_info("5l000G147608",date)
    print(f"\n途径信息\n{df}")

    df=TicketUrl.query_rest_ticket( from_city, to_city, date)
    print(f"\n余票信息\n{df}")

    df=TicketUrl.query_prices( from_city, to_city, date)
    print(f"\n票价信息\n{df}")