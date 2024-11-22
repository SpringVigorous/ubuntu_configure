import pandas as pd


def fun(df):
    print(df)
    df2=df.groupby('B').agg({'C': 'sum', 'D': 'first','F':"first"}).reset_index()
    # df3=df2.groupby('B')
    matches=df2['B']=="x"
    other_data=df2[~matches]
    matches_data=df2[matches]
    if not( matches.empty or other_data.empty): 
        sum_val=matches_data['C'].sum()
        other_data.loc[~matches,"F"]=other_data['C'].apply(lambda x: f"{x/sum_val:.2%}")
    df2=pd.concat([matches_data,other_data], axis=0)



    
    return df2


# 创建示例 DataFrame
data = {
    'A': [1, 1, 1, 2, 2, 2, 3, 3, 3],
    'B': ['x', 'y', 'x', 'y', 'x', 'y', 'x', 'y', 'x'],
    'C': [10, 20, 30, 40, 50, 60, 70, 80, 90],
    'D': ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'b', 'a'],
    'E': [100, 200, 300, 400, 500, 600, 700, 800, 900]
}
data["F"]=""

# print(data)

df = pd.DataFrame(data)

# 按 A 列进行分组
grouped_by_A = df.groupby('A')

# 在每个 A 列分组内，再按 B 列进行分组，并统计 C 列的合计值，同时保留 D 列
result = grouped_by_A.apply(fun, include_groups=False)
print(result)
print(type(result))

exit(0)



for  group in result:
    print(group)
    matches=group["B"]=="x"
    matches_rows=group[matches]
    other_rows=group[~matches]
    if not( matches_rows.empty or other_rows.empty): 
        sum_val=matches_rows['C'].sum()
        other_rows.loc[~matches,"F"]=other_rows['C'].apply(lambda x: f"{x/sum_val:.2%}")
    group=pd.concat([matches_rows,other_rows], axis=0)
    print(group)
    
# 重命名列名
# result.columns = ['A', 'B', 'C_sum', 'D']

# 输出结果
print(result)