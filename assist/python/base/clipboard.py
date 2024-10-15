import pyperclip

def set_clipboard_text(text):
    """将文本设置到剪切板"""
    pyperclip.copy(text)

def get_clipboard_text():
    """获取剪切板的文本信息"""
    return pyperclip.paste()


if __name__ == '__main__':
    # 设置剪切板文本
    # set_clipboard_text("这是测试文本")

    # 获取剪切板文本
    clipboard_text = get_clipboard_text()


    # 输出剪切板的文本信息
    print("剪切板的文本信息:", clipboard_text)