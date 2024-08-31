class NotesInfo:
    _instance= None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            
            
            
            
        return cls._instance



# 使用示例
instance1 = NotesInfo("data1")
instance2 = NotesInfo("data2")
instance3 = NotesInfo("data3")
instance4 = NotesInfo("data4")

print(instance1 is instance2)  # 输出 True，因为只有一个实例
print(instance1.url)  # 输出 "data1"
print(instance2.url)  # 输出 "data1"