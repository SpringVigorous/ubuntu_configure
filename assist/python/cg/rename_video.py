import os
import re

def rename_special_suffix_files_in_directory(directory,flag):
    # 定义正则表达式模式，匹配以 -split 或 _split 结尾的文件名
    
    
    pattern = re.compile(r'(?P<name>.+?)'+f'(?:{flag})'+r'\.(?P<ext>\w+)$')
    
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            # 构造新的文件名
            new_filename = f"{match.group('name')}.{match.group('ext')}"
            old_file_path = os.path.join(directory, filename)
            new_file_path = os.path.join(directory, new_filename)
            
            # 重命名文件
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {old_file_path} -> {new_file_path}")

def add_rename_files_in_directory(directory):
    # 遍历目录中的所有文件
    
    filenames =[filename for filename in os.listdir(directory) if not filename.endswith(".bat")] 
    fakes=[]
    normals=[]
    for index,filename in enumerate(filenames):
        # 构造新的文件名
        new_filename = f"数据-{index+1:02}.db"

        
        fakes.append(f'ren "{filename}" "{new_filename}"')
        normals.append(f'ren "{new_filename}" "{filename}"')

    print("\n".join(fakes))
    print("-"*50)
    print("\n".join(normals))

def extract_ren_commands(text):
    # 定义正则表达式模式，匹配 ren "X" "Y" 格式的条目
    pattern = re.compile(r'ren\s+"([^"]+)"\s+"([^"]+)"')
    
    # 查找所有匹配的条目
    matches = pattern.findall(text)
    
    # 提取并返回 X 和 Y 的值
    extracted_pairs = [(x, y) for x, y in matches]
    return extracted_pairs
def is_fake(name):
    pattern = re.compile(r'数据-\d{2}\.db')
    return bool(pattern.match(name))
    
    
