from lxml import etree
import os
import re
import shutil
from pathlib import Path




# //*[@id="page-series-index"]/div/div/div[2]/div/div[1]/div[2]/h4
# /html/body/div[2]/div[4]/div/div/div/div/div/div[2]/div/div[9]/div[2]/h4

# <h4 data-v-493154f0="" title="Zeno" class="channel-name">Zeno</h4>

def make_dir_from_html(html_str:str,root_dir:str)->str:
    html=etree.HTML(html_str)
    for item in html.xpath('//h4[@class="channel-name"]/text()'):
        # 替换所有空白字符 去掉·
        item = re.sub(r"[\s·]+", "", item)
        item=item.strip()
        print(item)
        if not item:
            continue
        cur_dir=os.path.join(root_dir,item)
        # os.makedirs(cur_dir,exist_ok=True)
        os.makedirs(os.path.join(cur_dir,"弹幕"),exist_ok=True)
        if "合集" in item :
            old_path=os.path.join(root_dir,item.replace("合集","合集·"))
            if  os.path.exists(old_path):
                # 复制整个文件夹及其内容
                shutil.copytree(old_path, cur_dir, dirs_exist_ok=True)
                shutil.remove(old_path)
                
                
def check_lost(root_dir:str):
    unhandled_files=[]
    handled_files={}
    # 遍历“哔哩哔哩视频”文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(root_dir):
        for item in files:
            item_split=item.split(".")
            suffix=item_split[-1]

            if suffix in ["mp4","srt","m4s"]:
                is_srt=suffix =="srt"
                is_m4s=suffix =="m4s"
                is_mp4=suffix =="mp4"
                
                if is_m4s:
                    cur_path=os.path.join(root,item)
                    unhandled_files.append(cur_path)
                    #顺便删除，重新下载
                    os.remove(cur_path)
                else:
                    index=-1 if  is_mp4  else -2
                    cur_name= os.path.join(root,".".join( item_split[:index]))
                    if not  cur_name in handled_files:
                        handled_files[cur_name]=1
                    else :
                        handled_files[cur_name]+=1
        
    for key,val in handled_files.items():
        if val<2:
            unhandled_files.append(key)
    unhandled_files.sort()
    print(f"以下文件缺失收据：{"\n".join(unhandled_files)}")
    
            
            
#哔哩哔哩 视频 整理
def move_bilibili_folders(root_folder,sub_folder_name:str="哔哩哔哩视频"):

    # 遍历根文件夹及其所有子文件夹
    for root, dirs, files in os.walk(root_folder):
        # 检查当前文件夹是否包含“哔哩哔哩视频”文件夹
        bilibili_folder = os.path.join(root, sub_folder_name)
        if os.path.exists(bilibili_folder):

            handled_files={}
            # 遍历“哔哩哔哩视频”文件夹中的所有文件和子文件夹
            for item in os.listdir(bilibili_folder):
                item_split=item.split(".")
                suffix=item_split[-1]
                dest_dir=root if suffix in ["mp4","srt","m4s"] else os.path.join(root,"弹幕")

                    
                    
                os.makedirs(dest_dir,exist_ok=True)
                org_path = os.path.join(bilibili_folder, item)
                dest_path=os.path.join(dest_dir,item)
                # 将文件或子文件夹移动到父文件夹中
                shutil.move(org_path, dest_path)

            
                
            # 删除“哔哩哔哩视频”文件夹
            os.rmdir(bilibili_folder)

    
    check_lost(root_folder)



      
def file_name(file_path):
    return file_path.split('.')[:-1]

def linux_path(file_path):
    org=str(os.path.normpath(file_path))
    return org.replace('\\','/')
    

def restore_classify_bullet(root_dir:str):
    
    
    bullet_path=os.path.join(root_dir,"弹幕")
    bullet_files=list(map(file_name,os.listdir(bullet_path)))
    bullet_names=list(map(lambda x:x[0],bullet_files))
    
    # 遍历根文件夹及其所有子文件夹
    for root, dirs, files in os.walk(root_dir):
        if os.path.normpath(root) == os.path.normpath(bullet_path):
            continue
        
        for file in files:
            
            pure_name=file_name(file)[0]
            if not pure_name in bullet_names:
                continue

            cur_file_name= ".". join(bullet_files[bullet_names.index(pure_name)]  ) +".srt"
            org_path=linux_path(os.path.join(bullet_path,cur_file_name)) 
            if  not os.path.exists(org_path):
                continue
            new_path=os.path.join(root,cur_file_name)
            print(new_path)
            # print(org_path,new_path)
            shutil.move(org_path,new_path)

                
       
def remove_leading_spaces(directory):
    # 遍历指定目录下的所有文件
    for root, dirs, files in os.walk(directory):
        for filename in files:
            new_filename=filename.strip()
            if filename!=new_filename:
                # 构建完整的文件路径
                old_file_path = os.path.join(root, filename)
                new_file_path = os.path.join(root, new_filename)
                # 重命名文件
                os.rename(old_file_path, new_file_path)
                print(f"Renamed '{filename}' to '{new_filename}'")



        
    
    
    
    
    
