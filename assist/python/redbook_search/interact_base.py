from DrissionPage import WebPage
import time
import re
import concurrent.futures

from base import logger as logger_helper,UpdateTimeType
from base.except_tools import except_stack
from base.com_decorator import exception_decorator
from base.state import ReturnState
from handle_comment import NoteCommentWriter

from handle_config import redbook_config
from redbook_tools import *

from data import *
from enum import Enum
from pathlib import Path

@exception_decorator()
def click_more_info(more_info):
    if more_info:
        more_info.click()
    # comment_logger.trace("more-click", f"第{index}次", update_time_type=UpdateTimeType.STEP)

#点击 more 子进程
def handle_more(show_mores,comment_logger):
    if not show_mores:
        return
    if len(show_mores)<2:
        click_more_info(more_info=show_mores[0])
        return
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        
        # 使用 enumerate 获取索引和元素
        futures = [executor.submit(click_more_info, more_info) for  more_info in show_mores]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # 获取结果或处理异常
            except Exception as e:
                comment_logger.error("异常",except_stack(),update_time_type=True)

def net_exception(title:str)->bool:
        # 定义关键词列表
        keywords = ["网络", "连接", "超时", "错误", "异常", "失败"]
        
        # 构建正则表达式模式
        pattern = "|".join(keywords)
        
        # 使用正则表达式搜索
        return re.search(pattern, title)

class ResultType(Enum):
    ONLY_NOTE = 1
    ONLY_COMMENT = 2
    BOTH = 3
    
    @property
    def is_only_note(self)->bool:
        return self==ResultType.ONLY_NOTE
    
    @property
    def is_only_comment(self)->bool:
        return self==ResultType.ONLY_COMMENT
    
    @property
    def is_both(self)->bool:
        return self==ResultType.BOTH
    


