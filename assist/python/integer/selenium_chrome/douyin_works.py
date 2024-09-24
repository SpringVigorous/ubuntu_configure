#抖音作品
from openpyxl import load_workbook
from openpyxl.styles import Font
from selenium.webdriver.common.by import By
from common.selenium_tools import SeleniumHelper
from pandas import DataFrame
from tqdm import tqdm
from openpyxl import load_workbook
import os


domain= "https://www.chanmama.com"

def douyin_info(url,driver_path,xls_path):
    with SeleniumHelper(driver_path=drive_path) as driver:
    #热门视频页面
        
        #如果强制定向到登录界面
        if driver.wait_url_contains(url,"login"):
            #单击登录按钮
            driver.wait_presence_of_element(By.XPATH,"web-login-button").click()# 登录右侧 flex 对齐项目中心
            if not driver.wait_leave_of_element(By.XPATH,'//div[@web-login-account-password__button-wrapper"]'):
                exit() #如果登录失败,结束程序

        #二.搜索
        # key = input("请输入关键词:")
        # driver.wait_presence_of_element(By.ID,'e2e-common-search-input').send_keys(key)
        # driver.wait_presence_of_element(By.ID,'e2e-common-search-btn').click()

        list_rows=[]
        
        #三.采集 
        rows = driver.wait_presence_of_elements_until_last(By.XPATH,'//li[@class="wqW3g_Kl WPzYSlFQ OguQAD1e"]')


        for  item in tqdm(rows):
            
            node=item.find_element(By.XPATH,'./div/a')
            
            dict_row ={
            "视频标题":node.text,

            "视频链接":node.get_attribute("href")
            }
            list_rows.append(dict_row)

            
        file_name = os.path.join(xls_path, f"作品集.xlsx")
        DataFrame(list_rows).to_excel(file_name,index=False)


            
if __name__ == '__main__':
    url="https://www.douyin.com/user/MS4wLjABAAAAiWLBwkqSxfbwmsDwSiIgsMejChfAhO_U_FTyrqFFoio?from_tab_name=main"
    drive_path=r"D:\Tool\chromedriver-win64\chromedriver.exe"
    xls_path=r"F:\教程\三维讲解建筑结构图"
    