import math
from collections.abc import Iterable
from collect_tools import unique
def ceil(n, m):
    n=float(n)
    m=float(m)
    return math.ceil(n / m) * m

def ceil_5(n):
    return ceil(n,5)


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