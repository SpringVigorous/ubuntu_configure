def safe_format(obj, fmt_spec=""):
    """
    安全格式化函数：
    - 若对象有自定义 __format__ 方法，直接使用；
    - 若无，且为 bytes 类型，解码为 UTF-8（错误替换）后格式化；
    - 其他类型用 str() 兜底格式化。
    
    参数：
        obj: 待格式化的对象
        fmt_spec: 格式说明符（如 ":10s" 左对齐10位、 ":d" 整数格式等）
    返回：
        格式化后的字符串
    """
    # 步骤1：判断对象的 __format__ 是否为有效自定义实现
    # 原理：自定义类会重写 __format__，与 object 的默认实现不同
    obj_class = obj.__class__
    has_valid_format = obj_class.__format__ is not object.__format__
    
    if has_valid_format:
        # 步骤2：有有效 __format__，直接格式化（支持格式符）
        try:
            return format(obj, fmt_spec)
        except Exception:
            # 极端情况：自定义 __format__ 报错，兜底用 str()
            return str(obj)
    else:
        # 步骤3：无有效 __format__，优先处理 bytes 类型
        if isinstance(obj, bytes):
            # 解码为 UTF-8，无效字节用 � 替换（避免报错）
            decoded_str = obj.decode("utf-8", errors="replace")
            return format(decoded_str, fmt_spec)
        else:
            # 其他类型（如 list、dict 等），用 str() 兜底格式化
            return format(str(obj), fmt_spec)


# 配合 f-string 使用（直接调用 safe_format 即可）
def f_safe_format(obj, fmt_spec=""):
    """简化 f-string 调用的辅助函数"""
    return safe_format(obj, fmt_spec)