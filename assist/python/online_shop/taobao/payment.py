


import re
import csv
import pandas as pd
import os



refund="退[费|款]|退回(积分)|佣金返还?"
cusume_payment="交易付款"
transfer_owner="店铺过户"
transfer_account="转账"
security="保证金"
trade_payments=[cusume_payment,"提现","结息","账户开户"]
small_payment="小额打款"
traffic_secuirty_normal="运费险"
traffic_secuirty="提升计划服务费"

trade_types = {
        "天猫佣金",
        "信用卡支付服务费",
        "花呗支付服务费",
        "淘宝客佣金",
        traffic_secuirty_normal,
        "先用后付",
        "代扣返点",
        "花呗分期",
        "品牌新享",
        "信用卡分期",
        traffic_secuirty,
        "基础软件服务费",
        "光合平台软件服务费",
        "跨境服务增值费",
        "自动充值",
        transfer_account,
        security,
        "结算"
}
traffic=f"集运物流|集运中转|{small_payment}"
# refund_grade="退回积分"

special_types=["淘宝客佣金",
               "花呗分期",
                "品牌新享",
                "信用卡分期",
                "光合平台软件服务费",
        "先用后付",
                "集运物流",
                "集运中转"
        ]

def order_num(data:str,note:str=None,serial_num=None)->str:

    data=data.strip("\t\n\r ")
    if note:
        note=note.strip("\t\n\r ")
    if serial_num:
        serial_num=serial_num.strip("\t\n\r ")
    
    if note:
        # pattern = r'淘宝订单号(\d+)(?=\D|$)'
        pattern = r'(?:交易单号|订单号|memberid)(?:[：  \:])?(\d+)(?=\D|$)'
        # 使用 re.search 查找匹配
        match = re.search(pattern, note)

        if match:
            return match.group(1)  # 提取订单号

    
    # 1. 提取第一个字符串最后一个 `==` 之后的数据
    pattern1 = r'==([^=]+)$'
    match1 = re.search(pattern1, data)
    if match1:
        return match1.group(1) 

    # 2. 提取第二个字符串 `P` 之后的数据
    pattern2 = r'P(\d+)'
    match2 = re.search(pattern2, data)
    if match2: 
        return  match2.group(1)
    # 3. 提取第三个字符串中的 `3951511311551140922`
    datas = data.split("_")
    if len(datas)>3:
        return  datas[2]
    
    num=data if data else str(serial_num)
    num=num.strip()
    # if not num:
    #     print(num)
    
    return num




def redund_flag(note):
    match=re.search(refund,note)
    if match:
        return match.group(0)
    return ""
def order_type(note,org_classify):
    #交易付款
    for item in trade_payments:
        if item in org_classify:
            return item 
    
    refund_str=redund_flag(note)
    type=""
    for trade_type in trade_types:
        if trade_type in note:
            type= trade_type
            break
        
        
    if not type:
        match = re.search(traffic, note)
        if match:
            type= match.group(0)
            if type in traffic_secuirty:
                type=traffic_secuirty_normal
            
    if not type and transfer_owner in note:
        type= cusume_payment
    
    lst=[refund_str,type]
    lst=[i for i in lst if i]
    if lst:
        return "_".join(lst)

    
    return "其他"





def get_index(val,lst):
    if lst.count(val)>0:
        return lst.index(val)
    else:
        return -1


def extract_data_from_csv(file_path):
    start_marker = "#-----------------------------------------账务明细列表----------------------------------------"
    end_marker = "#-----------------------------------------账务明细列表结束------------------------------------"
    
    data = []
    extracting = False
# , encoding='utf-8'
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        rows=[row for row in reader ]
        columns=[row[0]for row in rows]
        start_index=get_index(start_marker,columns)
        end_index=get_index(end_marker,columns)
        # if start_index<0:
        #     starty_index=0

        if end_index<0:
            end_index=len(rows)-1

    return rows[start_index+1:end_index]

