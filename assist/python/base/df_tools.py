import pandas as pd
from com_log import logger_helper
import os
import concurrent.futures
import gc
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

#按相邻行填充数据（针对 合并单元格的操作）
def fill_adjacent_rows(df:pd.DataFrame, column_names:list[str]=None):
    if not column_names:
        column_names=df.columns.tolist()
    elif isinstance(column_names,str):
        column_names=[column_names]
        
    df[column_names] = df[column_names].ffill().bfill()
    return df

#保留前者的所有列，差异化添加后者列
def merge_df(df1,df2,on,how="inner",keep_first=True):
    if df1 is None:
        return df2
    if df2 is None:
        return df1
    
    
    if isinstance(on,str):
        on=[on]

    common_cols = df1.columns.intersection(df2.columns).difference(on).tolist()
    if common_cols:
        src_df=df1 if not keep_first else df2
        src_df.drop(columns=common_cols, inplace=True)

    df=pd.merge(df1,df2,on=on,how=how)
    return df
    
#返回值：稀疏，完整
def sparse_columns_name(df):
    
    # 计算每列的空值数量
    null_counts = df.isna().sum()
    # 总行数
    total_rows = len(df)
    # 筛选空值数量超过总行数一半的列名
    sparse_columns = null_counts[null_counts > total_rows / 2].index.tolist()
    whole_columns = null_counts[null_counts <= total_rows / 2].index.tolist()
    return sparse_columns,whole_columns

#根据keys进行唯一化，若是存在重复行，则只保留第一行已有值的项
def unique_df(df:pd.DataFrame,keys:list[str]):
    if df.empty or df is None:
        return df
    result_df = df.groupby(keys,sort=False).first().reset_index()
    return result_df

def concat_dfs(dfs:list[pd.DataFrame])->pd.DataFrame:
    
    
    dfs=list(filter(lambda x:not(x is None or x.empty),dfs)) if dfs else []
    if not dfs:
        return pd.DataFrame()
    
    if len(dfs)==1:
        return dfs[0]
    df=pd.concat(dfs,ignore_index=True)
    return df


def assign_col_numbers(df,col_num_name:str):
    existing_numbers = set(df[df[col_num_name] > 0][col_num_name])
    mask = df[col_num_name] <= 0 | df[col_num_name].isna()

    # print(type(mask))
    # print(mask)
    current_num = 1
    available_nums:list[int] = []
    
    for _ in range(sum(mask)):
        while current_num in existing_numbers:
            current_num += 1
        available_nums.append(current_num)
        current_num += 1
    
    # 更新num列
    df.loc[mask, col_num_name] = available_nums if available_nums else None
    return df


def update_col_nums(df:pd.DataFrame,group_key:str|list[str],col_num_name:str)->pd.DataFrame:

    def _assign_numbers(group):
        
        group=assign_col_numbers(group,col_num_name)
        # print(mask)
        
        vals=group.name
        col_names=group_key
        if isinstance(vals,str):
            vals=[vals]
        if isinstance(col_names,str):
            col_names=[col_names]
        
        for col,val in zip(col_names,vals):
            group[col] = val
        

        return group
    
    # 分组处理
    df = df.groupby(group_key, group_keys=False).apply(_assign_numbers, include_groups=False)
    
    print(df)
    
    df[col_num_name]=df[col_num_name].astype(int)


    return df

#多线程读入
def parallel_json_normalize(data, batch_size=20000,**kwargs)->pd.DataFrame:

    
    def process_batch(batch):
        return pd.json_normalize(batch, **kwargs)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        batches = [data[i:min(len(data),i + batch_size)] for i in range(0, len(data), batch_size)]
        results = list(executor.map(process_batch, batches))

    final_df = pd.concat(results, ignore_index=True)
    
    # 当不再使用时，删除 DataFrame
    
    for result in results:
        del result
   
    # 显式调用垃圾回收器

    gc.collect()
    
    return final_df

#优化输出
def optimized_to_excel(df:pd.DataFrame, file_path, batch_size=None):
    """
    优化的 DataFrame 写入 Excel 文件的函数。

    :param df: 要写入的 DataFrame
    :param file_path: 输出 Excel 文件的路径
    :param batch_size: 分批次写入时每批的行数，如果为 None 则不分批
    """
    options = {'check_formulas': False, 'strings_to_urls': False}
    with pd.ExcelWriter(file_path, engine='xlsxwriter', engine_kwargs={'options':options}) as writer:
        if batch_size is None:
            df.to_excel(writer, index=False, merge_cells=False)
        else:
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                sheet_name = f'Sheet_{i // batch_size}'
                batch.to_excel(writer, sheet_name=sheet_name, index=False, merge_cells=False)




def optimized_read_excel(file_path,sheet_name=None, engine='openpyxl', usecols=None):
    """
    优化读取 Excel 文件的函数。

    :param file_path: 要读取的 Excel 文件的路径
    :param engine: 读取 Excel 文件使用的引擎，默认为 'openpyxl'
    :param usecols: 要读取的列，默认为 None 即读取所有列
    :return: 读取得到的 DataFrame
    """
    if not sheet_name:
        sheet_name="Sheet1"
    
    df = pd.read_excel(file_path,sheet_name=sheet_name, engine=engine,  usecols=usecols)
    return df 
