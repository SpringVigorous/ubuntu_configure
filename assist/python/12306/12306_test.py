import re

# 原始数据
data = "@bjb|北京北|VAP|beijingbei|bjb|0|0357|北京|||@bjd|北京东|BOP|beijingdong|bjd|1|0357|北京|||@bji|北京|BJP|beijing|bj|2|0357|北京|||@bjn|北京南|VNP|beijingnan|bjn|3|0357|北京|||@bjx|北京大兴|IPP|beijingdaxing|bjdx|4|0357|北京|||@bjx|北京西|BXP|beijingxi|bjx|5|0357|北京|||"

# 正则表达式匹配以@开头，|||结尾的内容
pattern = r'@([^|]+(?:\|[^|]+)*)\|\|\|'

# 查找所有匹配项
matches = re.findall(pattern, data)

# 处理每个匹配项，按 | 分割
result = [match.split('|') for match in matches]

# 打印结果
for item in result:
    print(item)