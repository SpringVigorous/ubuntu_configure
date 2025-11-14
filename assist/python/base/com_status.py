from enum import IntFlag, auto
from typing import Union
from base.com_log import logger_helper


__task_status_logger__=logger_helper("任务状态","检查")

class TaskStatus(IntFlag):
    """任务状态枚举类，使用位表示不同状态"""
    
    # 前两位：下载状态（互斥）
    UNDOWNLOADED = 0b00000    # 0: 未下载
    INCOMPLETED = 0b00001     # 1: 已下载+未完成  
    SUCCESS = 0b00011         # 3: 下载成功
    
    # 后三位状态标志（只能在非SUCCESS状态下有效）
    ERROR = 0b00100           # 4: 错误
    CHARGED = 0b01000            # 8: 收费
    NOT_FOUND = 0b10000       # 16: 网页不存在
    FETCH_ERROR = 0b100000      # 32: 获取网页信息失败
    CONVERT_ERROR = 0b1000000   # 64： 网页信息转换失败
    
    @staticmethod
    def CoreMask():
        return TaskStatus.UNDOWNLOADED | TaskStatus.INCOMPLETED | TaskStatus.SUCCESS 
    
    @staticmethod
    def FullMask():
        return TaskStatus.CoreMask() | TaskStatus.ReaseMask()
        
    def ReaseMask():
        return TaskStatus.ERROR | TaskStatus.CHARGED | TaskStatus.NOT_FOUND|TaskStatus.FETCH_ERROR|TaskStatus.CONVERT_ERROR
    
    @classmethod
    def from_value(cls, value: Union[int, str, 'TaskStatus']) -> 'TaskStatus':
        """从整数、字符串或TaskStatus实例创建枚举
        
        Args:
            value: 输入值，可以是整数、字符串或TaskStatus实例
            
        Returns:
            TaskStatus: 对应的枚举实例
        """
        if isinstance(value, TaskStatus):
            return value
        elif isinstance(value, str):
            # 支持二进制字符串（如"0b101"）和十进制字符串
            if value.startswith('0b'):
                int_value = int(value, 2)
            else:
                try:
                    int_value = int(value)
                except:
                    upper_txt=value.strip().upper()
                    if upper_txt in cls.__members__:
                        return cls[upper_txt]
                    return cls.UNDOWNLOADED
            return cls.from_int(int_value)
        elif isinstance(value, int):
            return cls.from_int(value)
        else:
            __task_status_logger__.error(f"不支持的类型: {type(value)}")
            return cls.UNDOWNLOADED
        
    @classmethod
    def from_int(cls,value: int) -> "TaskStatus":
        value=value& TaskStatus.FullMask()
        
        low_value=value & TaskStatus.SUCCESS
        
        if low_value == TaskStatus.SUCCESS:
            return cls.SUCCESS
        
        #排除未下载 却已完成的
        fuck_val=TaskStatus.INCOMPLETED<<1
        if low_value == fuck_val:
            value-=fuck_val
        
        
        
        return cls(value)
    @property
    def is_downloaded(self) -> bool:
        """第一位：是否下载（私有属性）"""
        return bool(self.value & TaskStatus.INCOMPLETED)
    
    @property
    def is_completed(self) -> bool:
        """第二位：是否完成（私有属性）"""
        return bool(self.value & 0b00010)
    
    @property
    def is_error(self) -> bool:
        """第三位：是否错误（私有属性）"""
        return bool(self.value & TaskStatus.ERROR)
    
    @property
    def is_charged(self) -> bool:
        """第四位：是否收费（私有属性）"""
        return bool(self.value & TaskStatus.CHARGED)
    
    @property
    def is_not_found(self) -> bool:
        """第五位：是否网页不存在（私有属性）"""
        return bool(self.value & TaskStatus.NOT_FOUND)
    
    @property
    def is_fetch_error(self) -> bool:
        """第六位：是否获取网页信息失败（私有属性）"""
        return bool(self.value & TaskStatus.FETCH_ERROR)
    
    @property
    def is_convert_error(self) -> bool:
        """第七位：是否网页信息转换失败（私有属性）"""
        return bool(self.value & TaskStatus.CONVERT_ERROR)
    
    @property
    def has_reaseon(self)->bool:
        return self.value & TaskStatus.ReaseMask() > 0

    
    
    # 前两位状态的公共属性
    @property
    def is_undownloaded(self) -> bool:
        """是否为未下载状态"""
        return self.value & TaskStatus.SUCCESS == TaskStatus.UNDOWNLOADED
    
    @property
    def is_incompleted(self) -> bool:
        """是否为已下载但未完成状态"""
        return self.value & TaskStatus.SUCCESS == TaskStatus.INCOMPLETED
    
    @property
    def is_success(self) -> bool:
        """是否为下载成功状态"""
        return self.value & TaskStatus.SUCCESS == TaskStatus.SUCCESS
    
    def set_error(self) -> 'TaskStatus':
        """设置错误状态（仅非SUCCESS状态有效）"""
        if not self.is_success:
            return TaskStatus(self.value | TaskStatus.ERROR)
        return self
    
    @property
    def set_charged(self) -> 'TaskStatus':
        """设置收费状态（仅非SUCCESS状态有效）"""
        if not self.is_success:
            return TaskStatus(self.value | TaskStatus.CHARGED)
        return self
    
    @property
    def set_not_found(self) -> 'TaskStatus':
        """设置网页不存在状态（仅非SUCCESS状态有效）"""
        if not self.is_success:
            return TaskStatus(self.value | TaskStatus.NOT_FOUND)
        return self
    
    @property
    def set_fetch_error(self) -> 'TaskStatus':
        """设置获取网页信息失败状态（仅非SUCCESS状态有效）"""
        if not self.is_success:
            return TaskStatus(self.value | TaskStatus.FETCH_ERROR)
        return self
    
    @property
    def set_convert_error(self) -> 'TaskStatus':
        """设置网页信息转换失败状态（仅非SUCCESS状态有效）"""
        if not self.is_success:
            return TaskStatus(self.value | TaskStatus.CONVERT_ERROR)
        return self
    
    
    @property
    def clear_error(self) -> 'TaskStatus':
        """清除错误状态"""
        return TaskStatus(self.value & ~TaskStatus.ERROR)
    
    @property
    def clear_charged(self) -> 'TaskStatus':
        """清除收费状态"""
        return TaskStatus(self.value & ~TaskStatus.CHARGED)
    
    @property
    def clear_not_found(self) -> 'TaskStatus':
        """清除网页不存在状态"""
        return TaskStatus(self.value & ~TaskStatus.NOT_FOUND)
    
    @property
    def clear_fetch_error(self) -> 'TaskStatus':
        """清除获取网页信息失败状态"""
        return TaskStatus(self.value & ~TaskStatus.FETCH_ERROR)
    
    @property
    def clear_convert_error(self) -> 'TaskStatus':
        """清除网页信息转换失败状态"""
        return TaskStatus(self.value & ~TaskStatus.CONVERT_ERROR)
    
    @classmethod
    def create(cls, base_status: 'TaskStatus', error: bool = False, 
               charged: bool = False, not_found: bool = False,
               fetch_error: bool = False, convert_error: bool = False
               
               ) -> 'TaskStatus':
        """创建新的任务状态对象
        
        Args:
            base_status: 基础状态（前两位）
            error: 是否错误
            charged: 是否收费  
            not_found: 是否网页不存在
            
        Returns:
            TaskStatus: 新创建的状态对象
        """
        if base_status.is_success and (error or charged or not_found):
            __task_status_logger__.warn("SUCCESS状态不能设置后三位标志")
            return base_status
        
        status = base_status
        if error:
            status = status | cls.ERROR
        if charged:
            status = status | cls.CHARGED
        if not_found:
            status = status | cls.NOT_FOUND
        if fetch_error:
            status = status | cls.FETCH_ERROR
        if convert_error:
            status = status | cls.CONVERT_ERROR
            
            
        return status
    
    def __repr__(self) -> str:
        """详细的状态信息描述"""
        base_desc = {
            TaskStatus.UNDOWNLOADED: "未下载",
            TaskStatus.INCOMPLETED: "部分下载", 
            TaskStatus.SUCCESS: "下载成功"
        }[self.value & TaskStatus.SUCCESS]
        
        flags = []
        if self.is_error:
            flags.append("错误")
        if self.is_charged:
            flags.append("收费")
        if self.is_not_found:
            flags.append("网页不存在")
        if self.is_fetch_error:
            flags.append("获取网页信息失败")
        if self.is_convert_error:
            flags.append("网页信息转换失败")
            
        flags_desc = "+".join(flags) if flags else ""
        
        return f"{base_desc}+{flags_desc}" if flags_desc else base_desc
        
        return (f"TaskStatus(value=0b{self.value:05b}'{base_desc}'{flags_desc}, 原始值={self.value})")
        
    __str__ = __repr__
    
    
