from collections import Counter,deque

def unique(original_list):
    counter = Counter(original_list)
    return list(counter.keys())

def remove_none(original_list):
    return filter(lambda x: x ,original_list)


def dict_first_item(val:dict):
    if not dict:
        return
    
    key= next(iter(val))
    return key,val[key]

def dict_val(cols:dict,key):
    if not cols:
        return

    return cols.get(key)



class Stack:
    def __init__(self):
        # 初始化一个 deque 对象来存储栈中的元素
        self.items = deque()

    def is_empty(self):
        # 判断栈是否为空，如果栈中元素数量为 0，则返回 True，否则返回 False
        return len(self.items) == 0

    def push(self, item):
        # 入栈操作，使用 deque 的 append 方法将元素添加到栈顶
        self.items.append(item)

    def pop(self):
        # 出栈操作，如果栈为空，返回 None；否则使用 deque 的 pop 方法移除并返回栈顶元素
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        # 查看栈顶元素，如果栈为空，返回 None；否则返回栈顶元素，但不将其从栈中移除
        if self.is_empty():
            return None
        return self.items[-1]

    def size(self):
        # 返回栈中元素的数量
        return len(self.items)



# 以下是使用自定义 Stack 类的示例
if __name__ == "__main__":
    stack = Stack()
    # 入栈操作
    stack.push(1)
    stack.push(2)
    stack.push(3)
    print("当前栈的大小:", stack.size())
    print("栈顶元素:", stack.peek())
    # 出栈操作
    popped_item = stack.pop()
    print("出栈的元素:", popped_item)
    print("出栈后栈的大小:", stack.size())
    print("此时栈顶元素:", stack.peek())