class InteractBase():
    def __init__(self,note_queue,comment_queue,interact_logger, result_type:ResultType.ONLY_NOTE,next_id_func,sec_sort_fun:None):
        self.wp=WebPage()
        url='https://www.xiaohongshu.com/'
        self.wp.get(url)
        self.interact_logger=interact_logger
        self.note_queue=note_queue
        self.comment_queue=comment_queue
        self.result_type=result_type
        self._theme=""
        self.sec_sort_fun=sec_sort_fun
        self.next_id_func=next_id_func

    def close_note(self):
        self.wp.wait.eles_loaded(redbook_config.path.close_path)
        close_flag=self.wp.ele(redbook_config.path.close_path)
        if close_flag:
            try:
                close_flag.click()
                time.sleep(.5)
            except:
                self.show_except_stack()
                

    @property
    def theme(self)->str:
        return self._theme
    
    
    def set_theme(self,theme:str):
        self._theme=theme
    @property
    def title(self)->str:
        val=re.sub(redbook_config.flag.title_suffix_pattern,"",self.wp.title)
        return val.split(redbook_config.flag.no_tilte_split)[0]
        

    def show_except_stack(self):
        self.interact_logger.error("异常",except_stack(),update_time_type=True)

    #第一步，需要调用这个
    @exception_decorator()
    def click_seach_theme(self,theme,note_type=redbook_config.note_type_map.all):

        self.interact_logger.update_target("采集主题",theme)
        self.interact_logger.reset_time()
        self.interact_logger.info("开始")

        #搜索输入框
        if not self.wp.wait.ele_displayed(redbook_config.path.search_input_path):
            return False
        search_input = self.wp.ele(redbook_config.path.search_input_path)
        search_input.clear()
        search_input.input(f'{theme}\n')
        # time.sleep(.4)

        #搜索按钮
        if not self.wp.wait.ele_displayed(redbook_config.path.search_button_path):
            return False
        seach_button=self.wp.ele(redbook_config.path.search_button_path)
        if not seach_button:
            sys.exit(0)
        seach_button.click()

        #如果是综合，就不需要再次搜索了
        if note_type==redbook_config.note_type_map.all:
            return True

        
        type_button=self.wp.ele(note_type)
        if type_button:
            type_button.click()
        self.wp.ele(redbook_config.path.search_button_path).click() #再次搜索下
        return True
    
    def theme_urls_path(self,theme)->str:
        return os.path.join(self.theme_dir,f"{theme}_urls.json")
        
    def load_theme_urls(self,theme)->list[str]:
        urls_path=self.theme_urls_path(theme)
        if os.path.exists(urls_path):
            with open(urls_path,"r",encoding="utf-8-sig") as f:
                return json.load(f) 
    
    def save_theme_urls(self,theme,urls:list[str]):
        urls_path=Path(self.theme_urls_path(theme))
        lst=[]
        
        if urls_path.exists():
            lst=self.load_theme_urls(theme)
        lst.extend(urls)
        lst=list(set(lst)) #去重
               
        with open(urls_path,"w",encoding="utf-8-sig") as f:
            json.dump(lst,f,ensure_ascii=False,indent=4)  
        self.interact_logger.info("保存url",urls_path,update_time_type=UpdateTimeType.STEP)
            
    
    def theme_urls(self,theme,search_count):

        #测试部分——————————————————————————————————————————————————
        urls_path=os.path.join(self.theme_dir,f"{theme}_urls.json")
        if os.path.exists(urls_path):
            with open(urls_path,"r",encoding="utf-8-sig") as f:
                return json.load(f) 
        #测试部分——————————————————————————————————————————————————

        self.interact_logger.update_target("采集url",theme)
        self.interact_logger.reset_time()
        self.interact_logger.info("开始")
        hrefs=[]
        try:

            #搜索输入框
            if not self.wp.wait.ele_displayed(redbook_config.path.search_input_path):
                return
            search_input = self.wp.ele(redbook_config.path.search_input_path)
            search_input.clear()
            search_input.input(f'{theme}\n')
            # time.sleep(.4)

            #搜索按钮
            if not self.wp.wait.ele_displayed(redbook_config.path.search_button_path):
                return
            seach_button=self.wp.ele(redbook_config.path.search_button_path)
            if not seach_button:
                sys.exit(0)
            self.wp.ele(redbook_config.path.search_button_path).click()


            
            type_button=self.wp.ele(redbook_config.note_type_map.all)
            if type_button:
                type_button.click()
            self.wp.ele(redbook_config.path.search_button_path).click() #再次搜索下
            time.sleep(.5)

            while len(hrefs)<search_count:
                secManager=SectionManager(self.wp,self.fixed_pos)
                secManager.update()
                time.sleep(.5)
                for item in secManager.urls:
                    if item not in hrefs:
                        hrefs.append(item)
                sec=secManager.last
                sec.click()
                self.close_note()

        except Exception as e:
            self.show_except_stack()
            
        #测试部分——————————————————————————————————————————————————
        with open(urls_path,"w",encoding="utf-8-sig") as f:
            json.dump(hrefs,f,ensure_ascii=False)  
        #测试部分——————————————————————————————————————————————————
  
        return hrefs
    
    
    def handle_theme_imp(self,theme,pfunc,search_count):
        if not self.click_seach_theme(theme):
            return False
        hrefs=[]
        try:

            time.sleep(.5)
            self.wp.listen.start(redbook_config.listen.listen_note) 

            secManager=SectionManager(self.wp,self.next_id_func,self.sec_sort_fun)
            secManager.update()

            while len(hrefs)<search_count:
                sec_item=secManager.next(self.title)
                sec=sec_item.sec if sec_item else None
                if not sec :
                    #更新表格
                    # secManager.resume_cur()
                    # secManager.set_wp(self.wp)
                    secManager.update()
                    continue
                time.sleep(.5)
                
                try:
                    if(self.wp.wait.ele_displayed(sec,timeout=5)):
                        sec.click()
                    else:
                        secManager.resume_cur()
                        secManager.update()
                        continue
                    # sec.click()
                except:
                    secManager.resume_cur()
                    secManager.update()
                    continue   
                
                
                
                body=None
                while True:
                    item=self.wp.listen.wait()
                    body=item.response.body
                    if not body:
                        continue
                    if item.target==redbook_config.listen.listen_note:
                        break
                url=self.wp.url
                body["my_link"]=url
                body["title"]=self.title
                body=JsonData(theme=self.theme,json_data=body)
                hrefs.append(url)
                
                pfunc(body)
                self.close_note()
                time.sleep(.5)
                
        
        except Exception as e:
            self.interact_logger.error("异常",f"一共获取{len(hrefs)}个笔记\n{except_stack()}",update_time_type=UpdateTimeType.ALL)
            pass
        finally:
            self.interact_logger.info("完成",f"一共获取{len(hrefs)}个笔记",update_time_type=UpdateTimeType.ALL)
            
            self.save_theme_urls(self.theme,hrefs)

            return hrefs
        
   
    def handle_comment_func(self,csvj_writer):
        def pfunc(body):
            note_id=""
            try:
                note_id=body[1]['data']['items'][0]['id']
            except:
                pass
            self.handle_comment(csvj_writer,note_id=note_id)
        return pfunc
    def handle_note_func(self):
        def pfunc(body):
            self.note_queue.put(body)    #整理到内部队列
        return pfunc
    #只提取评论
    def handle_theme_comment(self,theme,csvj_writer,search_count):
        return self.handle_theme_imp(theme,self.handle_comment_func(csvj_writer),search_count)
    #只提取内容
    def handle_theme_note(self,theme,csvj_writer,search_count):
        return self.handle_theme_imp(theme,self.handle_note_func(),search_count)

    def handle_theme(self,theme,csvj_writer,search_count):
        
        func_map={
            ResultType.ONLY_NOTE:self.handle_theme_note,
            ResultType.ONLY_COMMENT:self.handle_theme_comment,
            ResultType.BOTH:self.handle_theme_note_comment
        }
        
        if func_map.get(self.result_type):
            return func_map[self.result_type](theme,csvj_writer,search_count)
        else:
            return None
        
        
        
    #提取内容+评论
    def handle_theme_note_comment(self,theme,csvj_writer,search_count):
        def fun(body):
            self.handle_note_func()
            self.handle_comment_func(csvj_writer)
        return self.handle_theme_imp(theme,fun,search_count)
        
        

    def handle_comment_by_urls(self,urls,csvj_writer:NoteCommentWriter):
        
        self.interact_logger.update_target("采集评论—主题")
        self.interact_logger.reset_time()
        self.interact_logger.info("开始")
        for url in urls:
            self.wp.get(url)
            # time.sleep(.3)
            result=ReturnState.from_state(self.handle_comment(csvj_writer))
            if result.is_netExcept:
                return result
        self.interact_logger.info("完成",update_time_type=UpdateTimeType.ALL)
        
   
   #针对已打开的笔记，进行评论采集
    @exception_decorator() 
    def handle_comment(self,csvj_writer:NoteCommentWriter,note_id:str=""):
       
        time.sleep(.5)
        #处理评论
        title=self.title
        comment_logger=logger_helper("采集评论",title)
        
        container=self.wp.ele(redbook_config.path.comments_container_path,timeout=1)
        comments_total=0
        try:
            raw_total=container.ele('.total').text
            splits=raw_total.split()
            if len(splits)>1:
                comments_total=int( splits[1])
        except:
            #网络问题，提前退出
            if net_exception(title):
                comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
                return ReturnState.NETEXCEPT
            
            
            pass

        comment_logger.info("开始",f"总共{comments_total}个",update_time_type=UpdateTimeType.STEP)
        if comments_total<1:
            comment_logger.info("结束",f"共计时长",update_time_type=UpdateTimeType.ALL)
            return
        
        scroll_count=0
        
    
        #网络问题，提前退出
        if net_exception(title):
            comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
            return ReturnState.NETEXCEPT
        
        
        while not self.wp.wait.ele_displayed(redbook_config.path.comment_end_path,timeout=.1):
            #滚动
            if not self.wp.wait.ele_displayed(redbook_config.path.note_scroll_path,timeout=.5):
                break
            scroller= self.wp.ele(redbook_config.path.note_scroll_path)
            scroller.scroll.to_bottom()
            # time.sleep(.1)
            scroll_count+=1
            if scroll_count>20 and scroll_count %20 ==0 :
                time.sleep(1)
    
            #网络问题，提前退出
            if net_exception(title):
                comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
                return ReturnState.NETEXCEPT
            
        comment_logger.info("滚动到底",f"共{scroll_count}次",update_time_type=UpdateTimeType.STEP)
               

        more_index=1

        while True:        
            #更多评论
            show_mores=self.wp.eles(redbook_config.path.comment_more_path,timeout=1)
            comment_logger.trace("show-more",f"第{more_index}次,共{len(show_mores)}个",update_time_type=UpdateTimeType.STEP)
            if not show_mores:
                break
            handle_more(show_mores,comment_logger)
            more_count=len(show_mores)
            
            comment_logger.trace("more-click",f"共{more_count}个,完成",update_time_type=UpdateTimeType.STEP)
            more_index+=1
            if (more_index>10 and more_index %10 ==0 ) or more_count>10:
                time.sleep(1)
    
            #网络问题，提前退出
            if net_exception(title):
                comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
                return ReturnState.NETEXCEPT

    
        #网络问题，提前退出
        if net_exception(title):
            comment_logger.error("异常",f"{self.title}\n{except_stack()}",update_time_type=UpdateTimeType.STEP)
            return ReturnState.NETEXCEPT
        
            
        comment_container=self.wp.ele(redbook_config.path.comments_container_path,timeout=.5)
        if not comment_container:
            return
        comment_container_html=comment_container.html
        
        comment_logger.info("结束",f"共计时长",update_time_type=UpdateTimeType.ALL)

        #发送到笔记处理队列，并发执行
        comment_data=CommentData(csvj_writer,self.theme,comment_container_html,note_id,title)
        self.comment_queue.put(comment_data)



if __name__ == '__main__':
    
    data=None
    with open(r"F:\worm_practice\red_book\notes\祛湿url\祛湿url_urls.json","r",encoding="utf-8-sig") as f:
        data= json.load(f) 
    print(data)