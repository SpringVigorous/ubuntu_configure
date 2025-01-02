﻿import pandas as pd
import os
import requests
from PIL import Image
import re
def is_cloth(title:str):
    pattern = r'赠品|手提包|面罩|帽|袋|背包|冲锋包'
    match = re.search(pattern, title)
    return not bool(match) 

    

def convert_image_to_jpg(image_path,dest_path=None)->bool:

    if not dest_path:
        dest_path=image_path

    if not os.path.exists(image_path):
        return False
    # 打开图片
    image = Image.open(image_path).convert('RGB')
    image.save(dest_path, 'JPEG')



dir_path = r"E:\公司文件\库存"
stock_name="店铺商品资料_20250101190939_67455346_1.xlsx"
collect_name="副本全店价格表1月1号.xlsx"
dest_dir=os.path.join(dir_path, "结果")
os.makedirs(dest_dir, exist_ok=True)

color_map={"01":"军绿",
        "02":"灰色",
        "03":"黑色",
        "04":"藏青色",
        "05":"卡其色",
        "06":"白色",
        "07":"蓝色",
        "09":"荣冰蓝",
        "10":"柠檬绿",
        "11":"黄色",
        "12":"橘红色",
        "13":"紫色",
        "15":"酒红",
}

def get_color_name(color_index):
    # if not color_index:
    #     return ""
    
    name=color_map.get(color_index,"")
    if not name and color_index:
        print(f"颜色索引：【{color_index}】未找到")
        return f"【{color_index}】"
    
    return name


df_stock = pd.read_excel(os.path.join(dir_path, stock_name), sheet_name="Sheet1", dtype=str)
df_stock= df_stock[~df_stock['线上商品编码'].str.contains('-')]
# 应用 is_cloth 函数并筛选 DataFrame
df_stock = df_stock[df_stock['线上商品名称'].apply(is_cloth)]


df_stock.rename(columns={"线上商品编码":"商品编码",'线上商品名称':"名称"},inplace=True)
# 处理商品编码列
df_stock['修正编码'] = df_stock['商品编码'].apply(lambda x: x[:-1] if len(x) == 13 else x)

row_data=df_stock["修正编码"].str
df_stock["color_index"]=row_data[-5:-3]
df_stock["size"]=row_data[-3:]
df_stock["num"]=df_stock["商品编码"].apply(lambda x: x[:-5] if len(x)>6 else x)



df_stock.sort_values(by=['num',"color_index","size"],ascending=[True,True,True],inplace=True)



stock_name="实际库存"
picture_name="图片"


df_collect=pd.read_excel(os.path.join(dir_path, collect_name), sheet_name="Sheet1", dtype=str)
df_collect.dropna(subset=['货号'],inplace=True)
# 删除 '货号' 列长度小于 5 的行
df_collect = df_collect[df_collect['货号'].str.len() >= 5]

dest_num_name='货号编码'


# 根据“编码”列进行内连接
merged_df = pd.merge(df_stock, df_collect, on='商品编码', how='inner')
# merged_df = pd.merge(df_stock, df_collect, on='商品编码', how='outer', indicator=True)
merged_df["颜色"]=merged_df["color_index"].apply(get_color_name)
# merged_df.sort_values(by=['num',"color_index","size"],ascending=[True,True,True],inplace=True)




detail_path=os.path.join(dest_dir, "detail_result.xlsx")
merged_df.to_excel(detail_path, index=False)

# exit(0)

dest_df=merged_df[['图片','季节', "num","名称","颜色", "size",'销售价','成本价', '店铺库存']].copy()

dest_df.rename(columns={
    'num': dest_num_name,
    'size': "尺码",
}, inplace=True)

# 填充 NaN 值或删除包含 NaN 值的行
# 这里选择填充 NaN 值为 0

dest_df.fillna(0, inplace=True)

dest_df.loc[:,"成本价"]=dest_df["成本价"].astype(float)
dest_df.loc[:,"店铺库存"]=dest_df["店铺库存"].astype(int)
def cal_product_price(group):
    # 计算每种药材的总价
    total_price = (group["成本价"]  *group["店铺库存"]).sum()
    # 计算每种药材的总质量
    total_collect = group["店铺库存"].sum()
    
    # 返回一个包含总价格和总质量的 Series
    return pd.Series({
        "总成本": total_price,
        "总库存": total_collect
    })



#汇总信息-总价值及总库存
summary_df=dest_df.groupby([dest_num_name]).apply(cal_product_price,include_groups=False).reset_index()


# pictures_df=dest_df.drop_duplicates(subset=['num'])
picture_dir=os.path.join(dir_path, "图片")
os.makedirs(picture_dir, exist_ok=True)

picture_map={}


# 根据 "num" 列进行分组，并获取每个组中 "图片" 列的值

rawgrouped = dest_df.groupby(dest_num_name)

