import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import vlc
import pandas as pd
from pathlib import Path

class MediaController:
    def __init__(self, root):
        self.root = root
        self.i = 1
        self.current_file = None
        self.player = None
        
        # 初始化界面
        self.create_widgets()
        self.setup_clipboard()    # 在MediaController类中添加/修改以下方法
    def setup_clipboard(self):
        # 启用多选模式
        self.tree.configure(selectmode='extended')
        
        # 绑定快捷键和事件
        self.tree.bind("<Control-c>", self.copy_selection)
        self.tree.bind("<Control-v>", self.paste_to_selection)
        self.tree.bind("<Double-1>", self.on_double_click)  # 双击编辑
        
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.current_file = file_path
            self.initialize_player()
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
        self.tree.item(item, values=(self.i, f"{time:.2f}", ""))
        
    def create_widgets(self):
        # 主分割窗口
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # 左侧面板
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        # 播放器区域
        self.player_frame = ttk.Frame(left_frame, height=400)
        self.player_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 控制按钮
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="打开文件", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="播放", command=self.play).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="暂停", command=self.pause).pack(side=tk.LEFT)

        # 右侧面板
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        # 顶部控制栏
        top_control = ttk.Frame(right_frame)
        top_control.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top_control, text="清空", command=self.clear_list).pack(side=tk.LEFT)
        ttk.Button(top_control, text="导入原始字幕", command=self.import_subtitle).pack(side=tk.LEFT)
        ttk.Button(top_control, text="生成字幕", command=self.generate_subtitle).pack(side=tk.LEFT)

        # 参数设置栏
        param_frame = ttk.Frame(right_frame)
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(param_frame, text="时间差:").pack(side=tk.LEFT)
        self.time_diff = ttk.Entry(param_frame, width=8, validate="key")
        self.time_diff.insert(0, "0.1")
        self.time_diff.pack(side=tk.LEFT)
        self.time_diff['validatecommand'] = (self.time_diff.register(self.validate_number), '%P')
        
        ttk.Label(param_frame, text="输出路径:").pack(side=tk.LEFT, padx=(10,0))
        self.output_path = ttk.Entry(param_frame, width=30)
        self.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(param_frame, text="浏览", command=self.select_output_path).pack(side=tk.LEFT)

        # 表格区域
        self.tree = ttk.Treeview(right_frame, columns=('序号', '时间点', '字幕'), show='headings')
        self.tree.heading('序号', text='序号')
        self.tree.heading('时间点', text='时间点(s)')
        self.tree.heading('字幕', text='字幕文本')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 新增功能方法
    def validate_number(self, input):
        """验证时间差输入"""
        try:
            if input == "" or float(input) >= 0:
                return True
            return False
        except:
            return False

    def select_output_path(self):
        """选择输出路径"""
        path = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[("SRT字幕文件", "*.srt"), ("所有文件", "*.*")]
        )
        if path:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, path)

    def clear_list(self):
        """清空表格内容"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.i = 1

    def import_subtitle(self):
        """从剪贴板导入字幕"""
        try:
            clipboard_data = self.root.clipboard_get()
            subtitles = [line.strip() for line in clipboard_data.split('\n') if line.strip()]
            
            # 清空现有字幕列
            for idx, item in enumerate(self.tree.get_children()):
                values = list(self.tree.item(item, 'values'))
                values[2] = subtitles[idx] if idx < len(subtitles) else ""
                self.tree.item(item, values=values)
                
            # 自动扩展行数
            while len(self.tree.get_children()) < len(subtitles):
                self.tree.insert('', 'end', values=(len(self.tree.get_children())+1, "", ""))
                
        except tk.TclError:
            messagebox.showerror("错误", "剪贴板中没有有效数据")

    def generate_subtitle(self):
        """生成字幕文件"""
        try:
            diff = float(self.time_diff.get())
            output_path = self.output_path.get()
            
            if not output_path:
                messagebox.showerror("错误", "请先选择输出路径")
                return
                
            entries = []
            prev_time = 0.0
            for idx, item in enumerate(self.tree.get_children()):
                values = self.tree.item(item, 'values')
                time_point = float(values[1]) if values[1] else 0.0
                text = values[2]
                
                start = 0.0 if idx == 0 else prev_time + diff
                end = time_point
                entries.append((start, end, text))
                prev_time = time_point
            
            # 生成SRT文件
            with open(output_path, "w", encoding="utf-8") as f:
                for idx, (start, end, text) in enumerate(entries):
                    start_time = f"{int(start//3600):02}:{int(start%3600//60):02}:{start%60:06.3f}".replace('.', ',')
                    end_time = f"{int(end//3600):02}:{int(end%3600//60):02}:{end%60:06.3f}".replace('.', ',')
                    f.write(f"{idx+1}\n{start_time} --> {end_time}\n{text}\n\n")
            
            # 生成CSV文件
            csv_path = output_path.replace(".srt", ".csv")
            df = pd.DataFrame(entries, columns=["start", "end", "text"])
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            
            messagebox.showinfo("成功", f"文件已生成：\n{output_path}\n{csv_path}")
            
        except ValueError:
            messagebox.showerror("错误", "无效的时间差数值")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败：{str(e)}")

    # 原有方法修改（新增视频首帧显示逻辑）
    def initialize_player(self):
        if self.player:
            self.player.stop()
            
        self.instance = vlc.Instance()
        self.media = self.instance.media_new(self.current_file)
        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)
        
        # Windows系统嵌入窗口
        if os.name == 'nt':
            self.player.set_hwnd(self.player_frame.winfo_id())
        else:
            self.player.set_xwindow(self.player_frame.winfo_id())
        
        # 暂停并显示首帧
        self.player.play()
        self.player.pause()
        
    # 保留原有 clipboard 和 treeview 相关方法...
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
    root.title("智能字幕生成工具")
    root.geometry("1200x800")
    app = MediaController(root)
    root.mainloop()