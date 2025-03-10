from py3dbp import Packer, Bin, Item
# 参数：容器名称、尺寸（长宽高元组）、最大承重
my_bin = Bin("快递箱", *(200, 180, 150), 1000.0)
item = Item("电视机", *(120, 80, 60), 25.0)


packer = Packer()
packer.add_bin(my_bin)  # 添加容器
packer.add_item(item)   # 添加物品

# 添加多个容器和物品
packer.add_bin(Bin("卡车A", *(400, 250, 300), 5000))
packer.add_bin(Bin("卡车B", *(600, 300, 450), 8000))
items = [
    Item("冰箱", *(180, 80, 70), 50),
    Item("冰箱1", *(180, 80, 70), 50),
    Item("冰箱2", *(180, 80, 70), 50),
    Item("冰箱3", *(180, 80, 70), 50),
    Item("冰箱4", *(180, 80, 70), 50),
    Item("洗衣机", *(90, 60, 60), 30)
]
for item in items:
    packer.add_item(item)



packer.pack()
for bin in packer.bins:
    print(f"\n容器 {bin.name} 利用率：")
    for item in bin.items:
        print(f"物品 {item.name} 坐标：{item.position}")
    for item in bin.unfitted_items:
        print(f"未装入物品：{item.name}")