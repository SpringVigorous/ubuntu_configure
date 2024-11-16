import re
import pandas as pd

# 原始文本
text = """
美容养颜茶:玫瑰花3g,菊花1朵,太子参5g,获苓5g,何首乌5g;补肾
健脾祛湿:获苓6g,薏米（熟）6g,何首乌（生）5g,玫瑰花2g,荷叶5g;(何首乌->补肾,玫瑰花->美容养颜)
安神茶:熟枣仁3g,太子参(生)5g,茯苓5g,夜交藤3g,百合5g
通中焦:佛手3-5g,香橼5g,山楂片5g,陈皮3-5g,生甘草0.5-1g
气血双补茶:黄芪5g,当归5g,茯苓5g,荷叶5g,西洋参3-5g,玫瑰花2朵,大枣2g;(脾胃四君子)
明目护眼茶:决明子3-5g,菊花3g,荷叶3-5g;(荷叶->排湿减肥)
四神汤:党参5g,芡实5g,黄芪5g,莲子5g
清肝火:夏枯草6g,金钱草6g,五味子(生)3g,佛手3g;(疏肝)
养心安神茶:桂园肉5g,西洋参3g,百合5g,山楂1-3g
"""



"""车次	出发站
到达站	出发时间
到达时间	历时	商务座
特等座	优选
一等座	一等座	二等座
二等包座	高级
软卧	软卧/动卧
一等卧	硬卧
二等卧	软座	硬座	无座	其他	备注
G1476
复
上海虹桥
南阳东
09:5116:06
06:15
当日到达
1
--	
1
有	--	--	--	--	--	--	--	预订
G1532
上海虹桥
南阳东
11:5219:31
07:39
当日到达
1
--	
15
有	--	--	--	--	--	--	--	预订
G1810
智复
上海虹桥
南阳东
12:5219:24
06:32
当日到达
6
--	
17
有	--	--	--	--	--	--	--	预订
K282
铺
上海
南阳
20:4514:35
17:50
次日到达
--	--	--	--	--	候补	候补	--	有	有	--	预订"""
# 正则表达式模式
pattern = re.compile(r'(\w+):((?:\w+[\(（]?\w*[\)）]?\s*\d+(\.\d+)?(?:-\d+)?[g朵]*,?\s*)+)(;\S+.*?)?\n', re.DOTALL)

# 提取信息
matches = pattern.findall(text)

# 进一步处理成分，分离名称和用量
teas = []
for match in matches:
    name = match[0]
    ingredients_str = match[1].strip()
    function = match[3][1:].strip('()') if match[3] else None
    
    # 提取成分名称和用量
    ingredients = []
    for ingredient in ingredients_str.split(','):
        ingredient = ingredient.strip()
        if ingredient:
            parts = re.match(r'(\w+[\(（]?\w*[\)）]?)\s*(\d+(\.\d+)?(?:-\d+)?[g朵]*)', ingredient)
            if parts:
                ingredient_name = parts.group(1).strip()
                ingredient_amount = parts.group(2).strip()
                ingredients.append({
                    "name": ingredient_name,
                    "amount": ingredient_amount
                })
    
    teas.append({
        "name": name,
        "ingredients": ingredients,
        "function": function
    })

# 将结果转换为DataFrame
data = []
for tea in teas:
    for ingredient in tea['ingredients']:
        data.append({
            '茶名': tea['name'],
            '成分': ingredient['name'],
            '用量': ingredient['amount'],
            '功能': tea['function']
        })

df = pd.DataFrame(data)

# 生成HTML表格
html_table = df.to_html(index=False, classes='table table-striped')

# 保存到HTML文件
with open('teas_with_function.html', 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html>\n<html>\n<head>\n')
    f.write('<title>茶信息表</title>\n')
    f.write('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">\n')
    f.write('</head>\n<body>\n')
    f.write('<h1>茶信息表</h1>\n')
    f.write(html_table)
    f.write('\n</body>\n</html>')

print(html_table)