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
from calculate_rest_days import next_repay_days_rest,cur_repay_days_rest
from base.email.special_email import send_email
from base.string_tools import exe_dir,convert_to_html_table,html_table_to_str





def repay_days_sheet(file_path, sheet_name,current_date):


    df = pd.read_excel(file_path, sheet_name='credit_info')


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
        lambda row: next_repay_days_rest(
            current_date,
            int(row['repayment_day']),
            int(row['billing_day']),
            bool(row['billday_included'])
        ),
        axis=1
    )
    df['cur_rest_day'] = df.apply(
        lambda row: cur_repay_days_rest(
            current_date,
            int(row['repayment_day'])
        ),
        axis=1
    )
    # 根据 `next_rest_day` 列从大到小排序
    df.sort_values(by='next_rest_day', ascending=False, inplace=True)
    
    # 将 DataFrame 转换为 HTML 表格
    html_table = df.to_html(index=True, classes=['table', 'table-bordered'])

    # 输出 HTML 表格
    return  html_table
    print(html_table)


    body=f"当前日期：\t{current_date}\n" + "\t".join(df.columns) + "\n" + "\n".join("\t".join( map(str,  row)) for row in df.values)

    return  body



def main():
    file_path = os.path.join(exe_dir(),'credit_info.xlsx')
    sheet_name = 'credit_info'
    current_date = datetime.datetime.now().date()

    result= repay_days_sheet(file_path, sheet_name,current_date)
    # print(html_table_to_str(result))

    # send_email(f"{current_date}最大还款时间",convert_to_html_table(result) ,body_type='html')
    send_email(f"{current_date}推荐用卡",result ,body_type='plain')
    # to_clipboard(result)


if __name__ == '__main__':
    main()
