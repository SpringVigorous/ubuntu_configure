from enum import Enum

class ReturnState(Enum):
    SUCCESS = (1, "成功")
    FAILED = (2, "失败")
    EXCEPT = (3, "异常")
    IGNORE = (4, "忽略")
    NONE = (5, "空")
    NETEXCEPT=(6,"网络异常")

    def __init__(self, code, description):
        self.code = code
        self.description = description

    @property
    def is_success(self):
        return self == self.SUCCESS

    @property
    def is_failed(self):
        return self == self.FAILED

    def is_except(self):
        return self == self.EXCEPT

    @property
    def is_ignore(self):
        return self == self.IGNORE

    @property
    def is_none(self):
        return self == self.NONE
    
    @property
    def is_netExcept(self):
        return self == self.NETEXCEPT

    def __bool__(self):
        return self in [self.SUCCESS, self.IGNORE,self.NONE,]
    
    @classmethod
    def from_state(cls, state=None):

        # if not isinstance(state, cls):
        #     return cls.NONE

        if not str(type(state))==str(cls):
            return cls.NONE
        
        return state

    @classmethod
    def from_code(cls, code):
        """从数值代码转换为 ReturnState 枚举值"""
        for state in cls:
            if state.code == code:
                return state
        return ReturnState.NONE


    @classmethod
    def from_description(cls, description):
        """从描述字符串转换为 ReturnState 枚举值"""
        for state in cls:
            if state.description == description:
                return state
        return ReturnState.NONE

    
    
# 示例用法
if __name__ == "__main__":
    # 创建枚举实例
    result = ReturnState.SUCCESS

    # print(ReturnState.from_state(result))
    print(ReturnState.from_state())
    print(ReturnState.from_state(ReturnState.IGNORE))