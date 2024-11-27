import math
def ceil(n, m):
    n=float(n)
    m=float(m)
    return math.ceil(n / m) * m

def ceil_5(n):
    return ceil(n,5)