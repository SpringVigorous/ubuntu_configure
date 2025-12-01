import os
import shutil
from base import logger_helper,worm_root,kid_root
import re
from pathlib import Path
def rename_file_basic(filename,num_len=2):
    """
    基本函数：重命名单个文件名
    如果文件名以数字开头，将数字格式化为两位（不足补0），然后与后续字符组合
    
    参数:
        filename: 原始文件名
    返回:
        重命名后的文件名，如果不符合条件则返回原文件名
    """
    # 使用正则表达式匹配以数字开头的文件名
    match = re.match(r'^(\d+)(.*)$', filename)
    
    if match:
        # 提取数字部分和剩余部分
        num_part = match.group(1)
        rest_part = match.group(2)
        
        try:
            # 将数字部分转换为整数
            number = int(num_part)
            # 格式化为两位数字字符串（不足补0）
            formatted_num = f"{number:0{num_len}d}"
            # 组合新文件名
            new_filename = f"{formatted_num}{rest_part}"
            return new_filename
        except ValueError:
            # 如果数字部分无法转换为整数，返回原文件名
            return filename
    else:
        # 如果文件名不以数字开头，返回原文件名
        return filename


def rename_file_remove_pre_num(filename):
    """
    基本函数：重命名单个文件名
    如果文件名以数字开头，将数字格式化为两位（不足补0），然后与后续字符组合
    
    参数:
        filename: 原始文件名
    返回:
        重命名后的文件名，如果不符合条件则返回原文件名
    """
    # 使用正则表达式匹配以数字开头的文件名
    match = re.match(r'^\d+ \d+-(.*)$', filename)
    
    if match:
        # 提取数字部分和剩余部分
        return match.group(1)


def rename_files_in_folder(folder_path,rename_func, recursive=False,real_replace=True):
    """
    加强版函数：处理文件夹中的所有文件
    对文件夹中的每个文件应用基本重命名函数
    
    参数:
        folder_path: 文件夹路径
        recursive: 是否递归处理子文件夹，默认为False
    返回:
        一个元组 (成功重命名的文件数, 总文件数)
    """
    success_count = 0
    total_count = 0
    logger=logger_helper(f"重命名文件{folder_path}")
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        logger.trace(f"错误：文件夹 '{folder_path}' 不存在")
        return (0, 0)
    
    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            total_count += 1
            old_path = os.path.join(root, filename)
            logger.raii_target(detail=f"处理文件: {old_path}")
            new_filename = rename_func(filename)
            if not new_filename: 
                continue
            if new_filename != filename:
                new_path = os.path.join(root, new_filename)
                
                # 检查新文件名是否已存在
                if os.path.exists(new_path):
                    logger.warn("跳过","已存在")
                    continue
                
                try:
                    if real_replace:
                        os.rename(old_path, new_path)
                    success_count += 1
                    logger.trace("完成",f" '{filename}' -> '{new_filename}'")
                except Exception as e:
                    logger.error("失败", f"{str(e)}")
        
        # 如果不递归处理子文件夹，只处理当前目录后就退出
        if not recursive:
            break
    
    return (success_count, total_count)
