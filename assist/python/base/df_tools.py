import pandas as pd
from com_log import logger_helper
import os

def find_values_by_col_val(df, col_name,val,dest_name,default_val=pd.Series()):

    log=logger_helper(f"二次查找:{val}",f"【{col_name}】列中查找,返回【{dest_name}】列,默认值:{default_val}")
    try:
        matches=df[col_name] == val
        results= df.loc[matches, dest_name]

        if results.empty:
            log.info("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        return results
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val


def matches_by_col_val_contains(df, col_name,val,default_val=pd.Series()):

    # 创建一个日志记录器，用于记录匹配操作的日志信息
    log=logger_helper(f"对应列匹配{val}",f"{col_name}列模糊查找")
    try:
        # 使用pandas的str.contains方法在指定列中查找包含指定值的行
        # case=False表示忽略大小写，na=False表示将NaN值视为False
        matches=df[col_name].str.contains(val, case=False, na=False)
        # 返回匹配结果
        return matches
    except:
        # 如果在执行过程中发生异常，记录错误日志
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        # 返回默认值
        return default_val
def find_values_by_col_val_contains(df, col_name,val,dest_name,default_val=pd.Series()):


    log=logger_helper(f"模糊查找:{val}",f"【{col_name}】列中查找,返回【{dest_name}】列,默认值:{default_val}")
    try:
        matches=matches_by_col_val_contains(df,col_name,val)
        if (matches==False).all():
            log.info("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        
        results= df.loc[matches, :]
        log.trace("成功",f"共【{results.shape[0]}】条：\n{results.to_string(index=False)}")
        # print(type(results))
        return results[dest_name]
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val 
    
    
    
    
    
        
def find_last_value_by_col_val(df, col_name,val,dest_name,default_val=None):
    vals=find_values_by_col_val(df, col_name,val,dest_name,default_val)
    if vals is None or vals.empty:
        return default_val
    return vals.iloc[-1]


def sheet_names(file_path):
    if not os.path.exists(file_path):
        return []
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

def flat_df(lst:list[list[dict]]):
    
    dfs=[]
    for item in lst:
        if not item:
            continue
        df=pd.DataFrame(item)
        if not df.empty:
            df["key"]=1
            dfs.append(df)
            
    dest=dfs[0]
    for index in range(1,len(dfs)):
        dest=pd.merge(dest,dfs[index],on="key")
    dest.drop("key",axis=1,inplace=True)
    return dest

def columns_index(df,columns:list[str]):
    return [df.columns.get_loc(col) for col in columns]
    
def move_columns_to_front(df, columns_to_move:list[str]):
    # 获取要移动的列
    cols = columns_to_move + [col for col in df.columns if col not in columns_to_move]
    # 重新排列列顺序
    return df[cols]