
def dynamic_wrapper(*functions):

    def wrapper(*args, **kwargs):
        results = {}
        for func in functions:
            try:
                result = func(*args, **kwargs)
                results[func.__name__] = result
            except Exception as e:
                print(f"Error calling function {func.__name__}: {e}")
        return results

    return wrapper

# 假设我们有多个函数
def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

# 使用装饰器包装这两个函数
combined_function = dynamic_wrapper(add, multiply)
combined_function1 = dynamic_wrapper(combined_function, multiply)
# 现在调用这个组合函数
result = combined_function(2, 3)
print(result)  # 输出: {'add': 5, 'multiply': 6}

result = combined_function1(2, 3)
print(result)  # 输出: {'add': 5, 'multiply': 6}