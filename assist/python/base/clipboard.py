import pyperclip

def to_clipboard(text):
    """将文本设置到剪切板"""
    pyperclip.copy(text)

def from_clipboard():
    """获取剪切板的文本信息"""
    return pyperclip.paste()


if __name__ == '__main__':
    # 设置剪切板文本
    # to_clipboard("这是测试文本")

    # 获取剪切板文本
    clipboard_text = from_clipboard()


    # 输出剪切板的文本信息
    print("剪切板的文本信息:", clipboard_text)