import os
import pandas as pd
from pathlib import Path

def auto_start(org_lst,start=0,diff=.1):
    entries=[]
    for i in range(len(org_lst)):
        
        if i==0:
            start_time=start
        else:
            start_time=org_lst[i-1][0]+diff
        end_time=org_lst[i][0]
        entries.append((start_time,end_time,org_lst[i][1]))
    return entries

def generate_srt(org_lst, output_file="output.srt"):
    """
    生成SRT字幕文件
    
    参数:
    entries (list of tuples): 包含(开始时间(秒), 结束时间(秒), 字幕文本)的列表
    output_file (str): 输出文件路径
    """
    entries=auto_start(org_lst)
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(entries):
            # 转换时间格式为SRT要求的HH:MM:SS,mmm
            

            
            start_time = f"{int(start//3600):02}:{int(start%3600//60):02}:{(start%60):06.3f}".replace('.', ',')
            end_time = f"{int(end//3600):02}:{int(end%3600//60):02}:{(end%60):06.3f}".replace('.', ',')
            
            # 写入字幕块
            f.write(f"{idx+1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

if __name__ == "__main__":
    '''正则替换
    (.*),(.*)
    [$1,$2],
    '''

    
    # org_lst=[
    # [0.9,"亲爱的朋友们"],
    # [3,"今天给大家推荐一家超棒的酒店"],
    # [5.3,"臻月唐酒店新天地店"],
    # [8,"这是一家充满中式唐文化韵味的酒店"],
    # [8.4,"步入其中"],
    # [10,"仿佛穿越回了唐朝"],
    # [12.5,"能让您沉浸式感受唐文化的魅力"],
    # [14.5,"而且我们现在有超值的优惠活动"],
    # [15.6,"只需 99 元"],
    # [18.7,"您就可以享受 2 天 1 夜的舒适住宿"],
    # [19.5,"酒店干净卫生"],
    # [21.2,"让您住得安心、舒心"],
    # [23.5,"另外，我们还提供免费停车服务"],
    # [25.7,"为您的出行解决后顾之忧"],
    # [27.5,"无论是休闲度假还是商务出行"],
    # [30.2,"臻月唐酒店新天地店都是您的理想之选"],
    # [32.2,"别再犹豫啦，赶快预定"],
    # [35,"来体验这独特的住宿之旅吧"],

    # ]

    

    
    src_xls=r"F:\教程\字幕\自定义字幕.xlsx"
    df=pd.read_excel(src_xls,sheet_name="字幕")
    org_lst=list(zip(df["time"].tolist(),df["text"].tolist()))
    
    dest_dir = r"F:\教程\短视频教程\抖音\轻松学堂\21天课\钉钉消息\实战\素材\发布考核1-横版"
    
    dest_name=f"{Path(dest_dir).name}.srt"
    os.makedirs(dest_dir,exist_ok=True)
    generate_srt(org_lst, os.path.join(dest_dir,dest_name))
    
    
    df.to_csv(os.path.join(dest_dir,dest_name.replace(".srt","-字幕.csv")),index=False,encoding="gbk")
    