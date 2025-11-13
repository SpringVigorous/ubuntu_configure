import math
from collections.abc import Iterable
from base.collect_tools import unique
def ceil(n, m):
    n=float(n)
    m=float(m)
    return math.ceil(n / m) * m

def ceil_5(n):
    return ceil(n,5)

#用于获取最少的数字位数
def format_count(count:int):
    return math.ceil(math.log10(count))
def split_singles(start:int|float,end:int|float,splits:Iterable[int|float]|int|float)->list[int:float]:
    if not isinstance(splits,Iterable):
        splits=[splits]
    start,end=min(start,end),max(start,end)
    splits=unique(sorted(filter(lambda x:x>=start and x<=end, splits)))
    results=[start]
    results.extend(splits)
    results.append(end)
    return unique(results)

def split_pairs(start:int|float,end:int|float,splits:Iterable[int|float]|int|float)->list[tuple[int:float,int:float]]:
    vals=split_singles(start,end,splits)
    return [(vals[i],vals[i+1]) for i in range(len(vals)-1)]


def split_pairs_diff(start:int|float,end:int|float,splits:Iterable[int|float]|int|float)->list[tuple[int:float,int:float]]:
    vals=split_pairs(start,end,splits)
    return [(start,end-start) for start,end in vals]


def float_to_int_if_approx(num: float, epsilon: float = 1e-9) -> int | float:
    """
    判断浮点数是否近似于整数，若是则返回整数，否则返回原浮点数
    :param num: 输入浮点数（支持正负数、零）
    :param epsilon: 误差阈值（默认 1e-9，可按需调整，越小越严格）
    :return: 整数（近似时）或原浮点数（不近似时）
    """
    # 1. 校验输入类型（确保是浮点数，可选）
    if not isinstance(num, float):
        raise TypeError(f"输入必须是浮点数，当前类型：{type(num)}")
    
    # 2. 计算最接近的整数（round() 自动处理正负数、四舍五入）
    nearest_int = round(num)
    
    # 3. 判断差值是否在误差阈值内（绝对值 < epsilon 视为近似）
    if abs(num - nearest_int) <= epsilon:
        return nearest_int  # 近似整数，返回整数类型
    else:
        return num  # 不近似，保留原浮点数
