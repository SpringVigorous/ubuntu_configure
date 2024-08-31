import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 

df=pd.read_csv("./integer/test/players.csv",encoding="gbk")
print(df)

plt.rcParams["font.sans-serif"]=["SimHei"]
sns.lmplot(x="得分", y="命中率", data=df,fit_reg=False)
plt.show()