def get_dataframe(file_path):
    # 调用函数并打印结果
    extracted_data = extract_data_from_csv(file_path)

    df = pd.DataFrame(extracted_data[1:], columns=extracted_data[0])
    return df.fillna(0)

def sort_date(df):
    df.sort_values(by=["发生时间",], ascending=[True,],inplace=True,ignore_index=True,axis=0)
    return df.reset_index(drop=True)

def data_scale(df):
    # col_names= df.columns.tolist()
    # col_names.remove("type")
    # # col_names.remove("order_id")
    # col_dic={i:"first"  for i in col_names}
    # col_dic["amount"]="sum"

    # df1= df.groupby('type',sort=False).agg(col_dic).reset_index()
    # df1= df.groupby('type',sort=False).agg({'amount': 'sum', '发生时间': 'first',"备注":'first'}).reset_index()
    df1= df.groupby('type',sort=False).agg({'amount': 'sum', '发生时间': 'first'}).reset_index()
    df1["scale"]=""
    type_series=df1["type"]
    # print(type_series,type(type_series))
    
    matches=type_series==cusume_payment
    matches_rows=df1.loc[matches,'amount']
    #保证金、运费险、提升计划服务费、交易付款 需要排除
    other_match=~type_series.isin([cusume_payment,security,traffic_secuirty_normal,traffic_secuirty])
    other_amount=df1.loc[other_match,'amount']
    if not( matches_rows.empty or other_amount.empty): 
        sum_val=matches_rows.sum()
        if sum_val<=0:
            return df1
        df1.loc[other_match,'scale']=other_amount.apply(lambda x: f"{x/sum_val:.2%}")
        # print(df1)
    return df1.reset_index(drop=True)

def handle_data(df,dir_path):
    df["order_id"]=df.apply(
            lambda row: order_num(
            row['商户订单号'],
            row['备注'],
            row['账务流水号']
            ),
            axis=1
        )
    df["type"]= df.apply(
            lambda row: order_type(
            row['备注'],
            row['业务类型'],
            ),
            axis=1
        )

    df['收入金额（+元）']=df['收入金额（+元）'].apply(float)
    df['支出金额（-元）']=df['支出金额（-元）'].apply(float)
    df["amount"]= df['收入金额（+元）']+df['支出金额（-元）']
    
    
    
    special_series=df["type"].isin(special_types)
    
    special_matches= df[special_series].copy()
    # 更新特殊类型的 fee 列
    df.loc[special_series, "fee"] = special_matches["amount"]
    special_sum=special_matches["amount"].sum()
    
    print(special_sum)

    id_group = df.groupby('order_id',sort=False)
    
    org_df=id_group.apply(sort_date, include_groups=False)
    merge_df = id_group.apply(data_scale, include_groups=False)

    with pd.ExcelWriter(os.path.join(dir_path,"汇总.xlsx")) as writer:
            org_df.to_excel(writer,sheet_name="org")
            merge_df.to_excel(writer,sheet_name="汇总")




def handle_file(file_path):
    # 替换所有列中的空值为 0
    df =get_dataframe(file_path)
    dir_path=os.path.dirname(file_path)
    handle_data(df,dir_path)


def handle_files(dir_path):
    datas=[]
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.csv') and "(汇总)" not in file_name:
            file_path = os.path.join(dir_path, file_name)
            data=get_dataframe(file_path)
            if  data.empty:
                continue
            datas.append(data)

            
    
    # 沿行合并
    df = pd.concat(datas, axis=0)
    handle_data(df,os.path.join(dir_path,"汇总"))
    
    
if __name__ == '__main__':
    # file_path=r"E:\公司文件\支付宝\20888416369216990156_202409_账务明细_1.csv"
    # handle_file(file_path)
    
    dir_path=r"E:\公司文件\支付宝"
    handle_files(dir_path)
    
    # num=order_num("HVmXOl8Y+l72omZSCO7U5fD51mZ1Znz7Me8jNjcjOWjHiCDgBWW01g==","淘宝联盟推广佣金返还 memberid:4150059357 fee:34.91 batchno:H_UGP_4150059357_MRAD20240812_0_p")
    # print(num)


