import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频播放控制器")
        
        # 初始化变量
        self.video_path = ""
        self.is_playing = False
        self.current_time = 0.0
        self.record_times = []
        
        # 创建主界面布局
        self.create_widgets()
        
        # 视频相关参数
        self.cap = None
        self.video_length = 0
        self.delay = 15  # 刷新间隔（毫秒）
        
        def toggle_fullscreen(event=None):
            state = self.root.attributes("-fullscreen")
            self.root.attributes("-fullscreen", not state)
            return "break"
        
            # 绑定 F11 键以切换全屏模式
        root.bind("<F11>", toggle_fullscreen)
        # 绑定 ESC 键以退出全屏模式
        root.bind("<Escape>", toggle_fullscreen)

    def create_widgets(self):
        # 主窗口左右分割（左侧占比80%）
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板（权重3:1）
        left_pane = ttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(left_pane, weight=3)  # 左侧占75%宽度
        
        # 右侧面板（权重1）
        right_pane = ttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane, weight=1)  # 右侧占25%宽度

        # 左侧上部（视频播放器占80%高度）
        self.create_video_panel(left_pane)
        left_pane.add(self.video_frame, weight=4)  # 上部占80%高度
        
        # 左侧下部（控制面板占20%高度）
        self.create_control_panel(left_pane)
        left_pane.add(self.control_frame, weight=1)
        
        
                # 右侧上部（记录控制）
        self.create_record_control(right_pane)
        
        # 右侧下部（记录列表）
        self.create_record_list(right_pane)
        

    def create_video_panel(self, parent):
        # 视频显示区域
        self.video_frame = ttk.Frame(parent)
        
        # 使用Grid布局实现弹性伸缩
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        
        # 视频画布（弹性填充）
        self.canvas = tk.Canvas(self.video_frame, bg='black')
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # 进度条（固定高度）
        self.progress = ttk.Scale(self.video_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.progress.grid(row=1, column=0, sticky='ew', padx=5, pady=2)
        
        # 控制按钮（固定高度）
        control_buttons = ttk.Frame(self.video_frame)
        control_buttons.grid(row=2, column=0, sticky='ew', pady=5)
        
        # 按钮布局
        buttons = [
            ('⏮', self.goto_start),
            ('⏪', lambda: self.jump(-0.1)),
            ('⏯', self.toggle_play),
            ('⏩', lambda: self.jump(0.1)),
            ('⏭', self.goto_end)
        ]
        
        for text, cmd in buttons:
            btn = ttk.Button(control_buttons, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=2)

    def create_control_panel(self, parent):
        # 底部控制面板（固定高度）
        self.control_frame = ttk.Frame(parent)
        
        # 使用Grid布局
        self.control_frame.grid_columnconfigure(0, weight=1)
        
        # 打开文件按钮
        open_btn = ttk.Button(self.control_frame, text="打开文件", command=self.open_file)
        open_btn.grid(row=0, column=0, padx=5, sticky='w')
        
        # 步长设置
        ttk.Label(self.control_frame, text="快进步长(s):").grid(row=0, column=1, padx=5)
        self.step_entry = ttk.Entry(self.control_frame, width=6)
        self.step_entry.insert(0, "0.1")
        self.step_entry.grid(row=0, column=2, padx=5)
        
        # 记录按钮
        record_btn = ttk.Button(self.control_frame, text="记录", command=self.record_time)
        record_btn.grid(row=0, column=3, padx=5, sticky='e')

    def create_record_control(self, parent):
        # 记录控制面板（固定高度）
        control_frame = ttk.Frame(parent)
        parent.add(control_frame, weight=1)  # 顶部占20%高度
        
        # 清空按钮
        clear_btn = ttk.Button(control_frame, text="清空", command=self.clear_records)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 时间差设置
        ttk.Label(control_frame, text="时间差(s):").pack(side=tk.LEFT, padx=5)
        self.diff_entry = ttk.Entry(control_frame, width=6)
        self.diff_entry.insert(0, "0.1")
        self.diff_entry.pack(side=tk.LEFT, padx=5)

    def create_record_list(self, parent):
        # 记录列表（占80%高度）
        list_frame = ttk.Frame(parent)
        parent.add(list_frame, weight=4)
        
        # 使用Grid布局
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 树状列表
        columns = ("序号", "时间点(s)")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        # 滚动条
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)
        
        # 列配置
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor='center')
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.video_path = file_path
            self.init_video()
            self.play_video()

    def play_video(self):
        if self.cap and not self.is_playing:
            self.is_playing = True
            self.update_video()


    def update_video(self):
        if self.is_playing and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret:
                    self.current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    self.progress.set(self.current_time)
                    
                    # 转换颜色空间并创建图像对象
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    self.img = ImageTk.PhotoImage(image=img)
                    
                    # 更新画布显示
                    self.canvas.delete("video")
                    self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW, tags="video")
                    
                    # 计算下一帧的刷新时间
                    fps = self.cap.get(cv2.CAP_PROP_FPS)
                    delay = int(1000 / fps) if fps > 0 else 30
                    self.root.after(delay, self.update_video)
                else:
                    self.is_playing = False
            except Exception as e:
                print("视频播放错误:", e)
                self.is_playing = False

    def init_video(self):
        if self.cap: 
            self.cap.release()
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print("错误: 无法打开视频文件")
            return
        # 计算视频总时长（秒）
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_length = frame_count / fps if fps > 0 else 0
        self.progress.config(to=self.video_length)

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing: 
            self.play_video()

    def seek_video(self, event):
        if self.cap:
            target_time = self.progress.get()
            self.cap.set(cv2.CAP_PROP_POS_MSEC, target_time * 1000)
            self.current_time = target_time

    def jump(self, step):
        try:
            step = float(self.step_entry.get())
            self.current_time += step
            self.cap.set(cv2.CAP_PROP_POS_MSEC, self.current_time * 1000)
        except:
            pass

    def goto_start(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, 0)
            self.current_time = 0

    def goto_end(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, self.video_length)
            self.current_time = self.video_length

    def record_time(self):
        time_str = f"{self.current_time:.3f}"
        self.record_times.append(time_str)
        self.tree.insert("", tk.END, values=(len(self.record_times), time_str))
        self.tree.selection_set(self.tree.get_children()[-1])

    def clear_records(self):
        self.record_times.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    

        
    app = VideoPlayerApp(root)
    root.mainloop()