import re
import os
from pathlib import Path



def handle_credit_detail(data_path):

    cur_path=Path(data_path)

    with open(data_path,'r',encoding="utf-8-sig") as f:
        org_data = f.read().replace("\r","")
        # print(org_data)
        
        
        date_pattern = r'\d{1,}月\d{1,}日\n'
        
        
        matches = re.finditer(date_pattern, org_data)
        dates=[str(match.group(0)).strip("\n") for match in matches]
        # 使用正则表达式分割字符串
        split_result = re.split(date_pattern, org_data)
        datas=[]
        for data in split_result:
            each_data=[]
            for items in data.split("￼"):
                item=[val for val in items.strip().strip("\n").split("\n") if val]

                if len(item)>0:
                    each_data.append("\t".join(item))
            if len(each_data)>0:
                datas.append(each_data)
        # print(datas)
        # print(dates)

        with open(os.path.join(os.path.dirname(data_path),f"{cur_path.name}_detail.txt"),'w',encoding="utf-8") as f:
            for date,data in zip(dates,datas):
                for item in data:
                    f.write(f"{date}\t{item}\n")
                
        

    

if __name__=="__main__":
    handle_credit_detail(r"F:\个人\银行卡转账记录\mom.txt")
    handle_credit_detail(r"F:\个人\银行卡转账记录\me.txt")
    