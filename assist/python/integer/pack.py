#data 2维数组
def export_list2(file_path, data):
    dp_str="\n".join([  "\t".join(list(map(str, row)))  for row in data]   )        
    with open("pack.txt","w") as f:
        f.write(dp_str)

#（总重量，[索引号])
def package_items(items, bag_capacity,dp):
    sum_val=sum([item[1] for item in items])
    
    j=bag_capacity if sum_val>bag_capacity else sum_val
    item_count=len(items)
    
    result = []
    i = len(items)
    total_weight= dp[i][j]
    weight = total_weight
    while i > 0 and weight>0:
        if dp[i][weight] != dp[i - 1][weight]:
            # result.append(i - 1)
            vals=items[i - 1]
            
            result.append(vals[0])
            weight -= vals[1]
        i-=1
    # result.reverse()
    return (total_weight,result)



def min_bags_for_items(items, bag_capacity):
    # 对物品按重量从小到大排序
    items.sort(key=lambda x: x[1])

    # 初始化动态规划数组
    n = len(items)
    dp = [[0] * (bag_capacity + 1) for _ in range(n + 1)]
    # 初始状态：容量为0时所需背包数量为0
    for i in range(n + 1):
        dp[i][0] = 0

    # 动态规划填充
    for i in range(1, n + 1):
        weight = items[i - 1][1]
        for j in range(1, bag_capacity + 1):
            if weight > j:
                # 当前物品不能放入容量为j的背包中
                dp[i][j] = dp[i - 1][j]
            else:
                # 选择不放入当前物品的情况
                without_item = dp[i - 1][j]
                # 选择放入当前物品的情况
                with_item = dp[i - 1][j - weight] + weight
                
                # 选择总重量最大的
                dp[i][j] = max(without_item, with_item)
                
    export_list2("pack.txt",dp)
    return (package_items(items, bag_capacity,dp))
        
    # 返回所需的最少背包数量
    # return dp[n][bag_capacity]

def muti_min_bags_for_items(items, bag_capacity,result:list):
    
    item_vals=items[:]
    
    while(len(item_vals)>0):
        capacity,index= min_bags_for_items(item_vals, bag_capacity)
        result.append((capacity,index))
        for i in index:
            indices = [j for j, v in enumerate(item_vals) if v[0] == i]
            item_vals.pop(indices[0])


if __name__ == '__main__':
    # 物品列表，每个元素是一个二元组 (物品编号, 重量)
    items = [(1, 5), (2, 4), (3, 8), (4, 6), (5, 10), (6, 2)]
    bag_capacity = 15  # 背包的容量
    # min_bags = min_bags_for_items(items, bag_capacity)
    # print(f"Minimum number of bags required: {min_bags}")
    
    
    result=[]
    # 执行装箱算法
    muti_min_bags_for_items(items, bag_capacity,result)
    print(f"Minimum number of bags required: {result}")