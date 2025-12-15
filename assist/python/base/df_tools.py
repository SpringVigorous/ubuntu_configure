import pandas as pd
from base.com_log import logger_helper
import os
import concurrent.futures
import gc
from collections.abc import Iterable
from base.com_decorator import exception_decorator


import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Optional
def default_sheet_name()->str:
    return "Sheet1"
class DataFrameComparator:
    """
    用于比较两个具有相同列名的DataFrame的类
    支持根据指定列分离独有行、共有行，并提供详细的差异分析
    """
    
    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, key_columns: str|list[str]):
        """
        初始化比较器
        
        参数:
            df1: 第一个DataFrame
            df2: 第二个DataFrame  
            key_column: 用于比较的关键列名
        """
        self.df1 = df1.copy()
        self.df2 = df2.copy()
        self.set_key_columns(key_columns)
        
        # 存储比较结果
        self._merge_result = None
        self._dest_result = None
        self.logger=logger_helper("pandas.DataFrame 数据对比")
        
    def _special_result(self,type_key:str)->pd.DataFrame:
        """获取df1独有的行"""
        if self._dest_result is None:
            self.compare_dataframes()
        return self._dest_result[type_key] if type_key in self._dest_result.keys() else None
    @property
    def df1_only(self) -> pd.DataFrame:
        """获取df1独有的行"""
        return  self._special_result("df1_only")

    @property
    def df2_only(self) -> pd.DataFrame:
        """获取df2独有的行"""
        return  self._special_result("df2_only")
    
    @property
    def df_common(self) -> pd.DataFrame:
        """获取共有行"""
        return self._special_result("common")

    @property
    def df_org_common(self) -> pd.DataFrame:
        """获取共有行"""
        return self._special_result("org_common")
    
    @property
    def df1_suffix(self) -> pd.DataFrame:
        """获取df1的独有行"""
        return "_df1"

    @property
    def df2_suffix(self) -> pd.DataFrame:
        """获取df2的独有行"""
        return "_df2"
    
    def df1_column_name(self,name:str):
        return f"{name}{self.df1_suffix}"

    def df2_column_name(self,name:str):
        return f"{name}{self.df2_suffix}"
    def set_key_columns(self, key_columns: str|list[str]) -> None:
        self.key_columns = key_columns if isinstance(key_columns ,list) else [key_columns]
    
        
    @property
    def valid(self) -> bool:
        """验证两个DataFrame的结构是否一致"""
        if not self.df1.columns.equals(self.df2.columns):
            self.logger.error("异常","列名不完全一致，无法进行比较")
            return False
        def _check_key_columns(df: pd.DataFrame) -> bool:
            return all(col in df.columns for col in self.key_columns)
        
        if not( _check_key_columns(self.df1) and _check_key_columns(self.df2)):
            self.logger.error("异常",f"关键列 '{self.key_columns}' 不在DataFrame的列中")
            return False
            
        return True
    
    def compare_dataframes(self, how: str = 'outer') -> Dict[str, pd.DataFrame]:
        """
        比较两个DataFrame并返回分类结果
        
        参数:
            how: 合并方式 ('outer', 'inner', 'left', 'right')
            
        返回:
            包含分类结果的字典
        """
        # 执行合并操作
        self._merge_result = pd.merge(
            self.df1, self.df2, 
            on=self.key_columns, 
            how=how, 
            indicator=True,
            suffixes=(self.df1_suffix, self.df2_suffix)
        )
        
        # 分类结果
        df1_only = self._merge_result[self._merge_result['_merge'] == 'left_only'].copy()
        df2_only = self._merge_result[self._merge_result['_merge'] == 'right_only'].copy()
        org_common = self._merge_result[self._merge_result['_merge'] == 'both'].copy()
        
        # 还原列名（移除后缀）
        df1_only = self._restore_column_names(df1_only, include_suffix=self.df1_suffix,exclude_suffix=self.df2_suffix)
        df2_only = self._restore_column_names(df2_only, include_suffix=self.df2_suffix,exclude_suffix=self.df1_suffix)
        common = self.restore_common_columns(org_common)
        
        self._dest_result = {
            'df1_only': df1_only,
            'df2_only': df2_only,
            'common': common,
            'org_common':org_common,
        }
        
        return self._dest_result

    
    def _restore_column_names(self, df: pd.DataFrame, include_suffix: str,exclude_suffix:str=None) -> pd.DataFrame:
        """还原单个DataFrame的列名（针对独有部分）"""
        result_df = df.copy()
        
        # 选择包含指定后缀的列
        suffix_columns = [col for col in result_df.columns if col.endswith(include_suffix)]
        
        for col in suffix_columns:
            original_col = col.replace(include_suffix, '')
            if original_col not in self.key_columns:  # 关键列没有后缀
                result_df[original_col] = result_df[col]
                result_df.drop(columns=[col], inplace=True)
        
        if exclude_suffix:  # 删除指定后缀的列
            result_df.drop(columns=[col for col in result_df.columns if col.endswith(exclude_suffix)], inplace=True)
        
        
        # 删除辅助列
        if '_merge' in result_df.columns:
            result_df.drop(columns=['_merge'], inplace=True)
            
        return result_df
    
    # 智能选择：优先选择非空值，如果都非空则 按照keep_df1选择（True:df1 False:df2）的值
    def restore_common_columns(self, df: pd.DataFrame,keep_df1:bool=True) -> pd.DataFrame:
        """还原共有DataFrame的列名（智能选择策略）"""
        result_df = df.copy()
        
        # 获取所有非关键列的原列名
        data_columns = [col for col in self.df1.columns if col not in self.key_columns]
        
        def _dest_result(row,col_name1:str,col_name2:str):
            if keep_df1:
                return row[col_df1] if pd.notna(row[col_df1]) else row[col_df2]
            else:
                return row[col_df2] if pd.notna(row[col_df2]) else row[col_df1]
        
        for col in data_columns:
            col_df1 = f"{col}_df1"
            col_df2 = f"{col}_df2"
            if col_df1 in result_df.columns and col_df2 in result_df.columns:
                # 创建新列，智能选择值
                result_df[col] = result_df.apply(
                    lambda row: _dest_result(row,col_df1,col_df2), 
                    axis=1
                )
                
                # 删除带后缀的列
                result_df.drop(columns=[col_df1, col_df2], inplace=True)
        
        # 删除辅助列
        if '_merge' in result_df.columns:
            result_df.drop(columns=['_merge'], inplace=True)
            
        return result_df
    

    def get_detailed_differences(self) -> pd.DataFrame:
        """
        获取共有行中具体内容的差异[1,4](@ref)
        
        使用DataFrame.compare方法进行精确的元素级比较
        """
        if self._dest_result is None:
            self.compare_dataframes()
        
        common_df = self._dest_result['common']
        if len(common_df) == 0:
            return pd.DataFrame()
        
        # 设置关键列为索引
        df1_indexed = self.df1.set_index(self.key_columns)
        df2_indexed = self.df2.set_index(self.key_columns)
        
        # 获取共有的键值
        common_keys = common_df[self.key_columns].unique()
        df1_common = df1_indexed.loc[common_keys]
        df2_common = df2_indexed.loc[common_keys]
        
        try:
            # 使用compare方法进行精确比较[1](@ref)
            differences = df1_common.compare(df2_common, align_axis=0)
            if not differences.empty:
                differences = differences.droplevel(-1, axis=1).reset_index()
            return differences
        except Exception as e:
            print(f"详细比较时出现错误: {e}")
            return pd.DataFrame()
    

    def save_comparison_results(self, filepath: str) -> None:
        """将比较结果保存到Excel文件"""
        if self._dest_result is None:
            self.compare_dataframes()
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            self._dest_result['df1_only'].to_excel(writer, sheet_name='df1_独有', index=False)
            self._dest_result['df2_only'].to_excel(writer, sheet_name='df2_独有', index=False)
            self._dest_result['common'].to_excel(writer, sheet_name='两表共有', index=False)
            
            # 保存详细差异
            detailed_diff = self.get_detailed_differences()
            if not detailed_diff.empty:
                detailed_diff.to_excel(writer, sheet_name='详细差异', index=False)
        
        print(f"比较结果已保存到: {filepath}")




