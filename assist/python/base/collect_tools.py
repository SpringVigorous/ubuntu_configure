from collections import Counter,deque
from itertools import groupby

def unique(original_list):
    counter = Counter(original_list)
    return list(counter.keys())

#删除连续相同的元素
def remove_consecutive_duplicates(lst):
    return [key for key, group in groupby(lst)]
 



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

#元素归类，元素给出值即对应索引(紧邻重复值，索引序列)
def get_consecutive_elements_info(lst)->list:
    """
    获取列表中紧邻重复元素及非重复元素的信息（值、索引、是否重复）
    
    :param lst: 输入列表
    :return: 字典列表，每个字典包含 'value'（元素值）、'indices'（索引列表）、'is_consecutive_duplicate'（是否紧邻重复）
    """
    if not lst:  # 处理空列表
        return []
    
    result = []
    start_index = 0  # 连续元素的起始索引
    prev_value = lst[0]  # 前一个元素的值
    
    # 从第二个元素开始遍历
    for i in range(1, len(lst)):
        current_value = lst[i]
        if current_value != prev_value:
            # 前一段连续元素结束，记录信息
            indices = list(range(start_index, i))
            result.append((prev_value, indices) )
            # 更新起始索引和前一个值
            start_index = i
            prev_value = current_value
    
    # 处理最后一段连续元素
    last_indices = list(range(start_index, len(lst)))
    result.append((prev_value, last_indices) )
    
    return result



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