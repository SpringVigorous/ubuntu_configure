str_val="abc"
str_bytes=str_val.encode('utf-8')
print(str_bytes)

str_val_2=str_bytes.decode('utf-8')
print(str_val_2)