if __name__ == '__main__':

    root_dir=r'F:\教程\C++\双笙子佯谬'
    html_str='''
        <div data-v-493154f0="" class="channel-list clearfix"><!----><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/6da540ad825c94c87d110feaccf73f376152bdda.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/6da540ad825c94c87d110feaccf73f376152bdda.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/6da540ad825c94c87d110feaccf73f376152bdda.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">4</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·一步步把Vim打造成IDE" class="channel-name">
        合集·一步步把Vim打造成IDE
        </h4><div data-v-493154f0="" class="channel-update-time">
        昨天
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/3220ffe219cadd8a1b205053df37df94ca9252d3.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/3220ffe219cadd8a1b205053df37df94ca9252d3.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/3220ffe219cadd8a1b205053df37df94ca9252d3.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">52</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·现代C++项目实战" class="channel-name">
        合集·现代C++项目实战
        </h4><div data-v-493154f0="" class="channel-update-time">
        8-24
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/c9e96fbb149be2b6162970dc2273cd2bad6818e3.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/c9e96fbb149be2b6162970dc2273cd2bad6818e3.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/c9e96fbb149be2b6162970dc2273cd2bad6818e3.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">21</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·高性能并行编程与优化 - 录播" class="channel-name">
        合集·高性能并行编程与优化 - 录播
        </h4><div data-v-493154f0="" class="channel-update-time">
        8-4
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/cafd1bbcb86aade11b6e0459635d9cd4ac2bd834.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/cafd1bbcb86aade11b6e0459635d9cd4ac2bd834.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/cafd1bbcb86aade11b6e0459635d9cd4ac2bd834.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">4</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·SIMD优化专题课" class="channel-name">
        合集·SIMD优化专题课
        </h4><div data-v-493154f0="" class="channel-update-time">
        2023-8-21
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/eb37f762c0f61ad7e4e3f4a314d255cfde5f97d6.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/eb37f762c0f61ad7e4e3f4a314d255cfde5f97d6.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/eb37f762c0f61ad7e4e3f4a314d255cfde5f97d6.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">2</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·Zeno开发环境搭建指南" class="channel-name">
        合集·Zeno开发环境搭建指南
        </h4><div data-v-493154f0="" class="channel-update-time">
        2023-8-2
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/84de777409aa712d980f319633e950868e93a222.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/84de777409aa712d980f319633e950868e93a222.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/84de777409aa712d980f319633e950868e93a222.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">11</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·Zeno宣传片合集" class="channel-name">
        合集·Zeno宣传片合集
        </h4><div data-v-493154f0="" class="channel-update-time">
        2023-3-7
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/331a3a2c372536f266c6cf427912e75b60c2dbcd.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/331a3a2c372536f266c6cf427912e75b60c2dbcd.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/331a3a2c372536f266c6cf427912e75b60c2dbcd.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">2</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·小彭老师自制以撒mod系列" class="channel-name">
        合集·小彭老师自制以撒mod系列
        </h4><div data-v-493154f0="" class="channel-update-time">
        2023-1-28
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/7e30cbba74c4cb1c171ff20f1d16227539bcccc2.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/7e30cbba74c4cb1c171ff20f1d16227539bcccc2.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/7e30cbba74c4cb1c171ff20f1d16227539bcccc2.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">12</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·Zeno 新版教程" class="channel-name">
        合集·Zeno 新版教程
        </h4><div data-v-493154f0="" class="channel-update-time">
        2022-10-20
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//archive.biliimg.com/bfs/archive/46868cd67614af423b97849120f02d5732eb1413.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//archive.biliimg.com/bfs/archive/46868cd67614af423b97849120f02d5732eb1413.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//archive.biliimg.com/bfs/archive/46868cd67614af423b97849120f02d5732eb1413.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">10</span><em data-v-493154f0="" class="iconfont icon-heji"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="合集·Zeno 系列教程" class="channel-name">
        合集·Zeno 系列教程
        </h4><div data-v-493154f0="" class="channel-update-time">
        2022-2-26
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//i1.hdslb.com/bfs/archive/fa337d1a98bd1abaee6ee135b8f8ece173d7b61c.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//i1.hdslb.com/bfs/archive/fa337d1a98bd1abaee6ee135b8f8ece173d7b61c.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//i1.hdslb.com/bfs/archive/fa337d1a98bd1abaee6ee135b8f8ece173d7b61c.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">30</span><em data-v-493154f0="" class="iconfont icon-ic_channel1"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="Zeno" class="channel-name">
        Zeno
        </h4><div data-v-493154f0="" class="channel-update-time">
        2023-8-2
        </div></div></div><div data-v-493154f0="" class="channel-item"><div data-v-493154f0="" class="cover"><div data-v-493154f0="" class="b-img"><picture class="b-img__inner"><source type="image/avif" srcset="//i0.hdslb.com/bfs/archive/e606ad971c0c372b10a1f461cb4c08a727bbc156.jpg@320w_200h_1c_!web-space-channel-video.avif"><source type="image/webp" srcset="//i0.hdslb.com/bfs/archive/e606ad971c0c372b10a1f461cb4c08a727bbc156.jpg@320w_200h_1c_!web-space-channel-video.webp"><img src="//i0.hdslb.com/bfs/archive/e606ad971c0c372b10a1f461cb4c08a727bbc156.jpg@320w_200h_1c_!web-space-channel-video.webp" loading="lazy" onload="bmgOnLoad(this)" onerror="bmgOnError(this)" data-onload="bmgCmptOnload" data-onerror="bmgCmptOnerror"></picture></div><div data-v-493154f0="" class="video-num"><span data-v-493154f0="">10</span><em data-v-493154f0="" class="iconfont icon-ic_channel1"></em></div></div><span data-v-493154f0="" class="playall"><i data-v-493154f0="" class="iconfont icon-bofang"></i></span><div data-v-493154f0="" class="channel-meta"><h4 data-v-493154f0="" title="Taichi" class="channel-name">
        Taichi
        </h4><div data-v-493154f0="" class="channel-update-time">
        2022-9-7
        </div></div></div></div>
    '''
    # make_dir_from_html(html_str,root_dir)
    move_bilibili_folders(root_dir,"哔哩哔哩视频")

    # check_lost(root_dir)