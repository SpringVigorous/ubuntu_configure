from abc import ABC, abstractmethod

class MyBaseClass(ABC):
    @abstractmethod
    def my_method(self):
        pass

class MyDerivedClass(MyBaseClass):
    def my_method(self):
        print(f"This is the derived {__class__} method")
            
class MyDerivedClass1(MyBaseClass):
    def my_method(self):
        print(f"This is the derived {__class__} method")
        
class MyDerivedClass2(MyDerivedClass1):
    def my_method(self): 
        # super().my_method()
        print(f"This is the derived {__class__} method")
# 这将引发 TypeError，因为 MyBaseClass 是抽象基类，不能直接实例化
# my_base = MyBaseClass()

base_lst :list[MyBaseClass]= [MyDerivedClass(),MyDerivedClass2(),MyDerivedClass1()]

for base in base_lst:
    base.my_method()  # 输出: This is the derived class method