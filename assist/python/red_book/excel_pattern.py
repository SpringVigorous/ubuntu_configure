import pandas as pd
import numpy as np
from pandas.io.formats.style import Styler

count=100
data={}
names=[]
ids=[]
majors=[]
grades=[]
for i in range(count):
    names.append("学生"+str(i+1))
    ids.append("{:03d}".format(i+1))
    majors.append("计算机科学与技术" if i%2==0 else "软件工程")
    grades.append(np.random.randint(30,101))

data["id"]=ids
data["name"]=names
data["major"]=majors
data["grade"]=grades

def type_color(x):
    color="red" if x < 60 else( "green" if x < 80 else "blue")
    return f"color:{color}" 
 
student =pd.DataFrame(data)
student.set_index("id",drop=True,inplace=True)
# 应用条件格式化
styled_df: Styler = student.style.applymap(type_color,subset=["grade"])
print(student)

student.to_excel("student.xlsx",sheet_name="学生信息")

# # 应用条件格式化
# # styled_df: Styler = student.style.apply(lambda x: "color:red" if x<60 else "color:green" if x<80 else "color:blue",subset=["grade"])

# # 创建ExcelWriter对象
# writer = pd.ExcelWriter('student.xlsx', engine='openpyxl')

# student.to_excel("student.xlsx",sheet_name="学生信息")

# \
# # 获取工作表
# worksheet = writer.sheets['学生信息']
# # 设置工作表为可见
# worksheet.sheet_state = 'visible'

# writer.close()