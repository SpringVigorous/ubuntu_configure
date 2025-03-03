import os
import tkinter as tk
from tkinter import ttk, filedialog
import vlc
import pandas as pd
import time

class MediaController:
    def __init__(self, root):
        self.root = root
        self.i = 1  # 记录行计数器
        self.current_file = None
        self.player = None
        
        # 初始化界面
        self.create_widgets()
        self.setup_clipboard()

    def create_widgets(self):
        # 播放器区域
        self.player_frame = ttk.Frame(self.root)
        self.player_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 控制按钮区域
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="打开文件", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="播放", command=self.play).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="暂停", command=self.pause).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="导出Excel", command=self.export_excel).pack(side=tk.LEFT)

        # 表格区域
        self.tree = ttk.Treeview(self.root, columns=('序号', '时间点', '文本'), show='headings')
        self.tree.heading('序号', text='序号')
        self.tree.heading('时间点', text='时间点(s)')
        self.tree.heading('文本', text='字幕文本')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.current_file = file_path
            self.initialize_player()



            
    def initialize_player(self):
        if self.player:
            self.player.stop()
            
        # 创建VLC实例
        self.instance = vlc.Instance()
        self.media = self.instance.media_new(self.current_file)
        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)
        
        # 将播放器嵌入到窗口
        if os.name == 'nt':  # Windows系统
            self.player.set_hwnd(self.player_frame.winfo_id())
        else:  # Linux系统
            self.player.set_xwindow(self.player_frame.winfo_id())

    def play(self):
        if self.player:
            self.player.play()

    def pause(self):
        if self.player:
            # 获取当前播放时间
            current_time = round(self.player.get_time() / 1000, 2)
            
            # 更新表格
            self.update_table(current_time)
            self.i += 1

            # 暂停播放
            self.player.pause()

    def update_table(self, time):
        # 自动扩展表格行
        if self.i > len(self.tree.get_children()):
            self.tree.insert('', 'end', values=(self.i, "", ""))
            
        # 定位并更新时间
        item = self.tree.get_children()[self.i-1]
        txt=item.values[2] if item.values and len(item.values)>2 else ""
        self.tree.item(item, values=(self.i, f"{time:.2f}", txt))


    def export_excel(self):
        data = []
        for item in self.tree.get_children():
            data.append(self.tree.item(item)['values'])
        
        df = pd.DataFrame(data, columns=['序号', '时间点', '文本'])
        df.to_excel("subtitle_records.xlsx", index=False)

    # 在MediaController类中添加/修改以下方法
    def setup_clipboard(self):
        # 启用多选模式
        self.tree.configure(selectmode='extended')
        
        # 绑定快捷键和事件
        self.tree.bind("<Control-c>", self.copy_selection)
        self.tree.bind("<Control-v>", self.paste_to_selection)
        self.tree.bind("<Double-1>", self.on_double_click)  # 双击编辑

    def copy_selection(self, event):
        # 获取选中项的所有数据
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # 构建剪贴板数据（制表符分隔列，换行符分隔行）
        clipboard_data = []
        for item in selected_items:
            values = self.tree.item(item, 'values')
            clipboard_data.append('\t'.join(map(str, values)))
        
        # 设置剪贴板内容
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(clipboard_data))

    def paste_to_selection(self, event):
        try:
            # 获取剪贴板内容并解析
            clipboard_data = self.root.clipboard_get()
            rows = [row.split('\t') for row in clipboard_data.split('\n') if row.strip()]
            
            # 获取当前选中项（锚点项）
            anchor_item = self.tree.identify_row(event.y) if event else self.tree.selection()[0]
            
            # 获取起始位置
            start_idx = self.tree.index(anchor_item) if anchor_item else 0
            
            # 处理多行粘贴
            for row_idx, row_data in enumerate(rows):
                target_idx = start_idx + row_idx
                
                # 自动扩展表格
                if target_idx >= len(self.tree.get_children()):
                    self.tree.insert('', 'end', values=(len(self.tree.get_children())+1, "", ""))
                
                # 获取目标项ID
                target_item = self.tree.get_children()[target_idx]
                
                # 更新数据（保留原序号）
                original_values = list(self.tree.item(target_item, 'values'))
                for col_idx, value in enumerate(row_data):
                    if col_idx < len(original_values):
                        original_values[col_idx] = value.strip()
                self.tree.item(target_item, values=tuple(original_values))
            
            # 自动滚动到最后一个粘贴项
            last_item = self.tree.get_children()[start_idx + len(rows) - 1]
            self.tree.see(last_item)
            
        except tk.TclError:
            pass

    def on_double_click(self, event):
        # 获取点击位置
        region = self.tree.identify_region(event.x, event.y)
        if region not in ('cell', 'tree'):
            return
        
        # 获取单元格坐标
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        
        # 排除序号列编辑
        if column == '#0' or column == '#1':
            return
        
        # 获取单元格原始值
        col_idx = int(column[1:]) - 1
        values = list(self.tree.item(item, 'values'))
        
        # 创建编辑框
        x, y, width, height = self.tree.bbox(item, column)
        self.entry = ttk.Entry(self.tree, width=width//8)
        self.entry.place(x=x, y=y, width=width, height=height)
        
        # 设置初始值并全选
        self.entry.insert(0, values[col_idx])
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        # 绑定完成事件
        self.entry.bind("<FocusOut>", lambda e: self.finish_edit(item, col_idx))
        self.entry.bind("<Return>", lambda e: self.finish_edit(item, col_idx))

    def finish_edit(self, item, col_idx):
        # 获取新值并更新
        new_value = self.entry.get()
        values = list(self.tree.item(item, 'values'))
        values[col_idx] = new_value
        self.tree.item(item, values=values)
        
        # 清除编辑框
        self.entry.destroy()
if __name__ == "__main__":
    root = tk.Tk()
    root.title("媒体播放控制器")
    root.geometry("800x600")
    app = MediaController(root)
    root.mainloop()