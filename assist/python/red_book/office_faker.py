
#pip install python-office
import office
#模拟数据
office.excel.fake2excel(columns=['name', 'uuid4','company'], rows=200,path=r"E:\小红书竞标\office_fake.xlsx")