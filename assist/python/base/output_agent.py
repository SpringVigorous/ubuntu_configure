import sys
import io


class OutputAgent:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OutputAgent, cls).__new__(cls)
            cls._instance.install()
        return cls._instance

    def __init__(self):
        # 初始化方法只在第一次创建实例时调用
        if not hasattr(self, 'out_stream'):
            self.out_stream = io.StringIO()
            self.err_stream = io.StringIO()
            self.stdout, sys.stdout = sys.stdout, self.out_stream
            self.stderr, sys.stderr = sys.stderr, self.err_stream

    def __del__(self):
        self.uninstall()

    def install(self):
        self.out_stream = io.StringIO()
        self.err_stream = io.StringIO()
        self.stdout, sys.stdout = sys.stdout, self.out_stream
        self.stderr, sys.stderr = sys.stderr, self.err_stream

    def uninstall(self):
        if not self.stdout:
            return

        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.out_stream.close()
        self.err_stream.close()

        self.stdout = None
        self.stderr = None

    def clear(self):
        # 清空内容
        self.out_stream.seek(0)  # 将指针移动到文件开头
        self.out_stream.truncate(0)  # 删除后续的所有内容

        self.err_stream.seek(0)  # 将指针移动到文件开头
        self.err_stream.truncate(0)  # 删除后续的所有内容

    @property
    def out_value(self):
        return self.out_stream.getvalue().strip()

    @property
    def has_out(self):
        return bool(self.out_value)

    @property
    def err_value(self):
        return self.err_stream.getvalue().strip()

    @property
    def has_err(self):
        return bool(self.err_stream)
    

if __name__=="__main__":
    
    handler=OutputAgent()

    # 打印或处理输出内容
    print("输出内容:")
    print("1:2")
    print("5fasdf")
    data1=handler.out_value
    handler.clear()
    print("输出内容:6")
    data2=handler.out_value
    
    handler.uninstall()
    print(data1)
    print(data2)

    # 关闭字符流