def Undownloaded()->TaskStatus:
    return TaskStatus.UNDOWNLOADED
    
def Success()->TaskStatus:
    return TaskStatus.SUCCESS

def Incompleted()->TaskStatus:
    return TaskStatus.INCOMPLETED
    
if __name__=="__main__":   
    
    val=TaskStatus.create(TaskStatus.UNDOWNLOADED, error=True, charged=False, not_found=True)
    print(val)
    
    
    # 基本使用
    print("=== 基本状态 ===")
    undownloaded = TaskStatus.UNDOWNLOADED
    incompleted = TaskStatus.INCOMPLETED
    success = TaskStatus.SUCCESS

    print(undownloaded)    # TaskStatus(value=TaskStatus.UNDOWNLOADED, 状态='未下载', ...)
    print(incompleted)     # TaskStatus(value=TaskStatus.INCOMPLETED, 状态='已下载+未完成', ...)
    print(success)         # TaskStatus(value=TaskStatus.SUCCESS, 状态='下载成功', ...)

    # 测试from_value方法
    print("\n=== from_value测试 ===")
    status1 = TaskStatus.from_value(100)           # 整数
    status2 = TaskStatus.from_value("0b101")     # 二进制字符串  
    status3 = TaskStatus.from_value("8")         # 十进制字符串
    status4 = TaskStatus.from_value('none')     # TaskStatus实例

    print(status1)  # INCOMPLETED
    print(status2)  # 0b101 (INCOMPLETED | ERROR)
    print(status3)  # 0b1000 (UNDOWNLOADED | charged)
    print(status4)  # SUCCESS

    # 测试状态组合
    print("\n=== 状态组合 ===")
    error_status = TaskStatus.INCOMPLETED | TaskStatus.ERROR
    charged_status = TaskStatus.UNDOWNLOADED | TaskStatus.CHARGED
    complex_status = TaskStatus.INCOMPLETED | TaskStatus.ERROR | TaskStatus.CHARGED

    print(error_status)   # INCOMPLETED + 错误
    print(charged_status)    # UNDOWNLOADED + 收费  
    print(complex_status) # INCOMPLETED + 错误 + 收费

    # 测试属性访问
    print("\n=== 属性测试 ===")
    status = TaskStatus.INCOMPLETED | TaskStatus.ERROR
    print(f"是否下载: {status.is_downloaded}")      # True
    print(f"是否完成: {status.is_completed}")        # False  
    print(f"是否错误: {status.is_error}")           # True
    print(f"基础状态: {status.is_incompleted}")       # True

    # 测试设置方法
    print("\n=== 设置方法测试 ===")
    base = TaskStatus.UNDOWNLOADED
    status = base.set_charged.set_not_found
    print(status)  # UNDOWNLOADED + 收费 + 网页不存在

    # SUCCESS状态不能设置后三位
    success_with_error = success.set_error()
    print(success_with_error)  # 仍然是SUCCESS，错误标志被忽略

    # 使用create方法
    print("\n=== create方法测试 ===")
    new_status = TaskStatus.create(TaskStatus.INCOMPLETED, error=True, charged=True)
    print(new_status)  # INCOMPLETED + 错误 + 收费