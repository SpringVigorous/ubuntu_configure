
import requests
import parsel
from  pprint import pprint
import os
import re


root_dir=r"F:\cache\优美图"

domain="https://www.youmeitu.com/"

headers={
    
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
"Cookie":"PHPSESSID=6nibkvjh03pb8chl54blnv417n; Hm_lvt_4e8bffbc9979979c5952b668dad1fe4d=1724124588; HMACCOUNT=D55DFEF59F0F3227; Hm_lpvt_4e8bffbc9979979c5952b668dad1fe4d=1724132862",
"Referer":"https://www.youmeitu.com/mengchongtupian/list_6.html",
}

def sanitize_filename(filename):
    """
    替换Windows系统中不允许出现在文件名中的字符为下划线。
    
    参数:
    filename (str): 需要清理的文件名。
    
    返回:
    str: 清理后的文件名。
    """
    # Windows系统不允许的文件名字符
    illegal_chars = r'[\\/:*?"<>|]'
    # 使用下划线替换非法字符
    sanitized_filename = re.sub(illegal_chars, '_', filename)
    return sanitized_filename

def page_count(html):
    #获取页数
    count=1
    nums=re.findall(r'<div class="NewPages"><ul><li><a>共(\d+)页: ',html,re.S)
    if  nums is not None and len(nums)>0 :
        count= int(nums[0])
    return count
        

response = requests.get(domain,headers=headers)
response.encoding = 'utf-8'

sel=parsel.Selector(response.text)
theme_index=1


for item in sel.css(".ChannelTit a" ):
    org_url=item.css("::attr(href)").get()
    
    # org_url=r'https://www.youmeitu.com/mengchongtupian/'
    
    name=item.css("::attr(title)").get()
    theme_dir=os.path.join(root_dir,f"{theme_index}_{name}")
    os.makedirs(theme_dir,exist_ok=True)
    theme_index+=1
    # https://www.youmeitu.com/mengchongtupian/557.html
    theme_count=1
    i=1
    
    while i<=theme_count:
        list_url=f"{org_url}list_{i}.html"
        # print(url)
        response = requests.get(list_url,headers=headers)
        response.encoding = 'utf-8'
        theme_count=page_count(response.text)
        
        if i==1 and theme_count>1 :
            print(f"{theme_dir}：共有{theme_count}个页" )
        
        info=parsel.Selector(response.text)
        title_index=1
        for inner in info.css(".TypeList li"):
            
            raw_latter=inner.css("a::attr(href)").get()
            # raw_latter="/mengchongtupian/557.html"
            j=1
            title_count=1

            title_dir=""
            while j<=title_count:
                # print(cur_url)
                name,ext=os.path.splitext(raw_latter)
                #替换windows不允许的字符
                name=sanitize_filename(name)
                
                
                cur_url=domain + f"{name}_{j}{ext}"
                response = requests.get(cur_url,headers=headers)

                response.encoding = 'utf-8'
                # pprint(response.text)
                
                #获取页数
                title_count=page_count(response.text)
                

                
                sel_images=parsel.Selector(response.text)
                vals=sel_images.css(".ImageBody p")

                for val in vals:
                    if val.css("::attr(align)").get() == "center":
                        
                        img_url=domain + val.css("img::attr(src)").get()
                        cur_title=val.css("img::attr(title)").get()
                        # print(img_url)
                        response = requests.get(img_url,headers=headers)
                        if j==1:
                            title_dir=os.path.join(theme_dir,f"{title_index}_{cur_title}" )
                            os.makedirs(title_dir,exist_ok=True)
                            if title_count>1 :
                                print(f"{title_dir}：共有{title_count}个" )
                        title_index+=1
                        with open(os.path.join(title_dir,f"{j}.jpg"),"wb") as f:
                            f.write(response.content)
                j=j+1
                # break
            
    i+=1
    

print(response.text)