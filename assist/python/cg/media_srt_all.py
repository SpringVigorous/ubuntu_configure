import os
import json
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
        self.playing = False
        self.config_file = "config.json"
        self.history_limit = 20
        self.progress_update_interval = 100  # 进度更新间隔(毫秒)
        self.create_widgets()
        self.setup_clipboard()
        self.load_config()
        
        # 初始化VLC事件管理器
        self.event_manager = None
        self.setup_vlc_events()
        
        self.progress.bind("<Button-1>", self.start_seek)  # 开始拖动
        self.progress.bind("<ButtonRelease-1>", self.end_seek)  # 结束拖动
        # 添加时间显示样式（在__init__中）
        style = ttk.Style()
        style.configure("Time.TLabel", font=("Consolas", 9), foreground="#666666")


        
    def create_progress_bar(self):
        """创建带精确时间显示的进度条"""
        # 进度条容器
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=5, pady=2)

        # 当前时间标签（左）
        self.lbl_current = ttk.Label(
            progress_frame, 
            text="0.000s",
            width=8,
            anchor="e",
            font=("TkFixedFont", 9)
        )
        self.lbl_current.pack(side=tk.LEFT)

        # 进度条主体
        self.progress = ttk.Scale(
            progress_frame,
            from_=0,
            to=0,
            orient=tk.HORIZONTAL,
            command=lambda _: self.update_current_display()
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress.bind("<ButtonRelease-1>", self.seek_media)

        # 总时长标签（右）
        self.lbl_duration = ttk.Label(
            progress_frame,
            text="0.000s",
            width=8,
            anchor="w",
            font=("TkFixedFont", 9)
        )
        self.lbl_duration.pack(side=tk.RIGHT)
    def toggle_play_pause(self):
        """切换播放时禁用按钮直到初始化完成"""
        # if self.initializing:
        #     return
        """切换播放/暂停状态"""
        if not self.player:
            return
            
        if self.playing:
            # 执行暂停操作
            self.pause_media()
        else:
            # 执行播放操作
            self.play_media()

    def play_media(self):
        """开始播放"""
        self.playing = True
        self.player.play()
        self.play_pause_btn.config(text="暂停")
        self.start_progress_update()

    def pause_media(self):
        """暂停播放"""
        self.playing = False

        self.record()
        
        
        self.player.pause()
        self.player.set_time(int(self.progress.get() * 1000))  # 同步播放器位置
        self.play_pause_btn.config(text="播放")

    def on_media_end(self, event):
        """媒体结束处理"""
        self.playing = False
        # 重置播放位置到起始点
        self.player.set_time(0)  # 设置媒体时间为0毫秒
        self.player.pause()      # 暂停播放器
        
        # 更新UI状态
        self.progress.configure(value=0)
        self.play_pause_btn.config(text="播放")
        self.lbl_current.config(text="0.000s")  # 更新当前时间显示
        
        # 强制刷新视频帧显示首帧（需要Windows API支持）
        if os.name == 'nt':
            try:
                import win32api
                win32api.InvalidateRect(self.player_frame.winfo_id(), None, True)
            except ImportError:
                pass
                
        self.record_final_time()
        self.root.after(0, lambda: messagebox.showinfo("提示", "播放已完成"))
    def start_seek(self, event):
        """开始拖动时暂停自动更新"""
        self.progress_auto_update = False

    def end_seek(self, event):
        """结束拖动时恢复更新"""
        self.progress_auto_update = True
        self.seek_media(event)  # 执行跳转



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
        
    def get_cell(self, event):
        table = self.tree
        col_id = table.identify_column(event.x)
        row_id = table.identify_row(event.y)
        try:
            return int(row_id[1:]), table.index(row_id) + 1
        except ValueError as e:
            print(f"转换 row_id 失败：row_id='{row_id}', col_id='{col_id}'")
            raise  # 根据场景选择是否重新抛出异常或返回默认值

    # 修改on_double_click方法中的列判断逻辑
    def on_double_click(self, event):
        # 获取点击位置
        region = self.tree.identify_region(event.x, event.y)
        if region not in ('cell', 'tree'):
            return
        
        # 获取单元格坐标
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        
        # 排除序号列编辑（第一列）
        if column == '#1':
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
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.current_file = file_path
            self.initialize_player()
    def finish_edit(self, item, col_idx):
        # 获取新值并更新
        new_value = self.entry.get()
        values = list(self.tree.item(item, 'values'))
        values[col_idx] = new_value
        self.tree.item(item, values=values)
        
        # 清除编辑框
        self.entry.destroy()


    def start_progress_update(self):
        """启动进度条更新循环"""
        if self.playing:
            self.update_progress()

    # 在MediaController类中添加验证方法
    def validate_number(self, new_value):
        """验证时间差输入是否为有效数字"""
        try:
            if new_value == "":
                return True  # 允许空输入以便删除内容
            return float(new_value) >= 0
        except ValueError:
            return False
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
        
        # 进度条
        # self.progress = ttk.Scale(left_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        # self.progress.pack(fill=tk.X, padx=5, pady=2)
        # self.progress.bind("<ButtonRelease-1>", self.seek_media)
        self.create_progress_bar()
        
        # 控制按钮
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="打开文件", command=self.open_file).pack(side=tk.LEFT)
        # 修改控制按钮部分
        self.play_pause_btn = ttk.Button(control_frame, text="播放", command=self.toggle_play_pause)
        self.play_pause_btn.pack(side=tk.LEFT)
                
        # 在控制面板添加按钮
        self.btn_rewind = ttk.Button(control_frame, text="<< 0.1s", command=self.rewind)
        self.btn_rewind.pack(side=tk.LEFT, padx=5)  # 放在现有按钮左侧

        self.btn_forward = ttk.Button(control_frame, text="0.1s >>", command=self.forward)
        self.btn_forward.pack(side=tk.LEFT, padx=5)  # 放在现有按钮右侧
        
        self.btn_forward = ttk.Button(control_frame, text="记录", command=self.record)
        self.btn_forward.pack(side=tk.LEFT, padx=5)  # 放在现有按钮右侧

        # 右侧面板
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        # 顶部控制栏
        top_control = ttk.Frame(right_frame)
        top_control.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top_control, text="清空", command=self.clear_list).pack(side=tk.LEFT)
        ttk.Button(top_control, text="导入字幕", command=self.import_subtitle).pack(side=tk.LEFT)
        ttk.Button(top_control, text="生成字幕", command=self.generate_subtitle).pack(side=tk.LEFT)
        ttk.Button(top_control, text="保存", command=self.save_config).pack(side=tk.LEFT)

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
    def update_playback(self, time_delta):
        # 获取当前播放时间
        current_time = self.player.get_time()/1000  # 假设有获取时间的接口
        
        # 计算新时间（需处理边界）
        new_time = max(0, current_time + time_delta)
        new_time = min(new_time, self.player.get_length())  # self.media_length为总时长
        
        # 更新播放器
        self.player.set_time(int(new_time*1000))  # 假设有设置时间的接口
        
        # 更新进度条
        self.update_progress()
        
    def rewind(self):
        self.update_playback(-0.1)  # 后退0.1秒

    def forward(self):
        self.update_playback(0.1)   # 前进0.1秒
        
    def record(self):
        current_time = round(self.player.get_time() / 1000, 2)
        self.update_table(current_time)
        self.i += 1
        pass
    def update_progress(self):
        """更新进度显示时跳过初始化阶段"""
        # if self.initializing:
        #     return
        """更新进度显示"""
        if self.player:
            try:
                current_time = self.player.get_time() / 1000  # 转换为秒
                total_time = self.player.get_length() / 1000
                
                # 更新进度条值
                self.progress.configure(value=current_time)
                
                # 更新当前时间显示
                self.lbl_current.config(text=f"{current_time:.3f}s")
                
                # 自动更新总时长（处理直播流等情况）
                if total_time > 0 and self.progress['to'] != total_time:
                    self.progress.configure(to=total_time)
                    self.lbl_duration.config(text=f"{total_time:.3f}s")

            except Exception as e:
                print(f"更新进度时出错: {str(e)}")
            finally:
                pass
                # 保持循环更新
                # self.root.after(self.progress_update_interval, self.start_progress_update)
                # # self.root.after(self.progress_update_interval, self.start_progress_update)
    def update_current_display(self):
        """拖动进度条时更新临时显示"""
        if not self.playing:
            current_sec = self.progress.get()
            self.lbl_current.config(text=f"{current_sec:.3f}s")



    def seek_media(self, event):
        """处理进度跳转"""
        if self.player:
            try:
                target_sec = self.progress.get()
                # 增加边界检查
                val=self.progress['to']
                target_sec = max(0, min(target_sec, self.progress['to']))
                self.player.set_time(int(target_sec * 1000))
                # 强制刷新显示帧
                self.player.pause()
                self.player.play()
                if not self.playing:
                    self.player.pause()
                # 如果处于暂停状态更新表格
                if not self.playing and self.tree.get_children():
                    self.update_table(round(target_sec, 3))
                
            except Exception as e:

                print(f"跳转失败: {str(e)}")

            finally:
                pass
    # 增强VLC事件处理
    def setup_vlc_events(self):
        if self.player:
            self.event_manager = self.player.event_manager()
            self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_media_end)



    def record_final_time(self):
        if self.player:
            duration = self.player.get_length() / 1000
            self.update_table(round(duration, 2))
            self.i += 1

    # 配置文件管理
    def save_config(self):
        
        vals=[self.tree.item(item)['values'] for item in self.tree.get_children()]
        
        config = {
            "media_path": self.current_file,
            "time_diff": self.time_diff.get(),
            "output_path": self.output_path.get(),
            "subtitle_data": [item for item in vals if item and len(item)>2 and item[2]]
        }
        
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")]
        )
        if path:
            try:
                # 更新配置文件历史
                history = self.load_history()
                history.insert(0, path)
                if len(history) > self.history_limit:
                    history.pop()
                with open(self.config_file, 'w') as f:
                    json.dump(history, f)
                
                # 保存当前配置
                with open(path, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("成功", "配置保存成功")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

    def load_config(self):
        history = self.load_history()
        for path in history:
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        config = json.load(f)
                    self.current_file = config["media_path"]
                    self.time_diff.delete(0, tk.END)
                    self.time_diff.insert(0, config["time_diff"])
                    self.output_path.delete(0, tk.END)
                    self.output_path.insert(0, config["output_path"])
                    self.clear_list()
                    for values in config["subtitle_data"]:
                        self.tree.insert('', 'end', values=values)
                    self.i = len(config["subtitle_data"]) + 1
                    self.initialize_player()
                    break
                except:
                    continue

    def load_history(self):
        try:
            with open(self.config_file) as f:
                return json.load(f)
        except:
            return []

    # 其他功能方法保持原有逻辑...
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
                if not text:
                    continue
                start = 0.0 if idx == 0 else prev_time + diff
                end = time_point
                entries.append((start, end, text))
                prev_time = time_point
            
            # 生成SRT文件
            with open(output_path, "w", encoding="utf-8-sig") as f:
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
        

        # 新增加的状态跟踪变量
        self.initializing = True  # 标记正在初始化首帧
        self.retry_count = 0      # 重试计数器
        
        # 启动首帧获取流程
        self.player.play()
        self.check_first_frame()

        # 获取视频总时长并更新显示
        self.root.after(100, self.update_duration)  # 延迟确保获取到时
        
    def check_first_frame(self):
        """循环检测首帧是否就绪"""
        if self.retry_count > 10:  # 最多重试10次（约500ms）
            self.player.stop()
            return
        
        if self.player.is_playing():
            # 成功开始播放后立即暂停
            self.player.pause()
            self.initializing = False
            
            # 强制刷新显示（Windows需要）
            if os.name == 'nt':
                try:
                    import win32gui
                    win32gui.InvalidateRect(self.player_frame.winfo_id(), None, True)
                except ImportError:
                    pass
            # 更新进度显示
            self.update_duration()
        else:
            # 继续检测
            self.retry_count += 1
            self.root.after(50, self.check_first_frame)  # 每50ms检测一次
            
    def update_duration(self):
        """更新视频总时长显示"""
        if self.player:
            duration = self.player.get_length()
            if duration > 0:
                total_sec = duration / 1000
                self.progress.configure(to=total_sec)
                self.lbl_duration.config(text=f"{total_sec:.3f}s")
            else:
                self.root.after(100, self.update_duration)
    def select_output_path(self):
        """选择输出路径"""
        path = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[("SRT字幕文件", "*.srt"), ("所有文件", "*.*")]
        )
        if path:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, path)
    def update_table(self, time):
        # 自动扩展表格行
        if self.i > len(self.tree.get_children()):
            self.tree.insert('', 'end', values=(self.i, "", ""))
                
        # 修改后的正确代码段
        # 定位并更新时间
        item = self.tree.get_children()[self.i-1]
        # 正确获取现有值的方式
        existing_values = self.tree.item(item, 'values')
        # 安全获取字幕内容（第三列）
        txt = existing_values[2] if len(existing_values) > 2 else ""
        # 更新时间点并保留三位小数
        self.tree.item(item, values=(self.i, f"{time:.3f}", txt))
    # 在MediaController类中添加/修改以下方法
    def on_click(self, event):
        """记录当前点击的列位置"""
        region = self.tree.identify_region(event.x, event.y)
        if region == 'cell':
            self.current_col = self.tree.identify_column(event.x)
            _,self.i=self.get_cell(event)
        else:
            self.current_col = None

    def delete_selection(self, event):
        """处理删除键操作"""
        selected_items = self.tree.selection()
        if not selected_items or not hasattr(self, 'current_col') or not self.current_col:
            return
        
        # 禁止删除序号列（第一列）
        if self.current_col == '#1':
            return
        
        col_idx = int(self.current_col[1:]) - 1  # 转换为0-based索引
        
        for item in selected_items:
            values = list(self.tree.item(item, 'values'))
            if col_idx < len(values):
                new_values = list(values)
                new_values[col_idx] = ""
                self.tree.item(item, values=tuple(new_values))

    # 修改setup_clipboard方法
    def setup_clipboard(self):
        # 启用多选模式
        self.tree.configure(selectmode='extended')
        
        # 绑定快捷键和事件
        self.tree.bind("<Control-c>", self.copy_selection)
        self.tree.bind("<Control-v>", self.paste_to_selection)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Delete>", self.delete_selection)
        self.tree.bind("<ButtonPress-1>", self.on_click)  # 新增点击事件绑定


if __name__ == "__main__":
    root = tk.Tk()
    root.title("智能媒体控制器")
    root.geometry("1200x800")
    app = MediaController(root)
    root.mainloop()

    
    

