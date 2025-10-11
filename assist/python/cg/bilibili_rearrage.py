import os
import shutil
from base import logger_helper
import re

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


def rename_files_in_folder(folder_path,rename_func, recursive=False):
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
            
            if new_filename != filename:
                new_path = os.path.join(root, new_filename)
                
                # 检查新文件名是否已存在
                if os.path.exists(new_path):
                    logger.warn("跳过","已存在")
                    continue
                
                try:
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


if __name__ == "__main__":
    # 根目录路径
    root_directory = r"E:\旭尧"
    # def rename_num_count_fun(name:str):
    #     return rename_file_basic(name,2)
    # rename_files_in_folder(root_directory,rename_num_count_fun,recursive=True) #重命名文件
    
    
    
    root_directory = r"E:\旭尧\叫叫识字大冒险"
    # rename_files_in_folder(root_directory,rename_file_remove_pre_num,recursive=True) #重命名文件
    
    def rename_remove_size_flag(name:str):
        return name.replace("-720P 准高清","")
    rename_files_in_folder(root_directory,rename_remove_size_flag,recursive=True) #重命名文件
    
    
    # process_bilibili_directories(root_directory) #整理文件

