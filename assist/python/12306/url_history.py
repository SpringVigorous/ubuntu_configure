import requests

cookies = {
    '_uab_collina': '175550955572785146880319',
    'JSESSIONID': 'FE73B0D030B4CC4547040A94A81D5E12',
    '_jc_save_wfdc_flag': 'dc',
    '_jc_save_zwdch_fromStation': '%u56FA%u59CB%2CGXN',
    '_jc_save_zwdch_cxlx': '0',
    '_c_WBKFRo': 'sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS',
    'OUTFOX_SEARCH_USER_ID_NCOO': '742496979.536112',
    'guidesStatus': 'off',
    'highContrastMode': 'defaltMode',
    'cursorStatus': 'off',
    'BIGipServerotn': '1893269770.24610.0000',
    'BIGipServerpassport': '937951498.50215.0000',
    'route': '495c805987d0f5c8c84b14f60212447d',
    '_jc_save_fromStation': '%u897F%u5CE1%2CSNH',
    '_jc_save_toStation': '%u5408%u80A5%2CHFH',
    '_jc_save_toDate': '2025-09-11',
    '_jc_save_fromDate': '2025-09-14',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': '_uab_collina=175550955572785146880319; JSESSIONID=FE73B0D030B4CC4547040A94A81D5E12; _jc_save_wfdc_flag=dc; _jc_save_zwdch_fromStation=%u56FA%u59CB%2CGXN; _jc_save_zwdch_cxlx=0; _c_WBKFRo=sraC6YRdJb6MbjH9xxa1sLa6fYmljIB032VpIYoS; OUTFOX_SEARCH_USER_ID_NCOO=742496979.536112; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; BIGipServerotn=1893269770.24610.0000; BIGipServerpassport=937951498.50215.0000; route=495c805987d0f5c8c84b14f60212447d; _jc_save_fromStation=%u897F%u5CE1%2CSNH; _jc_save_toStation=%u5408%u80A5%2CHFH; _jc_save_toDate=2025-09-11; _jc_save_fromDate=2025-09-14',
    'If-Modified-Since': '0',
    'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E8%A5%BF%E5%B3%A1,SNH&ts=%E5%90%88%E8%82%A5,HFH&date=2025-09-11&flag=N,N,Y',
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
    'leftTicketDTO.train_date': '2025-09-14',
    'leftTicketDTO.from_station': 'SNH',
    'leftTicketDTO.to_station': 'HFH',
    'purpose_codes': 'ADULT',
}

response = requests.get('https://kyfw.12306.cn/otn/leftTicket/queryG', params=params, cookies=cookies, headers=headers)
