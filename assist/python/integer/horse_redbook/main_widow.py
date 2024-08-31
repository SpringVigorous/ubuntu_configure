import tkinter as tk
import red_search as rs

def create_scrollable_text(parent, row, column,tip:str):
    """创建带有滚动条的文本框"""
    parent.columnconfigure(0, weight=1)
    parent.columnconfigure(1, weight=0)
    parent.rowconfigure(0, weight=0)
    parent.rowconfigure(1, weight=1)
    label1 = tk.Label(parent, text=f"{tip}：", width=5)
    label1.grid(row=row, column=column, columnspan=2, sticky=tk.W, padx=10, pady=5)
    
    
    text_widget = tk.Text(parent)
    scrollbar = tk.Scrollbar(parent, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.grid(row=row+1, column=column,  sticky=tk.NSEW, padx=10, pady=5)
    scrollbar.grid(row=row+1, column=column + 1,  sticky=tk.NS)

def main():
    # 创建主窗口
    root = tk.Tk()
    root.title('小红书详情采集软件v1 | 马哥python说 |')
    root.minsize(width=850, height=500)

    # 设置列权重和最小宽度
    root.columnconfigure(0, minsize=10, weight=0)  # 第一列宽度较小
    root.columnconfigure(1, weight=1)  # 第二列可以根据窗口大小扩展

    # 输入控件部分：
    # a1填写
    label1 = tk.Label(root, text="a1:", width=5)
    entry_a1 = tk.Entry(root)
    label1.grid(row=0, column=0, sticky=tk.NS, padx=10, pady=5)
    entry_a1.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)

    # web_session填写
    label2 = tk.Label(root, text="web_session:", width=10)
    entry_web_session = tk.Entry(root)
    label2.grid(row=1, column=0, sticky=tk.NS, padx=10, pady=5)
    entry_web_session.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

    # 第三行：多行文本框
    link_container = tk.Frame(root)
    link_container.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=5)
    create_scrollable_text(link_container, 0, 0,"链接")

    # 第四行：多行文本框
    log_container = tk.Frame(root)
    log_container.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=5)
    create_scrollable_text(log_container, 0, 0,"日志")

    # 第五行：两个按钮
    button_container = tk.Frame(root)
    button_container.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)
    button_container.columnconfigure(0, weight=1)
    button_container.columnconfigure(1, weight=1)
    button_container.rowconfigure(0, weight=1)

    button1 = tk.Button(button_container, text="开始执行", command=lambda: print("按钮被点击了！"))
    button2 = tk.Button(button_container, text="退出程序", command=root.quit)
    button1.grid(row=0, column=0, sticky=tk.NS, padx=10, pady=5)
    button2.grid(row=0, column=1, sticky=tk.NS, padx=10, pady=5)

    # 设置行权重
    for i in range(5):
        if i < 2 or i>3:
            root.rowconfigure(i, minsize=20, weight=0)

        else:
            root.rowconfigure(i, weight=1)

    # 运行主循环
    root.mainloop()

if __name__ == '__main__':
    main()