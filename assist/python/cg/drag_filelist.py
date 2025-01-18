import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox

class FileDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件拖放示例")
        self.root.geometry("600x400")

        # 创建一个 Frame 来接受文件拖放
        self.drop_frame = tk.Frame(self.root, width=600, height=400, bg="lightblue")
        self.drop_frame.pack(fill=tk.BOTH, expand=True)

        # 创建一个 Listbox 来显示文件路径，并启用多选
        self.listbox = tk.Listbox(self.drop_frame, font=("Arial", 12), selectmode=tk.MULTIPLE)
        self.listbox.pack(expand=True, fill=tk.BOTH)

        # 绑定文件拖放事件
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.drop)

        # 绑定 Ctrl+C 复制事件
        self.root.bind("<Control-c>", self.copy_to_clipboard)

    def drop(self, event):
        # 获取拖放的文件路径
        file_paths = self.get_file_paths(event.data)
        if file_paths:
            self.display_file_paths(file_paths)

    def get_file_paths(self, data):
        # 解析拖放的数据
        file_paths = data.split()
        # 将 Windows 路径中的 {} 去掉
        file_paths = [path.strip('{}') for path in file_paths]
        return file_paths

    def display_file_paths(self, file_paths):
        # 清空 Listbox
        self.listbox.delete(0, tk.END)
        # 显示文件路径
        for path in file_paths:
            self.listbox.insert(tk.END, path)

    def copy_to_clipboard(self, event):
        # 获取选中的项的索引
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("信息", "没有选中的文件路径")
            return

        # 获取选中的文件路径
        selected_paths = [self.listbox.get(index) for index in selected_indices]

        # 将选中的文件路径复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(selected_paths))
        self.root.update()  # 确保剪贴板更新

        messagebox.showinfo("信息", "文件路径已复制到剪贴板")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileDropApp(root)
    root.mainloop()