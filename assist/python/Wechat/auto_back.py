import pandas as pd
import numpy as np
import os
from uiautomation import WindowControl, MenuControl
# 绑定微信主窗口
wx = WindowControl(
Name='微信',
searchDepth=2
)
print(wx)
# 切换窗口
wx.SwitchToThisWindow()

#寻找会话控件绑定
hw = wx.ListControl(Name='会话')
print('寻找会话控件绑定',hw)

# 通过pd读取数据
cur_dir=os.path.dirname(os.path.abspath(__file__))
df = pd.read_excel( os.path.join(cur_dir,  '回复数据.xlsx'),sheet_name="关键词")
print(df)
# df = pd.read_csv('回复数据.csv',encoding='gb18030')
# 死循环接受消息
while True:
    #查找未读消息(4个)
    we = hw.TextControl(searchDepth=4)
    #print('查找未读消息'we)
    #死循环维持,没有超时报错
    while not we.Exists(0):
        pass
    print('查找未读消息',we)
    # 存在未读消息
    if we.Name :
        # 点击未读消息
        we.Click(simulateMove=False)
        # 读职最后一条消息
        msgs=[item.Name for item in wx.ListControl(Name='消息').GetChildren()]
        print(msgs)
        pass
    
    
        last_msg =msgs[-1]
        print('读取最后一条消息',last_msg)
        # 判断关键字
        msg = df.apply(lambda x: x['回复内容']if x['关键词'] in last_msg else None, axis=1)# 数据筛造,移除空数据
        msg.dropna(axis=0, how='any', inplace=True)# 做成列表
        ar = np.array(msg).tolist()
        #能够匹配到数据时
        if ar:
            # 将数据输入
            # 赫换换行符号

            wx.SendKeys(ar[0].replace('{br}',"{Shift}{Enter}"),waitTime=0)
            # 发送消息
            wx.SendKeys('{Enter}', waitTime=0)
            #通过消息匹配检索会话栏的联系人
            wx.TextControl(SubName=ar[0][:5]).RightClick()
        # 没有匹配到数据时
        else:
            pass
            wx.SendKeys("我没有理解你的意思",waitTime=0)
            wx.SendKeys("{Enter}", waitTime=0)
            wx.TextControl(SubName=last_msg[:5]).RightClick()
        # 匹配右击控件
        # ment = MenuControl(ClassName='CMenuWnd")
        # # 点击石谜控件中的不显示聊天
        #ment.TextControl(Name='不显示职天').Click()