def restore_names():
    old_operate="""
        ren "3D肉蒲团-极乐宝典.mp4" "数据-01.db"
        ren "3D肉蒲团.mp4" "数据-02.db"
        ren "Anjelica-Burn My Passion.mp4" "数据-03.db"
        ren "Anjelica-[18OnlyGirls]-(2012)-Hardcore Tricks.mp4" "数据-04.db"
        ren "Anjelica-[DDFnetwork]-(2012)-Deserving An A For Anal.mp4" "数据-05.db"
        ren "SKYHD-029.720p.BluRay.x264-CrMo.mkv" "数据-06.db"
        ren "xart.14.05.11.the.red.fox.rope.priorities.mp4" "数据-07.db"
        ren "[X-Art] Jessica-Model Couple (1080p).mp4" "数据-08.db"
        ren "[X-Art] Veronica-The Young and The Restless (1080p).mp4" "数据-09.db"
        ren "[港台]一龙二凤乱伦悲剧之警钟.mp4" "数据-10.db"
        ren "一路向西.mp4" "数据-11.db"
        ren "丰满的应招女.rmvb" "数据-12.db"
        ren "交换工作_漂亮的女性员工.mp4" "数据-13.db"
        ren "全方位性爱观察_性爱观.mp4" "数据-14.db"
        ren "印度密宗.mp4" "数据-15.db"
        ren "印度密宗.srt" "数据-16.db"
        ren "印度密宗_导读.docx" "数据-17.db"
        ren "善良的妻子.mp4" "数据-18.db"
        ren "四大名捕之入梦妖灵.mp4" "数据-19.db"
        ren "団地妻の秘密-菜穂23歳.mp4" "数据-20.db"
        ren "女员工_2对2性爱.mp4" "数据-21.db"
        ren "性爱寄宿家庭_轮流性爱.mp4" "数据-22.db"
        ren "性福汤屋.mp4" "数据-23.db"
        ren "波多野结衣之人妻性奴隶.mp4" "数据-24.db"
        ren "波多野结衣之双飞调教.mp4" "数据-25.db"
        ren "波多野结衣之忆青春飘逝.mp4" "数据-26.db"
        ren "波多野结衣之慾乱上班族.mp4" "数据-27.db"
        ren "波多野结衣之慾望金鱼妻.mp4" "数据-28.db"
        ren "波多野结衣之无法抗拒.mp4" "数据-29.db"
        ren "波多野结衣之窥视情人.mp4" "数据-30.db"
        ren "波多野结衣之裸露快感.mp4" "数据-31.db"
        ren "破处门_1.flv" "数据-32.db"
        ren "立花里子-女佣-02.wmv" "数据-33.db"
        ren "立花里子-白衣护士.wmv" "数据-34.db"
        ren "老婆的姐姐.mp4" "数据-35.db"
        ren "金瓶梅2008.mp4" "数据-36.db"
        ren "金瓶梅II爱的奴隶.mp4" "数据-37.db"
        ren "隔壁的呻吟声.mp4" "数据-38.db"
    """

    new_operate="""
    ren "[港台]一龙二凤乱伦悲剧之警钟.mp4" "数据-01.db"
    ren "一路向西.mp4" "数据-02.db"
    ren "交换工作_漂亮的女性员工.mp4" "数据-03.db"
    ren "全方位性爱观察_性爱观.mp4" "数据-04.db"
    ren "善良的妻子.mp4" "数据-05.db"
    ren "団地妻の秘密-菜穂23歳.mp4" "数据-06.db"
    ren "性爱寄宿家庭_轮流性爱.mp4" "数据-07.db"
    ren "性福汤屋.mp4" "数据-08.db"
    ren "数据-01.db" "数据-09.db"
    ren "数据-02.db" "数据-10.db"
    ren "数据-03.db" "数据-11.db"
    ren "数据-04.db" "数据-12.db"
    ren "数据-05.db" "数据-13.db"
    ren "数据-06.db" "数据-14.db"
    ren "数据-07.db" "数据-15.db"
    ren "数据-08.db" "数据-16.db"
    ren "数据-09.db" "数据-17.db"
    ren "数据-12.db" "数据-18.db"
    ren "数据-15.db" "数据-19.db"
    ren "数据-16.db" "数据-20.db"
    ren "数据-17.db" "数据-21.db"
    ren "数据-19.db" "数据-22.db"
    ren "数据-21.db" "数据-23.db"
    ren "数据-25.db" "数据-24.db"
    ren "数据-26.db" "数据-25.db"
    ren "数据-27.db" "数据-26.db"
    ren "数据-28.db" "数据-27.db"
    ren "数据-29.db" "数据-28.db"
    ren "数据-30.db" "数据-29.db"
    ren "数据-31.db" "数据-30.db"
    ren "数据-32.db" "数据-31.db"
    ren "数据-34.db" "数据-32.db"
    ren "数据-35.db" "数据-33.db"
    ren "数据-36.db" "数据-34.db"
    ren "数据-38.db" "数据-35.db"
    ren "数据-39.db" "数据-36.db"
    ren "老婆的姐姐.mp4" "数据-37.db"
    ren "隔壁的呻吟声.mp4" "数据-38.db"
    """

    old_dict={key:val   for key,val in extract_ren_commands(old_operate)}
    old_reverse_dict={val:key for key,val in old_dict.items()}
    new_dict={key:val   for key,val in extract_ren_commands(new_operate)}
    new_reverse_dict={val:key for key,val in new_dict.items()}
    
    real_dict={}
    
    for key,val in new_dict.items():
        if is_fake(key):
            if val in real_dict:
                print(val)
            real_dict[val]=old_reverse_dict.get(key,"未知")
        else:
            real_dict[key]=val
    # print( "\n".join(f"{key} -> {val}" for key,val in real_dict.items()))
    
    for key,_ in old_dict.items():
        print(key)


if __name__ == "__main__":
    target_directory = r"F:\数据库"
    # rename_special_suffix_files_in_directory(target_directory,"-split|_split")
    add_rename_files_in_directory(target_directory)
    # restore_names()