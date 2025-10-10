import os
import shutil

def process_bilibili_directories(root_dir):
    """
    处理根目录下的子目录，按规则移动视频和字幕文件并修改目录名
    
    参数:
        root_dir: 根目录路径
    """
    # 检查根目录是否存在
    if not os.path.exists(root_dir):
        print(f"错误: 根目录 '{root_dir}' 不存在")
        return
    
    # 遍历根目录下的所有子目录
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        
        # 确保是目录
        if not os.path.isdir(subdir_path):
            continue
            
        # 检查是否存在"哔哩哔哩视频"子目录
        bilibili_dir = os.path.join(subdir_path, "ass")
        if os.path.exists(bilibili_dir) and os.path.isdir(bilibili_dir):
            print(f"处理目录: {subdir_path}")
            
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
                                if '.ai-zh' in new_filename:
                                    new_filename = new_filename.replace('.ai-zh', '')
                                    dest_dir = src_zh_dir
                                    print(f"处理中文字幕: {filename} -> {new_filename} (移至src-zh)")
                                
                                # 处理包含.ai-en的英文字幕
                                elif '.ai-en' in new_filename:
                                    new_filename = new_filename.replace('.ai-en', '')
                                    dest_dir = src_en_dir
                                    print(f"处理英文字幕: {filename} -> {new_filename} (移至src-en)")

                            
                            # 处理mp4视频文件
                            elif ext == '.mp4':
                                dest_dir = mp4_dir
                                print(f"处理视频文件: {filename} (移至mp4)")
                            
                            # 构建目标路径
                            dest_path = os.path.join(dest_dir, new_filename)
                            

                            
                            # 确保目标目录存在
                            if not os.path.exists(dest_dir):
                                os.makedirs(dest_dir)
                                print(f"创建目录: {dest_dir}")
                            
                            # 移动文件
                            shutil.move(file_path, dest_path)
                            print(f"移动完成: {file_path} -> {dest_path}")
                
                # 重命名"哔哩哔哩视频"目录为"ass"
                new_dir_name = os.path.join(subdir_path, "ass")

                if bilibili_dir==new_dir_name:
                    continue
                os.rename(bilibili_dir, new_dir_name)
                print(f"目录重命名: {bilibili_dir}->{new_dir_name}")
                
            except Exception as e:
                print(f"处理目录时出错: {str(e)}\n")


if __name__ == "__main__":
    # 根目录路径
    root_directory = r"E:\旭尧"
    print(f"开始处理根目录: {root_directory}\n")
    process_bilibili_directories(root_directory)
    print("处理完成")
