import chardet


org_str="图名：未知图纸"
val=org_str.encode('utf-8')
print(chardet.detect(org_str.encode()))
print(type(org_str))
print(org_str)
print(val)
val1=val+"图名".encode("gbk")
# print(val1.decode("utf-8"))
print(val1)
