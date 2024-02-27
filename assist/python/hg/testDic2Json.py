import json
a={"s":23,"df":2.0}
b=[334,63,"sdf"]
a["c"]=b

def print(**kwargs):
    with open(r"D:\dwgTemp\test1.json","w") as f:
        json.dump(kwargs,f)

print(**a)

# with open(r"D:\dwgTemp\test.json","w") as f:
#     json.dump(a,f)