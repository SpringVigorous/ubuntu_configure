# 

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


      
def get_val(org_str,del_str:str)->int:
    if type(org_str)==str:
        dest_str=org_str.replace(del_str,"").strip()
        try:
            return int(dest_str) if len(dest_str)>0 else 0
        except:
            return 0
    return org_str

def redbook_info(url,driver_path,xls_path):
    search_count=10
    stoped=False
    with SeleniumHelper(driver_path=drive_path) as driver:
        # driver.set_timeout(2,.1)
    #热门视频页面
        
        #如果强制定向到登录界面
        if driver.wait_url_contains(url,"login"):
            #单击登录按钮
            driver.wait_presence_of_element(By.XPATH,"web-login-button").click()# 登录右侧 flex 对齐项目中心
            if not driver.wait_leave_of_element(By.XPATH,'//div[@web-login-account-password__button-wrapper"]'):
                exit() #如果登录失败,结束程序

        #二.搜索
        # key = input("请输入关键词:")
        # key = '太极拳'
        # driver.wait_presence_of_element(By.ID,'search-input').send_keys(f'{key}\n')
        # driver.wait_presence_of_element(By.XPATH,'//div[@class="search-icon"]').click()

        
            
        cur_time=time.time()
        coments=[]
        
        while True:
       
            show_mores=driver.wait_presence_of_elements(By.XPATH,'//div[@class="show-more"]')
            if show_mores:
                for more_info in show_mores:
                    more_info.click()
                    
            func=driver.wait_presence_of_elements_until_last if not coments else driver.wait_presence_of_elements
            cur_coments=  func(By.XPATH,'//div[@class="content"]')
            if not cur_coments:
                break

            if len(coments)==len(cur_coments):
                break
            coments=cur_coments

        print(f"共{len(coments)}条评论，用时{time.time()-cur_time}秒")
        
        cur_time=time.time()
        
        # with open(os.path.join(xls_path,f"{driver.title}评论.html"),"w",encoding="utf-8") as f:
        #     f.write(driver.page_source)


        items=driver.wait_presence_of_elements(By.XPATH,'.//div[@class="comment-inner-container"]')
        rows=[]
        
        

        #参考 cache_data/comment-inner-container.html
        for  index,inner_item in enumerate(tqdm(items)):
            if index==0:
                with open(os.path.join(xls_path,f"{index}-{driver.title}评论.html"),"w",encoding="utf-8") as f:
                    f.write( driver.html_code(inner_item))
            
            
            author_info=inner_item.find_element(By.XPATH,'./div[@class="right"]')
            
            # author=info.find_element(By.XPATH,'./div[1]//div[@class="name"]')
            author=author_info.find_element(By.XPATH,'./div//a[@class="name"]')
            name=author.text
            id=author.get_attribute("data-user-id")
            ref=author.get_attribute("href")
            comment=author_info.find_element(By.XPATH,'./div[@class="content"]').text
            
            info=author_info.find_element(By.XPATH,'./div[@class="info"]')
            
            date_info=info.find_element(By.XPATH,'./div[@class="date"]')
            date=date_info.find_element(By.XPATH,'./span[1]').text
            pos=date_info.find_element(By.XPATH,'./span[2]').text
            
            like_info=info.find_element(By.XPATH,'./div[@class="interactions"]')
            like_count=get_val(like_info.find_element(By.XPATH,'./div[@class="like"]//span[@class="count"]').text,"赞")
            reply_count=get_val(like_info.find_element(By.XPATH,'./div[@class="reply icon-container"]//span[@class="count"]').text,"回复")
            

            data={
                "name":name,
                "id":id,
                "ref":ref,
                "comment":comment,
                "date":date,
                "pos":pos,
                "like_count":like_count,
                "reply_count":reply_count,
                
            }
            rows.append(data)
        
        print(f"获取评论:用时{time.time()-cur_time}秒")
        cur_time=time.time()
        
        df=DataFrame(rows)

        df.to_excel(os.path.join(xls_path,f"{driver.title}评论.xlsx"),index=False)

       

        print(f"输出:用时{time.time()-cur_time}秒")


            
if __name__ == '__main__':
    from base import worm_root

    url='https://www.xiaohongshu.com/explore/66cdaabd000000001f01f16e?xsec_token=ABegm4vPSBdyhgubz1i7dTbPRbj35Sp_tuHPan2Dp2pYA=&xsec_source=pc_feed'
    drive_path=r"D:\Tool\chromedriver-win64\chromedriver.exe"
    xls_path=worm_root/r"red_book"
    redbook_info(url,drive_path,xls_path)