def process_bilibili_directories(root_dir):
    """
    处理根目录下的子目录，按规则移动视频和字幕文件并修改目录名
    
    参数:
        root_dir: 根目录路径
    """
    
    logger=logger_helper(f"整理视频文件{root_dir}")
    
    # 检查根目录是否存在
    if not os.path.exists(root_dir):
        logger.warn("不存在",f"错误: 根目录 '{root_dir}' 不存在")
        return
    
    # 遍历根目录下的所有子目录
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        
        # 确保是目录
        if not os.path.isdir(subdir_path):
            continue
            
        # 检查是否存在"哔哩哔哩视频"子目录
        bilibili_dir = os.path.join(subdir_path, "哔哩哔哩视频")
        if os.path.exists(bilibili_dir) and os.path.isdir(bilibili_dir):
            with logger.raii_target(detail=f"处理目录: {subdir_path}"):
                logger.trace("开始")
                try:
                    # 定义所需的目标目录
                    src_zh_dir = os.path.join(subdir_path, "src-zh")
                    src_en_dir = os.path.join(subdir_path, "src-en")
                    mp4_dir = os.path.join(subdir_path, "mp4")
                    
                    # 移动文件到相应位置
                    for filename in os.listdir(bilibili_dir):
                        file_path = os.path.join(bilibili_dir, filename)
                        
                        # 只处理文件，不处理子目录
                        if os.path.isfile(file_path):
                            # 获取文件扩展名
                            ext = os.path.splitext(filename)[1].lower()
                            
                            # 只处理.mp4和.srt文件
                            if ext in ('.mp4', '.srt'):
                                # 处理文件名和目标目录
                                new_filename = filename
                                dest_dir = subdir_path  # 默认目标目录
                                
                                # 处理srt字幕文件
                                if ext == '.srt':
                                    # 处理包含.ai-zh的中文字幕
                                    if '.ai-zh' in new_filename or '.zh-Hans' in new_filename:
                                        new_filename = new_filename.replace('.ai-zh', '').replace('.zh-Hans', '')
                                        dest_dir = src_zh_dir
                                        logger.trace(f"处理中文字幕: {filename} -> {new_filename} (移至src-zh)")
                                    
                                    # 处理包含.ai-en的英文字幕
                                    elif '.ai-en' in new_filename:
                                        new_filename = new_filename.replace('.ai-en', '')
                                        dest_dir = src_en_dir
                                        logger.trace(f"处理英文字幕: {filename} -> {new_filename} (移至src-en)")

                                
                                # 处理mp4视频文件
                                elif ext == '.mp4':
                                    dest_dir = mp4_dir
                                    logger.trace(f"处理视频文件: {filename} (移至mp4)")
                                
                                # 构建目标路径
                                dest_path = os.path.join(dest_dir, new_filename)
                                

                                
                                # 确保目标目录存在
                                if not os.path.exists(dest_dir):
                                    os.makedirs(dest_dir)

                                
                                # 移动文件
                                shutil.move(file_path, dest_path)
                                logger.trace("完成",f"{file_path} -> {dest_path}")
                    
                    # 重命名"哔哩哔哩视频"目录为"ass"
                    new_dir_name = os.path.join(subdir_path, "ass")

                    if bilibili_dir==new_dir_name:
                        continue
                    os.rename(bilibili_dir, new_dir_name)
                    logger.trace(f"目录重命名: {bilibili_dir}->{new_dir_name}")
                    
                except Exception as e:
                    logger.trace(f"处理目录时出错: {str(e)}\n")
    
#针对 怪物数学小分队/怪物数学小分队中文版第1集乌菲散步-国语720P.【www.oiabc.com】.mp4
def rename_file_only_math(filename:str):
    # 使用正则表达式匹配文件名模式
    match = re.search(r'第(\d+)集([^.-]+)', filename)
    
    if match:
        # 提取集数和标题
        episode_num = int(match.group(1))
        title = match.group(2).strip()
        
        # 格式化集数为两位数
        formatted_episode = f"{episode_num:02d}"
        
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        
        # 构建新文件名
        new_filename = f"{formatted_episode}_{title}{ext}"
        return new_filename

#01 第1集 ABC Song 字母歌 美语版-1080P.mp4
def rename_file_only_english(filename:str):
    # 正则表达式匹配原文件名结构
    # 匹配规则：
    # ^(\d+)\s+第\d+集\s+：开头的序号（如01）+ 空格 + "第X集" + 空格
    # (.*?)\s+.*?-.*?\.mp4$：标题部分（到附加信息前）+ 空格 + 附加信息（如美语版-1080P）+ .mp4
    pattern = r'(\d+)\s+第\d+集\s+(.*)-1080P'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{episode_num}_{title}{Path(filename).suffix}"
    return new_filename