def find_rows_by_col_val(df, col_name,val,default_val=pd.DataFrame()):

    log=logger_helper(f"二次查找:{val}",f"【{col_name}】列中查找【{val}】")
    try:
        matches=df[col_name] == val
        results= df[matches]

        if results.empty:
            log.warn("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        return results
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val

def find_values_by_col_val(df, col_name,val,dest_name,default_val=pd.Series()):

    log=logger_helper(f"二次查找:{val}",f"【{col_name}】列中查找,返回【{dest_name}】列,默认值:{default_val}")
    try:

        match_df=find_sub_df_by_col_val(df,col_name,val)
        if df_empty(match_df):
            log.info("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        
        results= match_df[dest_name]
        if results.empty:
            log.info("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        return results
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val

@exception_decorator(error_state=False)
def find_sub_df_by_col_val(df, col_name,val):
    matches=df[col_name] == val
    return df[matches]
        
        
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
def find_by_col_val_contains(df, col_name,val,default_val=pd.DataFrame()):


    log=logger_helper(f"模糊查找:{val}",f"【{col_name}】列中查找")
    try:
        matches=matches_by_col_val_contains(df,col_name,val)
        if (matches==False).all():
            log.error("失败",f"没有找到匹配的值，返回默认值{default_val}")
            return default_val
        
        results= df.loc[matches, :]
        log.trace("成功",f"共【{results.shape[0]}】条：\n{results.to_string(index=False)}")
        # print(type(results))
        return results
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val 
    
    
def find_values_by_col_val_contains(df, col_name,val,dest_name,default_val=pd.Series()):
    results= find_by_col_val_contains(df,col_name,val,default_val)
    
    log=logger_helper(f"模糊查找:{val}",f"【{col_name}】列中查找,返回【{dest_name}】列")
    if df_empty(results):
        return default_val
    try:
        return results[dest_name]
    except:
        log.error("异常",f"没有找到匹配的值，返回默认值{default_val}")
        return default_val
    

    
    
        
def find_last_value_by_col_val(df, col_name,val,dest_name,default_val=None):
    vals=find_values_by_col_val(df, col_name,val,dest_name,default_val)
    if vals is None:
        return default_val
    if isinstance(vals,pd.DataFrame) or isinstance(vals,pd.Series):
        if vals.empty:
            return default_val
        if isinstance(vals,pd.Series):
            return list(filter(lambda x:x ,vals))[-1]
        return vals.iloc[-1]
    return vals


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
    if df_empty(df):
        return df
    result_df = df.groupby(keys,sort=False).first().reset_index()
    return result_df

def unique_df_last(df:pd.DataFrame,keys:list[str]):
    if df_empty(df):
        return df
    result_df = df.groupby(keys,sort=False).last().reset_index()
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
    mask =df[col_num_name] < 0 | df[col_num_name].isna()

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
    
    # print(df)
    
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


#根据keys进行唯一化，每列数据 保留第一个有效值
def concat_unique(dfs:list[pd.DataFrame],keys)->pd.DataFrame:

    return unique_df(concat_dfs(dfs),keys=keys)



def content_same(df1:pd.DataFrame,df2:pd.DataFrame):
    
    
    
    df1_reset = df1.reset_index(drop=True)
    df2_reset = df2.reset_index(drop=True)

    return df1_reset.equals(df2_reset)


#交集
def intersect_df(df1:pd.DataFrame,df2:pd.DataFrame,keys:list|str)->pd.DataFrame:
    intersection = pd.merge(df1, df2, on=keys, how='inner')
    return intersection
    
#差集
def sub_df(df1:pd.DataFrame,df2:pd.DataFrame,keys:list|str)->pd.DataFrame:
    if df1.empty or  df2.empty:
        return  df1
    # 统一转换为list处理
    keys = [keys] if isinstance(keys, str) else keys
    df1_only=df1[keys].astype(str).agg(','.join, axis=1)
    df2_only=df2[keys].astype(str).agg(','.join, axis=1)
    mask=df1_only.isin(df2_only)
    diff_result = df1[~mask]
    
    
    return diff_result.copy()


#添加属性名
def set_attr(df:pd.DataFrame,attr_name:str,attr_value:str)->pd.DataFrame:
    if df is None:
        return df
    df.attrs[attr_name]=attr_value
    return df

def get_attr(df:pd.DataFrame,attr_name:str)->str:
    if df is None:
        return None
    return df.attrs.get(attr_name)
@exception_decorator(error_state=False)
def df_empty(df:pd.DataFrame)->bool:
    if not is_df(df):
        return True
    
    return df.empty

@exception_decorator(error_state=False)
def is_df(df:pd.DataFrame)->bool:
    if df is None:
        return False
    
    return isinstance(df,pd.DataFrame)



def add_df(src_df:pd.DataFrame,dest_df:pd.DataFrame,unique_cols:str|Iterable[str]=None)->pd.DataFrame:
    if df_empty(src_df):
        return dest_df
    
    
    if df_empty(dest_df):
        dest_df=src_df
    else:
        dest=concat_dfs([dest_df,src_df])
        if unique_cols :
            if isinstance(unique_cols,str):
                unique_cols=[unique_cols]
            dest_df=unique_df(dest,keys=unique_cols)
    return dest_df

def update_df(src_df:pd.DataFrame,dest_df:pd.DataFrame,unique_cols:str|Iterable[str]=None)->pd.DataFrame:
    dest_df=add_df(src_df,dest_df,unique_cols)
    if unique_cols :
        dest_df=unique_df_last(dest_df,keys=unique_cols)
    return dest_df



#获取所有的dfs
@exception_decorator(error_state=False)
def read_xlsx_dfs(xlsx_path:str)->dict[str,pd.DataFrame]:
    results={}
    with pd.ExcelFile(xlsx_path) as reader:
        for name in reader.sheet_names:
            df=reader.parse(name)
            if df_empty(df):
                continue
            results[name]=df   
    return results


@exception_decorator(error_state=False)
def get_df(xlsx_path:str,sheet_name:str)->pd.DataFrame:
    return read_xlsx_dfs(xlsx_path).get(sheet_name,None)




# 使用示例
if __name__ == "__main__":
    # 创建示例数据
    data1 = {
        'relative_path_id': ['001', '002', '003', '004'],
        'file_name': ['a.txt', 'b.txt', 'c.txt', 'd.txt'],
        'file_size': [100, 200, 300, 400],
        'modification_time': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04']
    }
    
    data2 = {
        'relative_path_id': ['002', '003', '005', '006'],
        'file_name': ['b.txt', 'c_modified.txt', 'e.txt', 'f.txt'],
        'file_size': [200, 350, 500, 600],  # 003的file_size不同
        'modification_time': ['2023-01-02', '2023-01-05', '2023-01-05', '2023-01-06']
    }
    
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    
    # 使用比较器
    comparator = DataFrameComparator(df1, df2, key_columns='relative_path_id')
    
    
    # 访问具体结果
    print("\nDF1 独有数据:")
    print(comparator.df1_only)
    
    print("\nDF2 独有数据:")
    print(comparator.df2_only)
    
    print("\n两表共有数据:")
    print(comparator.df_common)
    
    print("\n合并数据:")
    print(comparator._merge_result)