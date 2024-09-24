#抖音作品
from openpyxl import load_workbook
from openpyxl.styles import Font
from selenium.webdriver.common.by import By
from common.selenium_tools import SeleniumHelper
from pandas import DataFrame
from tqdm import tqdm
from openpyxl import load_workbook
import os
import time


class Section:
    def __init__(self,sec,yVal,id,already,url=""):
        self.sec=sec
        self.yVal=yVal
        self.id=id
        self.already=already
        self.url=url

def contain_search_key(str):
    lst=["大家都在搜","相关搜索","热门搜索"]
    return  any([key in str for key in lst])
    

class SectionManager:
    def __init__(self,wp):
        self.wp=wp
        self.cur_secs=[]
        self.secs=[]
        self.cur_index=0
        
    def __set_secs(self,secs:list):
        self.cur_secs=secs
        
        for sec in self.cur_secs:
            sec_ids=[sec.id for sec in self.secs]
            if sec.id not in sec_ids:
                self.secs.append(sec)
            else:
                self.secs[sec_ids.index(sec.id)]=sec
        


    def update(self):
        
        # await asyncio.sleep(.3)
        # time.sleep(.3)
        
        org_secs=self.wp.wait_presence_of_elements(By.XPATH,'//section[@class="note-item"]')
        sorted(org_secs,key=lambda x:x.location['y'])

        secs=[]
        for sec in org_secs:
            text=r"\n".split(sec.text)[0]
            if not contain_search_key(text):
                try:
                    href_obj=sec.find_element(By.XPATH,f'./div/a[2]')
                    if not href_obj:
                        continue
                    href=href_obj.get_attribute("href")
                    secs.append(Section(sec,sec.location['y'],text,False,href))
                except:
                    pass

        
 
        
        if self.secs:
            for sec in secs:
                
                org=self.get_by_id(sec.id)
                if org:
                    sec.already=org.already
                    
        
        

        self.__set_secs(secs)
    def get_by_id(self ,id):
        secs=[sec for sec in self.secs if sec.id==id]
        return secs[0] if secs else None
        

    
    def next(self):

        for sec in self.cur_secs:
            if not sec.already:
                sec.already=True
                self.cur_index=self.cur_secs.index(sec)
                yield sec.sec
     
    def resume_cur(self):
        if self.cur_index<len(self.cur_secs):
            self.cur_secs[self.cur_index].already=False
        
        
    def count(self):

        return sum([ 0 if sec.already else 1  for sec in self.cur_secs ])


      



def douyin_info(url,driver_path,xls_path):
    search_count=10
    stoped=False
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
        key = '太极拳'
        driver.wait_presence_of_element(By.ID,'search-input').send_keys(f'{key}\n')
        driver.wait_presence_of_element(By.XPATH,'//div[@class="search-icon"]').click()

        list_rows=[]
        
        #三.采集 
        sec_i=0
        
        secManager=SectionManager(driver)
        secManager.update()
        while (secManager.count())>0:
            
            if sec_i>search_count:
                stoped=True
                break
            # secManager.update()
            

            sec=next(secManager.next()) 
            if not sec:
                continue

            
            try:
                def func(driver):
                    
                    
                    driver.wait_presence_of_element(By.XPATH,'//div[@class="video-info"]')
                    
                    
                    pass
                driver.handle_new_url(sec.url,driver)
                
                sec.click()
            except:
                secManager.resume_cur()
                secManager.update()
                continue
          
            close_flag=driver.wait_presence_of_element(By.XPATH,'//div[@class="close close-mask-dark"]')
            if close_flag:
                try:
                    close_flag.click()
                except:
                    continue

                

        for  item in tqdm(org_secs):
            
            node=item.find_element(By.XPATH,'./div/a')
            
            dict_row ={
            "视频标题":node.text,

            "视频链接":node.get_attribute("href")
            }
            list_rows.append(dict_row)

            
        file_name = os.path.join(xls_path, f"作品集.xlsx")
        DataFrame(list_rows).to_excel(file_name,index=False)


            
if __name__ == '__main__':
    url='https://www.xiaohongshu.com/'
    drive_path=r"D:\Tool\chromedriver-win64\chromedriver.exe"
    xls_path=r"F:\worm_practice\red_book"
    douyin_info(url,drive_path,xls_path)