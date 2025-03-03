import pandas as pd
from time import time
from datetime import datetime


df=pd.read_excel(r"F:\教程\轮滑课\轮滑课.xlsx")

# 修改原始代码中的lambda表达式
df["time"] = df["时间"].apply(
    lambda x: datetime.strptime(x.split("-")[0].strip(), "%H:%M").time()
)

time_lst=  sorted(df["time"].unique().tolist())
day_lst=df["周"].unique().tolist()

dest_head=["时间"]
dest_head.extend(df["星期"].unique().tolist())

datas=[]

org_data={key:None for key in dest_head}
for item_time,item in df.groupby("time",sort=True):
    row_data=org_data.copy()
    row_data["时间"]=item["时间"].iloc[0]
    for index,row in item.iterrows():
        row_data[row["星期"]]=row["课程内容"]
        
    datas.append(row_data)
# 正确添加方式
dest_df = pd.DataFrame(datas)
dest_df.to_excel(r"F:\教程\轮滑课\轮滑课_new.xlsx",index=False)     
        
