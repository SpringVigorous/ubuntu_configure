import sys
import os
import pandas as pd
import datetime
import time


from  base.clipboard import to_clipboard
from calculate_rest_days import cur_consume_to_paydays,cur_cycle_to_paydays
from base.email.special_email import send_emails_by_config
from base.string_tools import exe_dir,convert_to_html_table,html_table_to_str,cur_date_str



def org_sheet_df(file_path, sheet_name)->pd.DataFrame:
    org_df = pd.read_excel(file_path, sheet_name=sheet_name)
    return org_df


def repay_days_sheet_df(df,current_date)->pd.DataFrame:
    # 删除 `valid` 列
    # df = df.drop(columns=['valid',"limit"])
    # 将 `billday_included` 的空值替换为 0
    df['billday_included'] = df['billday_included'].fillna(0)
    df['billing_day'] = df['billing_day'].fillna(0)
    df['repayment_day'] = df['repayment_day'].fillna(0)
    df['num'] = df['num'].fillna("")


    # 将相关列转换为整型
    df['billing_day'] = df['billing_day'].astype(int)
    df['repayment_day'] = df['repayment_day'].astype(int)
    df['billday_included'] = df['billday_included'].astype(int)

    df['num'] = df['num'].astype(str)

    # 添加新列 `next_rest_day` 并计算对应的值
    df['next_rest_day'] = df.apply(
        lambda row: cur_consume_to_paydays(
            current_date,
            int(row['billing_day'])+(0 if bool(row['billday_included']) else 1),
            int(row['repayment_day'])
            
        ),
        axis=1
    )
    df['cur_rest_day'] = df.apply(
        lambda row: cur_cycle_to_paydays(
            current_date,
            int(row['repayment_day'])
        ),
        axis=1
    )
    # 根据 `next_rest_day` 列从大到小排序
    df.sort_values(by='next_rest_day', ascending=False, inplace=True)
        

    # 输出 HTML 表格
    return  df


def rearrage_df(org_df)->dict:
    
    df_dict={}
    for owner,df in org_df.groupby("owner"):
        df_dict[owner]=df.copy()
    all_df=org_df.copy()
    all_df["credit"]=all_df.apply(lambda row: f'{row.name:02d}:{row["owner"]}_{row['credit']}',axis=1)
    all_df["owner"]="all"
    df_dict["all"]=all_df
    return  df_dict

def repay_days_sheet_dfs(org_df,current_date)->dict:

    df_dict={}
    for owner,df in rearrage_df(org_df).items():
        df_dict[owner]=repay_days_sheet_df(df,current_date)

        
    # 输出 HTML 表格
    return  df_dict


def repay_days_sheet_html(org_df, current_date):

    tab_dict={}
    df_dict= repay_days_sheet_dfs(org_df,current_date)
    for owner,df in df_dict.items():
                # 将 DataFrame 转换为 HTML 表格
        html_table = df.to_html(index=False, classes=['table', 'table-bordered'])

        # 创建包含二级标题和表格的 HTML 字符串
        html_content = f"""
        <div style="text-align: center; margin: 0 auto; width: fit-content;">
            <h2>{current_date}-最佳刷卡表({owner})</h2>
            {html_table}
        </div>
        """
        tab_dict[owner]=html_content

    return  tab_dict
    print(html_table)


    body=f"当前日期：\t{current_date}\n" + "\t".join(df.columns) + "\n" + "\n".join("\t".join( map(str,  row)) for row in df.values)

    return  body



def recommend_credit_card(org_df,current_date,attachment_path:str|list=None):

    
    result_dict= repay_days_sheet_html(org_df,current_date)
    # print(html_table_to_str(result))

    # send_email(f"{current_date}最大还款时间",convert_to_html_table(result) ,body_type='html')
    send_emails_by_config(f"{current_date}推荐用卡",result_dict ,body_type='html',attachment_path=attachment_path)
    # to_clipboard(result)

import matplotlib.pyplot as plt
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


# 30种颜色 - 相邻色差极大序列（跨色系轮询排列，视觉区分度最高）
high_contrast_30_colors = [
    # 第1轮跨色系：红→蓝→绿→橙→紫→深棕
    "#e74c3c",  # 红（红色系）
    "#3498db",  # 亮蓝（蓝紫系）
    "#2ecc71",  # 草绿（绿色系）
    "#f39c12",  # 亮橙（橙黄系）
    "#9b59b6",  # 玫紫（蓝紫系）
    "#34495e",  # 深灰（中性系）
    # 第2轮跨色系：深红→深蓝→深绿→深橙→深紫→炭黑
    "#c0392b",  # 深红（红色系）
    "#2980b9",  # 深蓝（蓝紫系）
    "#27ae60",  # 深绿（绿色系）
    "#e67e22",  # 深橙（橙黄系）
    "#8e44ad",  # 深紫（蓝紫系）
    "#2c3e50",  # 炭黑（中性系）
    # 第3轮跨色系：砖红→藏蓝→茶绿→土黄→茄紫→咖啡
    "#d35400",  # 砖红（红色系）
    "#000080",  # 藏蓝（蓝紫系）
    "#16a085",  # 茶绿（绿色系）
    "#d4ac0d",  # 土黄（橙黄系）
    "#6c3483",  # 茄紫（蓝紫系）
    "#795548",  # 咖啡（中性系）
    # 第4轮跨色系：玫红→钴蓝→薄荷绿→金黄→紫罗兰→深棕
    "#ec407a",  # 玫红（红色系）
    "#4169e1",  # 钴蓝（蓝紫系）
    "#1abc9c",  # 薄荷绿（绿色系）
    "#f1c40f",  # 金黄（橙黄系）
    "#9932cc",  # 紫罗兰（蓝紫系）
    "#5d4037",  # 深棕（中性系）
    # 第5轮跨色系：橙红→湖蓝→青绿→亮黄→纯紫→藏青
    "#ff7f0e",  # 橙红（红色系/橙黄系过渡）
    "#00bfff",  # 湖蓝（蓝紫系）
    "#38ada9",  # 青绿（绿色系）
    "#ff7f0e",  # 亮黄（橙黄系，补充）
    "#800080",  # 纯紫（蓝紫系）
    "#003366"   # 藏青（中性系/蓝紫系过渡）
]
def get_color(i:int):
    return  high_contrast_30_colors[i%len(high_contrast_30_colors)]

