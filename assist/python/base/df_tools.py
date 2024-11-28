import pandas as pd
from com_log import logger_helper

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

    log=logger_helper(f"对应列匹配{val}",f"{col_name}列模糊查找")
    try:
        matches=df[col_name].str.contains(val, case=False, na=False)
        return matches
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val
def find_values_by_col_val_contains(df, col_name,val,dest_name,default_val=pd.Series()):

    if val=="玫瑰花":
        print(val)
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
