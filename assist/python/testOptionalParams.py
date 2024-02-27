
def printVal(a,b,interval):
    print("%5d-%s:%d"%(a,b,interval))


def printArgs(**args):
    print("原始内容为:",args)
    printVal(**args)
    a=str(args)
    c=a.center(100,"*")
    print(c)
    d=dict(fun="dfaf",val=2)
    print(d)
    print("{0[val]:15d}".format(d))
    g=10
    e=f"{g+1}"
    print(e)

interval=100
printArgs(a=100,b="dfadf",interval=interval)