def arrage_month_figure(org_df:pd.DataFrame,duration=31)->dict:

    
    dfs=[]
    for i in range(0,duration):  
        current_date = datetime.datetime.now().date()+datetime.timedelta(days=i)
        df=repay_days_sheet_df(org_df.copy(),current_date)
        df["cur_date"]=current_date
        dfs.append(df)

    all_df=pd.concat(dfs,axis=0)
    
    # 设置图形大小为 2560x1440 像素，假设 DPI 为 100
    figure_dict={}
    for owner,df in rearrage_df(all_df).items():
        
        df.drop(columns=["billing_day","repayment_day","billday_included","limit"], inplace=True)
        
        # print(df.columns.to_list())


        # 假设 df 是你的 DataFrame
        df["credit_num"] = df.apply(lambda x: f"{x['credit']}-{x['num']}", axis=1)

        plt.figure(figsize=(25.6, 14.4), dpi=100)
        # 计算y值的最小值和最大值
        y_min = df['next_rest_day'].min()
        y_max = df['next_rest_day'].max()

        # 计算x值的最小值和最大值
        x_min = df['cur_date'].min()
        x_max = df['cur_date'].max()
        plt.xlim(x_min, x_max)
        
        # 添加水平虚线
        for y in range(y_min, y_max + 1):
            plt.hlines(y, x_min, x_max, colors='gray', linestyles='dashed', linewidth=1)

        # 添加垂直虚线
        for x in pd.date_range(start=x_min, end=x_max, freq='D'):
            plt.vlines(x, y_min, y_max, colors='gray', linestyles='dashed', linewidth=1)
            
        title_dict={}
        color_index=0
        color_dict={}
        for credit_num, item_df in df.groupby("credit_num"):
            color=get_color(color_index)
            color_index+=1
            item_df.sort_values(by='cur_date', ascending=True, inplace=True)
            cur_date_item=item_df['cur_date']
            rest_item=item_df['next_rest_day']
            plt.step(cur_date_item, rest_item, label=f'{credit_num}', marker='o', where='post',color=color)
            
            
            # 在第一个数据点的顶部添加 credit_num 文字
            if not item_df.empty:
                first_x = cur_date_item.iloc[0]
                first_y =rest_item.iloc[0]
                pos=(first_x, first_y)
                
                color_dict[pos]=color
                
                if title_dict.get(pos, None) is None:
                    title_dict[pos]=[credit_num]
                else:
                    title_dict[pos].append(credit_num)
                    
        for key, credit_nums in title_dict.items():
            first_x, first_y = key
            plt.text(first_x, first_y+.2, f'{";".join(credit_nums)}\n', fontsize=9, ha='center', va='bottom',color=color_dict[key])
            # for index,credit_num in enumerate(credit_nums):

        
        # 添加图例
        plt.legend()

        # 添加标签和标题
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title(f'{duration}天【{owner}】的推荐用卡')

        # 在节点上显示数值
        for credit_num, item_df in df.groupby("credit_num"):
            for x, y in zip(item_df['cur_date'], item_df['next_rest_day']):
                plt.text(x, y, f'{y}', fontsize=9, ha='right')
        # 增加 X 轴刻度数量
        plt.xticks(rotation=45)  # 旋转刻度标签以避免重叠
        # plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=duration))  # 设置刻度数量
        # 设置 X 轴主刻度位置，每 天一个刻度
        import matplotlib.ticker as ticker
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(base=1))
        # 自动调整子图参数
        plt.tight_layout()
        # 显示图形
        # plt.show()

        # 保存图形到本地
        save_path = os.path.join(exe_dir(), f'{owner}_{cur_date_str()}.png')
        plt.savefig(save_path)
        plt.close()
        figure_dict[owner]=save_path


    return figure_dict
    
    

#N天的推荐用卡u
def main(day_duration=1):
    file_path = os.path.join(exe_dir(),'credit_info.xlsx')
    sheet_name = 'credit_info'
    org_df=org_sheet_df(file_path, sheet_name)
    org_df.drop(columns=["valid"],inplace=True)
    #N天的数据
    figure_dict=arrage_month_figure(org_df,31)
    figures=list(figure_dict.values())
    
    #M天的记录，每天一个邮件
    for i in range(0,day_duration):  
        current_date = datetime.datetime.now().date()+datetime.timedelta(days=i)
        recommend_credit_card(org_df,current_date,attachment_path=figures)
        time.sleep(2)  

    pass


    
    
    
    

if __name__ == '__main__':
    # arrage_month_figure(31)
    # exit(0)
    main()
