from abc import ABC, abstractmethod
from typing import Callable

def wrapper_lamda(func,*args,**kwargs):
    return lambda: func(*args, **kwargs)


class RAIITool():
    """RAII风格的抽象基类（虚基类），定义资源管理的接口规范"""
    
    def __init__(self, acquire_func:Callable,release_func:Callable):
        self.resource=acquire_func()
        self._release_func = release_func
    def __enter__(self):
        """上下文管理器进入方法，返回资源对象"""
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出方法，确保资源释放"""
        self._release_func()
        return False  # 不抑制异常


class RAIIBase(ABC):
    """RAII风格的抽象基类（虚基类），定义资源管理的接口规范"""
    
    def __init__(self, resource_name):
        """初始化资源管理器，触发资源获取"""
        self.resource_name = resource_name
        self.resource = None
        # 调用抽象方法获取资源（由子类实现具体逻辑）
        self.resource = self._acquire_resource()
    
    @abstractmethod
    def _acquire_resource(self):
        """抽象方法：获取资源（必须由子类实现）"""
        pass  # 子类必须实现具体的资源获取逻辑
    
    @abstractmethod
    def _release_resource(self):
        """抽象方法：释放资源（必须由子类实现）"""
        pass  # 子类必须实现具体的资源释放逻辑
    
    def __enter__(self):
        """上下文管理器进入方法，返回资源对象"""
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出方法，确保资源释放"""
        self._release_resource()
        return False  # 不抑制异常


# 示例：派生类实现（文件资源管理）
class FileResource(RAIIBase):
    def _acquire_resource(self):
        """具体实现：打开文件"""
        print(f"打开文件: {self.resource_name}")
        return open(self.resource_name, 'w')  # 实际打开文件
    
    def _release_resource(self):
        """具体实现：关闭文件"""
        if self.resource:
            print(f"关闭文件: {self.resource_name}")
            self.resource.close()  # 确保文件关闭


# 示例：派生类实现（数据库连接管理）
class DBConnection(RAIIBase):
    def _acquire_resource(self):
        """具体实现：建立数据库连接"""
        print(f"连接数据库: {self.resource_name}")
        # 模拟数据库连接
        return f"DBConnection({self.resource_name})"
    
    def _release_resource(self):
        """具体实现：断开数据库连接"""
        print(f"断开数据库连接: {self.resource_name}")


# 使用示例
if __name__ == "__main__":
    print("1")
    
    # 使用文件资源
    with FileResource("example.txt") as file:
        print(f"正在读取文件: {file.name}")
    print("2")
    # 使用数据库连接
    with DBConnection("mysql://localhost:3306/mydb") as db:
        print(f"正在使用数据库连接: {db}")
    print("3")

    
    with RAIITool(lambda :print("acquire_func"),lambda :print("release_func")) as f:
        print("正在使用文件:")
    print("4")
    
    
    def print_func(a,c,b=2):
        print(a)
        print(b)
        print(c)
    func=wrapper_lamda(print_func,1,3,b=10)
    func()