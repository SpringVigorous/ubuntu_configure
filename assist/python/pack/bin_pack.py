import binpacking

# 一维固定容量装箱
items = [4, 8, 1, 4,6,3,2,7,5,1]
bins = binpacking.to_constant_volume(items, 10)
print(bins)

# 多维装箱（需字典格式）
items = [{'volume':4, 'weight':2}, {'volume':8, 'weight':3}]
bins = binpacking.to_constant_bin_number(items, 2, weight_pos='weight')
print(bins)
