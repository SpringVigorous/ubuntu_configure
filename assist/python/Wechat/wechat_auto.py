import pandas as pd
from pywinauto import Application, Desktop
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time

# 读取 Excel 文件
def read_excel(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)

# 获取最新的未读消息
def get_latest_unread_message(app):
    dlg = app.window(title_re="微信")
    # dlg.wait('visible')
    
    # 查看未读消息
    unread_msg_button = dlg.child_window(title="查看", control_type="Button")
    if unread_msg_button.exists():
        unread_msg_button.click()
    
    # 获取最新消息
    messages = dlg.child_window(auto_id="MessageListRoot", control_type="List")
    latest_message_item = messages.children(control_type="ListItem")[-1]
    
    # 获取最新消息的文本内容
    text_control = latest_message_item.TextControl()
    message_text = text_control.window_text()
    return message_text

# 模糊匹配关键词并返回回复
def match_keyword_and_reply(message, df):
    best_match, score = process.extractOne(message, df['关键词'].tolist())
    if score > 80:  # 设置匹配阈值
        reply = df[df['关键词'] == best_match]['回复数据'].values[0]
        return reply
    else:
        return "没有理解你的意思"

# 发送回复
def send_reply(app, reply):
    dlg = app.window(title_re="微信")
    dlg.wait('visible')
    
    # 获取输入框
    input_box = dlg.child_window(auto_id="Edit", control_type="Edit")
    input_box.set_text(reply)
    
    # 发送消息
    send_button = dlg.child_window(title="发送", control_type="Button")
    send_button.click()

import os
# 主函数
def main():
    cur_dir=os.path.dirname(os.path.abspath(__file__))
    
    # 读取 Excel 文件
    file_path =  os.path.join(cur_dir,  '回复数据.xlsx')
    sheet_name = "关键词"
    df = read_excel(file_path, sheet_name)
    
    # 启动微信
    app = Application(backend="uia").start(r"D:\微信\WeChat\WeChat.exe")
    time.sleep(5)  # 等待微信启动
    
    # 获取最新的未读消息
    message = get_latest_unread_message(app)
    print(f"最新消息: {message}")
    
    # 模糊匹配关键词并返回回复
    reply = match_keyword_and_reply(message, df)
    print(f"回复: {reply}")
    
    # 发送回复
    send_reply(app, reply)

if __name__ == "__main__":
    main()