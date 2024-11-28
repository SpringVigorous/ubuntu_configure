import pandas as pd
from com_log import logger_helper


def find_value_by_col_val(df, col_name,val,dest_name,default_val=None):

    log=logger_helper("二次查找值",f"df[df[{col_name}]=={val},{dest_name}],{default_val}")
    try:
        matches=df[col_name] == val
        results= df.loc[matches, dest_name]
        if results.empty:
            log.info("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        return results.iloc[-1]
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val