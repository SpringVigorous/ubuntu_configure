import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(300, 200))

        panel = wx.Panel(self)
        button = wx.Button(panel, label="点击我", pos=(100, 50))

        # 绑定事件
        button.Bind(wx.EVT_BUTTON, self.on_button_click)

    def on_button_click(self, event):
        wx.MessageBox("你点击了按钮！", "提示")

app = wx.App()
frame = MyFrame(None, "wxPython 示例")
frame.Show()
app.MainLoop()