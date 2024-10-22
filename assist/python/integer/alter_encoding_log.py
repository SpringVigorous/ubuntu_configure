import re
from pathlib import Path
# 定义要匹配的字符串

file_path=Path(r"F:\test\ubuntu_configure\assist\python\logs\alter_encoding\alter_encoding-trace.log")

text =""
with open(file_path,"r",encoding="utf-8-sig") as f:
    text = f.read()


# 编写正则表达式
pattern = r'成功转换：\[ (.*?) \]->\[ .*? \]:(.*?)->utf-8-sig'

# 使用 re.search 进行匹配
match = re.findall(pattern, text, re.DOTALL)
if match:
    with open(file_path.with_stem(file_path.stem + "_match"),"w",encoding="utf-8-sig") as f:
        for m in match:
            f.write("\t".join(m) + "\n")
else:
    print("No match found")