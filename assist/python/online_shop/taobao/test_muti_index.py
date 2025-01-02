import pandas as pd

# 创建示例数据
data = {
    'Category': ['Electronics', 'Electronics', 'Clothing', 'Clothing', 'Electronics'],
    'Subcategory': ['Phone', 'Phone', 'Shirt', 'Pants', 'Tablet'],
    'Sales': [100, 200, 150, 120, 180]
}

df = pd.DataFrame(data)

print("原始数据:")
print(df)

# 按 Category 和 Subcategory 分组，并计算每个分组的总销售额
result = df.groupby(['Category', 'Subcategory'],sort=True).apply(lambda x: x['Sales'].sum())

print(f"\n分组后的结果:{result.index.tolist()}")
print(result)
# 使用 .loc 筛选 Category 为 Clothing 的数据

result_df = result.reset_index(name='Total_Sales')
print(result_df)


clothing_df = result_df.loc[result_df['Category'] == 'Clothing']

print(clothing_df)