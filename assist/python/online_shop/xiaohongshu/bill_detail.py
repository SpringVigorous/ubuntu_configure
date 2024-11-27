import pandas as pd
import os

#小红书账单



def merge_dfs(dest_lst,key):
    dest_lst=[df for df in dest_lst if df is not None]
    if not dest_lst:
        return  pd.DataFrame()
    # 初始化合并后的 DataFrame
    merged_df = dest_lst[0] 
    # 依次合并剩余的 DataFrame

    # 依次合并剩余的 DataFrame
    for i, df in enumerate(dest_lst[1:], start=1):
        suffixes = (f'_{i}', f'_{i+1}')
        merged_df = pd.merge(merged_df, df, on='订单号', how='outer', suffixes=suffixes)
    return merged_df


def get_sheet_names(file_path):
    """
    获取 Excel 文件中的所有表单名称
    :param file_path: Excel 文件路径
    :return: 表单名称列表
    """
    # 创建 ExcelFile 对象
    excel_file = pd.ExcelFile(file_path)
    # 获取所有表单名称
    sheet_names = excel_file.sheet_names
    return sheet_names

def handle_files(dir_path):
    normal_name="订单销售"
    back_name="订单退款"
    carriage_name="运费宝"
    
    sheet_names=[
        normal_name,
        back_name,
        carriage_name,
        "寄件服务",
        "增值辅助服务",
        "运费报销",
        "薯券",
        "极速退款赔付",
        "小额打款",
        "分期免息补贴",
        "申诉调账",
        "人工调账",
    ]
    except_name="总览"
    org_dfs={}


    
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.xlsx') and "明细" not in file_name:
            file_path = os.path.join(dir_path, file_name)
            # 获取所有表单名称
            for name in get_sheet_names(file_path):
                if name ==except_name:
                    continue
                df=pd.read_excel(file_path, sheet_name=name)
                if org_dfs.get(name):
                    org_dfs[name].append(df)
                else:
                    org_dfs[name]=[df]


    # 拼接 DataFrame 列表
    merged_dfs={name: pd.concat(dfs, ignore_index=True).sort_values(by='结算时间', ascending=[True,],ignore_index=True,axis=0) if dfs else pd.DataFrame()   for name,dfs in org_dfs.items() }
    #merge()
    dest_lst=[
        merged_dfs.get(normal_name),
        merged_dfs.get(back_name),
        merged_dfs.get(carriage_name)
    ]
    # 初始化合并后的 DataFrame
    merged_df = merge_dfs(dest_lst,'订单号')
    with pd.ExcelWriter(os.path.join(os.path.dirname(dir_path), '合并账单.xlsx')) as writer:
            for name,org_df in merged_dfs.items():
                org_df.to_excel(writer,sheet_name=name)
            if not merged_df.empty:
                merged_df.to_excel(writer,sheet_name="汇总")

    return merged_df


if __name__ == '__main__':
    dir_path = r'E:\公司文件\小红书\账单'
    

    
    merged_df = handle_files(dir_path)