#货品信息
def get_goods_info(grouped):
    raw_urls=grouped["图片"].tolist()
    
    return pd.Series({
        "名称":grouped["名称"].iloc[0],
        "urls":list( list(dict.fromkeys(raw_urls))),
                     "季节":grouped["季节"].iloc[0],
                     "产品数目":len(raw_urls)})
goods_df=dest_df.groupby(dest_num_name).apply(get_goods_info,include_groups=False).reset_index()



# 遍历汇总表，获取 "图片" 列的值
import aiohttp
import asyncio


#下载某一个图片
async def _download_image(session, url, cur_path):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            with open(cur_path, 'wb') as f:
                f.write(await response.read())
            convert_image_to_jpg(cur_path, cur_path)
            return url
    return None

#从备选中，下载一个图片，直到成功下载为止
async def download_image(session, urls, num):
    cur_path = os.path.join(picture_dir, f"{num}.jpg")
    if os.path.exists(cur_path):
        return num,urls[0],cur_path
    dest_url=None
    for url in urls:
        dest_url=await  _download_image(session, url, cur_path)
        if  dest_url:
            break
    return num,dest_url,cur_path


async def download_images(df):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, row in df.iterrows():
            num=row[dest_num_name]
            urls=row["urls"]
            task = asyncio.create_task(download_image(session, urls, num))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        results_map={num:(url,path) for num,url,path in results if url}
        for idx, row in df.iterrows():
            num=row[dest_num_name]
            result_info= results_map.get(num)
            if result_info and result_info[0]:
                df.loc[idx,"path"]=result_info[1]
                df.loc[idx,"url"]=result_info[0]
            else:
                urls=row["urls"]
                print(f"{num} 图片下载失败,{urls}")

# 使用示例
asyncio.run(download_images(goods_df))
goods_df.to_excel(os.path.join(dest_dir, "商品信息.xlsx"), index=False)

for idx, row in goods_df.iterrows():
    
    num=row[dest_num_name]
    path=row["path"]
    count=row["产品数目"]
    picture_map[num]=(path,count)


#导出merge_df结果
dest_price_path=os.path.join(dest_dir, "price_result.xlsx")
dest_path=os.path.join(dest_dir, "merge_result.xlsx")
summary_df.to_excel(dest_price_path, index=False)

from openpyxl import Workbook
from openpyxl.drawing.image import Image
# 创建一个新的Excel工作簿
wb = Workbook()
ws = wb.active
ws.title = "库存信息"



# 将DataFrame写入Excel工作表


# 使用 .loc 方法将“图片”列赋值为空字符串
# dest_df.loc[:, '图片'] = ''
# 获取表头
headers = dest_df.columns.tolist()

# 写入表头
for c_idx, header in enumerate(headers, start=1):
    ws.cell(row=1, column=c_idx, value=header)
for r_idx, row in enumerate(dest_df.itertuples(index=False), start=1):
    for c_idx, value in enumerate(row, start=1):
        ws.cell(row=r_idx+1, column=c_idx, value=value)


already_exist_num=[]
from openpyxl.styles import Alignment


def merge_column_cells(ws, start_row, start_col, row_count):

    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row+row_count-1, end_column=start_col)
    ws.cell(row=start_row, column=start_col).alignment = Alignment(horizontal='center', vertical='center')





# 将图片插入到第一列的单元格中
for idx, row in dest_df.iterrows():
        num=   row[dest_num_name] 
        if num in already_exist_num:
            continue
        already_exist_num.append(num)
        img_info =picture_map.get(num)
        
        if  not  img_info:
            continue
        img_path,count=img_info
        
        row_index=idx+2
        if not img_path:
            continue
        if os.path.exists(img_path):
                img = Image(img_path)
                # 调整图片大小（可选）
                img.width = 100
                img.height = 100
                # 计算图片插入的位置
                cell = ws.cell(row=row_index, column=1)  

                # 设置行高
                if count<3:
                    ws.row_dimensions[row_index].height = img.height                
                ws.add_image(img, cell.coordinate)
                
        merge_column_cells(ws, row_index, 1, count)    
        merge_column_cells(ws, row_index, 2, count)    
        merge_column_cells(ws, row_index, 3, count)    
        merge_column_cells(ws, row_index, 4, count)    
        
                
        # # 合并前两行和前两列
        # ws.merge_cells(f'A{row_index}:A{row_index+count-1}')
        # # 设置合并单元格的对齐方式（可选）
        # cell = ws[f'A{row_index}']
        # ws.cell(row=row_index, column=1).alignment = Alignment(horizontal='center', vertical='center')
        # cell.alignment = Alignment(horizontal='center', vertical='center')
# 保存Excel文件
# 设置列宽
ws.column_dimensions["A"].width = 10

ws.freeze_panes = 'A2'  # 冻结首行


wb.save(dest_path)