#01 01.自然拼读Lesson 1—ab.mp4  -> 01_ab.mp4
def rename_file_only_spell(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'(\d+)\s+.*?—(.*?)\.'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{episode_num}_{title}{Path(filename).suffix}"
    return new_filename

#“01 02. [Greeting] Good morning. How are you_ - Easy Dialogue - Role Play.mp44” 转换为 “02_[Greeting]_Good morning. How are you.mp4”
def rename_file_easy_dialog(filename:str):
    # 正则表达式匹配原文件名结构，提取关键部分
    # 匹配规则解析：
    # ^.*?\s+：跳过开头冗余前缀（如"01 "，非贪婪匹配到第一个空格）
    # (\d+)\.\s+：匹配目标序号（如"02. "，捕获数字部分"02"）
    # \[(.*?)\]\s+：匹配带[]的标签（如"[Greeting] "，捕获标签内容"Greeting"，保留中括号结构）
    # (.*?)_ -：匹配核心标题（如"Good morning. How are you"，到"_ -"前结束，捕获标题）
    # .*?\.mp44$：匹配末尾冗余内容和错误后缀（如" Easy Dialogue - Role Play.mp44"，不捕获）
    pattern = r'.*?\s+(\d+)\.\s+\[(.*?)\]\s+(.*?) English Dialogue  - Role-play (.*?)\.'
    match = re.match(pattern, filename)
    match = re.search(pattern, filename)
    logger=logger_helper(filename,f"正则表达式:\n{pattern}")
    if not match:
        logger.debug("失败",f"文件名格式不匹配，跳过")
        return

    
    # 提取序号、标签内容、核心标题
    episode_num = match.group(1)  # 序号（如"02"）
    tag = match.group(2)          # 标签内容（如"Greeting"）
    title = match.group(3).strip()# 核心标题（如"Good morning. How are you"）
    latter = match.group(4).strip()
    
    # 处理空值情况（防止异常）
    if not all([episode_num, tag, title]):
        logger.debug("失败",f"提取信息不完整，跳过")
        return
    
    # 构建新文件名：序号_[标签]_标题.mp4（修正后缀为.mp4）
    new_filename = f"{episode_num}_{tag}_{title}_{latter}{Path(filename).suffix}"
    return new_filename

def fetch_from_log(log_file_path):
    """
    从.log文件中提取原文件路径和重命名后的路径
    :param log_file_path: .log文件的绝对路径或相对路径
    :return: 提取到的路径列表，每个元素为元组(原路径, 新路径)
    """
    # 正则表达式规则：
    # 1. 匹配原文件路径（处理文件: 后的绝对路径，以.srt结尾，到第一个逗号结束）
    # 2. 匹配重命名后的路径（-> ' 后的内容，以.mp4结尾，到'结束）
    pattern = r'【完成】详情：处理文件: (.*?),.*?-> \'(.*?)\''
    logger=logger_helper(f"处理日志文件：{log_file_path}",f"正则表达式:\n{pattern}")
    extracted = []
    try:
        # 读取日志文件内容
        with open(log_file_path, 'r', encoding='utf-8-sig') as f:
            log_content = f.read()
        
        # 查找所有匹配的内容（支持一行多个或多行多个）
        matches = re.findall(pattern, log_content, re.DOTALL)
        
        for match in matches:
            original_path = match[0].strip()  # 原路径（.srt文件）
            new_path = match[1].strip()       # 新路径（.mp4文件）
            
            cur_path=Path(original_path)
            dest_path=Path(new_path)
            
            extracted.append({"org_path":original_path, "new_name":new_path,"new_path":cur_path.parent/new_path,"same_suffix":cur_path.suffix==dest_path.suffix})

        

    
    except FileNotFoundError:
        logger.error("异常",f"错误：文件不存在 → {log_file_path}")
    except Exception as e:
        logger.error("异常",f"处理失败：{str(e)}")
    import pandas as pd
    df=pd.DataFrame(extracted)
    # df.to_excel(Path(log_file_path).with_suffix(".xlsx"))
    return df
import pandas as pd
from base import df_empty

def correct_suffix_error(df:pd.DataFrame):
    logger=logger_helper("回滚——重命名后缀错误")
    suffix_errors_df=df[~df["same_suffix"]]
    if  df_empty(suffix_errors_df):
        return 
    for index, row in suffix_errors_df.iterrows():
        org_path=row["org_path"]
        old_path=row["new_path"]
        new_path=Path(old_path).with_suffix(Path(org_path).suffix)
        if not os.path.exists(org_path):
            continue
        os.rename(old_path, new_path)
        logger.trace("完成",f" '{old_path}' -> '{new_path}'")

def correct_lose_prefix(df):
    logger=logger_helper("回滚——重命名删除前缀错误")
    prefix_df=df[df["org_path"].str.contains(kid_root\r"英语_儿童日常对话",regex=False)]
    if  df_empty(prefix_df):
        return 
    for index, row in prefix_df.iterrows():
        org_path=Path(row["org_path"])
        old_path=Path(row["new_path"])
        
        
        org_math=re.search(r"\[(.*?)\]",org_path.name)
        new_math=re.search(r"\d{2}_[^_]+_[^_]+\.",old_path.name)
        if not org_math or  new_math:
            continue
        
        if not os.path.exists(old_path):
            continue
        os.rename(old_path, org_path)
        logger.trace("完成",f" '{old_path}' -> '{org_path}'")
    pass
def correct_file_name(xlsx_path:str):
    
   
    df =pd.read_excel(xlsx_path)
    correct_suffix_error(df)
    correct_lose_prefix(df)


#01 第1集 ABC Song 字母歌 美语版-1080P.mp4
def rename_file_double_num_prefix(filename:str):
    # 正则表达式匹配原文件名结构
    # 匹配规则：
    # ^(\d+)\s+第\d+集\s+：开头的序号（如01）+ 空格 + "第X集" + 空格
    # (.*?)\s+.*?-.*?\.mp4$：标题部分（到附加信息前）+ 空格 + 附加信息（如美语版-1080P）+ .mp4
    pattern = r'\d+\s+(\d+)\s+(.*)'
    match = re.search(pattern, filename)
    
    if not match:
        match = re.search(r"(\d+)\s+(.*)", filename)
        
    if not match:
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    name = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not name.strip():
        return
    
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{int(episode_num):02d}_{name}"
    return new_filename

#02 1.【自然拼读洗脑歌曲】 字母A.mp4  -> 02_字母A.mp4
def rename_file_only_spell_rjb(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'\d+\s+(\d+)\.(.*)'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    title=title.replace("【自然拼读洗脑歌曲】","").strip()
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{int(episode_num):02d}_{title}"
    return new_filename

#01 01. Kids vocabulary - Sea Animals - Learn English for kids - English educational.mp4 -> 01_Sea Animals.mp4
def rename_file_only_spell_dh(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'\d+\s+(\d+)\.(.*)'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    titles=title.split("-")
    
    def find_index(titles,keys):
        for index,title in enumerate(titles):
            for key in keys:
                if key in title:
                    return index

    if len(titles)>3:
        
        last_index=find_index(titles,["Learn English",'Learn Engl','English edu',"English",'educational','Lear','Engl'])
        
        title='-'.join(map(lambda x: x.strip() ,titles[1:last_index]))
    else:
        return
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{int(episode_num):02d}_{title}{Path(filename).suffix}"
    return new_filename

#'26 Alphabet Z Sound Song l Phonics for English Education.srt' -> '26_Z.srt'
def rename_file_only_spell_fy(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'(\d+)\s+Alphabet (.*?) Sound Song'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{int(episode_num):02d}_{title}{Path(filename).suffix}"
    return new_filename
#'02 磨耳朵单词课—第一节：房子—house.mp4' -> '02_房子—house.mp4'
def rename_file_only_spell_med(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'(\d+)\s+.*第.*?节—(.*)'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{int(episode_num):02d}_{title}"
    return new_filename
#'01 01-人之初-蓝光4k.mp4' -> '01_人之初.mp4'
def rename_file_only_spell_szj(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'(\d+)\s+\d+(.*)'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    episode_num = match.group(1)  # 第一个分组：序号（01）
    title = match.group(2)        # 第二个分组：标题（ABC Song 字母歌）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    # 构建新文件名：序号_标题.mp4
    title=title.replace("-蓝光4k","")
    new_filename = f"{int(episode_num):02d}_{title}"
    return new_filename

#'正在播放爆笑虫子：荒岛求生记第01集全集___动漫___星辰剧集网.mp4' -> '荒岛求生记_01.mp4'
def rename_file_only_bxcz(filename:str):
    # 匹配规则解析：
    # ^(\d+)\s+：开头的序号（如01）+ 空格（捕获序号）
    # .*?—：中间的冗余内容（如"01.自然拼读Lesson 1"）+ "—"（非贪婪匹配，直到第一个"—"）
    # (.*?)\.mp4$："—"后面的目标字符（如ab）+ .mp4（捕获目标字符）
    # 注意：原文件名中的"—"是中文破折号，正则中需准确匹配
    pattern = r'正在播放爆笑虫子：(.*?)第(\d+)集'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）
    title = match.group(1)        # 第二个分组：标题（ABC Song 字母歌）
    episode_num = match.group(2)  # 第一个分组：序号（01）
    
    # 处理可能的空标题（防止异常）
    if not title.strip():
        return
    # 构建新文件名：序号_标题.mp4
    new_filename = f"{title}_{int(episode_num):02d}{Path(filename).suffix}"
    return new_filename


def rename_file_special_only(filename:str):

    cur_path=Path(filename)
    if cur_path.stem=="01 磨耳朵单词课，500个核心单词，469个常用句子，28幅导图，每天5分钟，轻松学词汇。适合3—12岁儿童。":
        return f"01_磨耳朵单词课，500个核心单词，469个常用句子，28幅导图，每天5分钟，轻松学词汇。适合3—12岁儿童{cur_path.suffix}"

def rename_file_only_quote(filename:str):
    pattern = r'《([^《》 ]+)》'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）

    title = match.group(1)        # 第二个分组：标题（ABC Song 字母歌）
    title=title.strip() if title else ""
    # 处理可能的空标题（防止异常）
    if not title:
        return

    new_filename = f"{title}{Path(filename).suffix}"
    return new_filename
def rename_file_only_bbbs(filename:str):
    pattern = r'：(.*)'
    match = re.search(pattern, filename)
    
    if not match:
        print(f"文件名格式不匹配，跳过：{filename}")
        return

    
    # 提取序号（如01）和标题（如ABC Song 字母歌）

    title = match.group(1)        # 第二个分组：标题（ABC Song 字母歌）


    new_filename = f"{title}"
    return new_filename

if __name__ == "__main__":
    

    
    
    rename_files_in_folder(worm_root/r"player\video",rename_file_only_bbbs,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()
    rename_files_in_folder(worm_root/r"player\video",rename_file_only_bxcz,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()
    rename_files_in_folder(worm_root/r"player\video",rename_file_only_quote,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()
    
    rename_files_in_folder(kid_root\r"磨耳朵单词课",rename_file_special_only,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    # rename_files_in_folder(kid_root\r"磨耳朵单词课",rename_file_only_spell_med,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()
    rename_files_in_folder(kid_root\r"三字经",rename_file_only_spell_szj,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()

    rename_files_in_folder(kid_root\r"自然拼读26个字母发音",rename_file_only_spell_fy,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()
    
    rename_files_in_folder(kid_root\r"幼小阶段看动画背单词磨耳朵",rename_file_only_spell_dh,recursive=True,real_replace=True) #重命名文件    # 根目录路径
    exit()
    rename_files_in_folder(kid_root\r"Hello Carrie 阶段一 26个字母的自然发音",rename_file_only_spell_rjb,recursive=True) #重命名文件    # 根目录路径
    exit()
    rename_files_in_folder(kid_root\r"英语_自然拼读动画",rename_file_double_num_prefix,recursive=True) #重命名文件    # 根目录路径
    
    exit()
    
    
    # df=fetch_from_log(worm_root/r"logs\bilibili_rearrage\bilibili_rearrage-trace.log")
    
    # correct_file_name(worm_root/r"logs\bilibili_rearrage\bilibili_rearrage-trace.xlsx")

    rename_files_in_folder(kid_root\r"英语_儿童日常对话",rename_file_easy_dialog,recursive=True) #重命名文件    # 根目录路径
    exit()
    rename_files_in_folder(kid_root\r"2025版_幼儿入门级自然拼读",rename_file_only_spell,recursive=True) #重命名文件    # 根目录路径
    

    
    rename_files_in_folder(kid_root\r"英语儿歌",rename_file_only_english,recursive=True) #重命名文件    # 根目录路径
    
    exit()
    rename_files_in_folder(kid_root\r"怪物数学小分队",rename_file_only_math,recursive=True) #重命名文件    # 根目录路径
    
    
    
    
    
    exit()
    
    root_directory = kid_root
    process_bilibili_directories(root_directory) #拆分 MP4 、srt 整理文件
    def rename_num_count_fun(name:str):
        return rename_file_basic(name,2)
    rename_files_in_folder(root_directory,rename_num_count_fun,recursive=True) #重命名文件
    
    exit()
    
    root_directory = kid_root\r"叫叫识字大冒险"
    # rename_files_in_folder(root_directory,rename_file_remove_pre_num,recursive=True) #重命名文件
    
    def rename_remove_size_flag(name:str):
        return name.replace("-720P 准高清","")
    rename_files_in_folder(root_directory,rename_remove_size_flag,recursive=True) #重命名文件
    
    

