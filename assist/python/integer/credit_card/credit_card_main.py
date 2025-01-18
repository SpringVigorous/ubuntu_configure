import sys
import os
import pandas as pd
import datetime

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

from  base.clipboard import to_clipboard
from calculate_rest_days import cur_consume_to_paydays,cur_cycle_to_paydays
from base.email.special_email import send_emails
from base.string_tools import exe_dir,convert_to_html_table,html_table_to_str


def repay_days_sheet_df(file_path, sheet_name,current_date)->pd.DataFrame:
    org_df = pd.read_excel(file_path, sheet_name='credit_info')
    df_dict={}
    for owner,df in org_df.groupby("owner"):

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
        
        df_dict[owner]=df
        
    # 输出 HTML 表格
    return  df_dict


def repay_days_sheet(file_path, sheet_name,current_date):

    tab_dict={}
    df_dict= repay_days_sheet_df(file_path, sheet_name,current_date)
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



def recommend_credit_card(cur_date_offset=0):
    file_path = os.path.join(exe_dir(),'credit_info.xlsx')
    sheet_name = 'credit_info'
    current_date = datetime.datetime.now().date()+datetime.timedelta(days=cur_date_offset)

    
    result_dict= repay_days_sheet(file_path, sheet_name,current_date)
    # print(html_table_to_str(result))

    # send_email(f"{current_date}最大还款时间",convert_to_html_table(result) ,body_type='html')
    send_emails(f"{current_date}推荐用卡",result_dict ,body_type='html')
    # to_clipboard(result)

import time
#N天的推荐用卡
def main(day_duration=1):
    for i in range(0,day_duration):  
        recommend_credit_card(i)
        time.sleep(2)  
    # recommend_credit_card()
    pass


if __name__ == '__main__':
    main(8)
