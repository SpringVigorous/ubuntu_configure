import os
import shutil
from pathlib import Path

def organize_files_with_complex_rules(directory_a, real_move=False):
    """
    按照复杂规则整理目录A中的文件
    
    参数:
        directory_a: 要整理的源目录
        real_move: 如果为False只打印操作，为True则实际执行
    """
    # 验证目录存在
    if not os.path.exists(directory_a):
        print(f"错误: 目录 {directory_a} 不存在")
        return
    
    # 创建目标子目录
    subdirs = ['xlsx', 'html', 'audio']
    for subdir in subdirs:
        target_dir = os.path.join(directory_a, subdir)
        if real_move and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"创建目录: {target_dir}")
    
    # 步骤1: 获取所有文件列表B（包含相对路径）
    file_list_b = []
    for root, dirs, files in os.walk(directory_a):
        for file in files:
            # 跳过我们创建的目标目录中的文件
            if any(subdir in root for subdir in subdirs):
                continue
            relative_path = os.path.relpath(os.path.join(root, file), directory_a)
            file_list_b.append((os.path.join(root, file), relative_path, file))
    
    print(f"找到 {len(file_list_b)} 个需要处理的文件")
    
    # 步骤2: 处理 .mp4 和 .m4a 文件 -> audio目录
    print("\n=== 处理音频文件 ===")
    audio_extensions = {'.mp4', '.m4a',".acc"}
    for full_path, relative_path, filename in file_list_b:
        file_ext = Path(filename).suffix.lower()
        if file_ext in audio_extensions:
            # 保留相对路径层次结构
            target_path = os.path.join(directory_a, 'audio', relative_path)
            target_dir = os.path.dirname(target_path)
            
            if real_move:
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(full_path, target_path)
                print(f"移动音频文件: {relative_path} -> audio/{relative_path}")
            else:
                print(f"[模拟] 移动音频文件: {relative_path} -> audio/{relative_path}")
    
    # 重新获取文件列表（因为已经移动了一些文件）
    if real_move:
        file_list_b = []
        for root, dirs, files in os.walk(directory_a):
            if any(subdir in root for subdir in subdirs):
                continue
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), directory_a)
                file_list_b.append((os.path.join(root, file), relative_path, file))
    
    # 步骤3: 处理 .xlsx 文件（复杂规则）
    print("\n=== 处理Excel文件 ===")
    xlsx_files_to_process = []
    
    for full_path, relative_path, filename in file_list_b:
        if filename.lower().endswith('.xlsx'):
            # 排除已经在xlsx目录和catalog.xlsx文件
            if 'xlsx' not in relative_path.split(os.sep) and filename != 'catalog.xlsx':
                xlsx_files_to_process.append((full_path, relative_path, filename))
    
    for full_path, relative_path, filename in xlsx_files_to_process:
        # 解析路径结构：去掉直接父目录
        path_parts = relative_path.split(os.sep)
        if len(path_parts) > 2:  # 有子目录结构
            # 去掉直接父目录，保留祖父目录
            new_relative = os.sep.join(path_parts[:-2] + [filename])
            
            cur_path=Path(filename)
            if  "_album" in cur_path.stem:
                new_filename=cur_path
            else :
                new_filename=cur_path.with_stem(f"{cur_path.stem}_album")
            
            
            
            new_filename = str(new_filename)
            target_path = os.path.join(directory_a, 'xlsx', new_relative)
            target_path = target_path.replace(filename, new_filename)
            
            # 原父目录路径（用于后续删除）
            parent_dir = os.path.dirname(full_path)
            
            if real_move:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(full_path, target_path)
                print(f"移动并重命名Excel文件: {relative_path} -> xlsx/{new_relative}")
                
                # 删除原父目录（如果为空）
                try:
                    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                        print(f"删除空目录: {parent_dir}")
                except OSError as e:
                    print(f"无法删除目录 {parent_dir}: {e}")
            else:
                print(f"[模拟] 移动并重命名Excel文件: {relative_path} -> xlsx/{new_relative}")
                print(f"[模拟] 会删除空目录: {parent_dir}")
    
    # 重新获取文件列表
    if real_move:
        file_list_b = []
        for root, dirs, files in os.walk(directory_a):
            if any(subdir in root for subdir in subdirs):
                continue
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), directory_a)
                file_list_b.append((os.path.join(root, file), relative_path, file))
    
    # 步骤4: 特殊处理catalog.xlsx和_album.xlsx文件
    print("\n=== 处理特殊Excel文件 ===")
    for full_path, relative_path, filename in file_list_b:
        # 拷贝catalog.xlsx到xlsx目录
        if filename == 'catalog.xlsx':
            target_path = os.path.join(directory_a, 'xlsx', filename)
            if real_move:
                shutil.copy2(full_path, target_path)
                print(f"拷贝catalog.xlsx到xlsx目录")
            else:
                print(f"[模拟] 拷贝catalog.xlsx到xlsx目录")
        
        # 移动以_album.xlsx结尾的文件到xlsx目录，并去掉_album
        elif filename.endswith('_album.xlsx'):
            new_filename = filename.replace('_album.xlsx', '.xlsx')
            target_path = os.path.join(directory_a, 'xlsx', new_filename)
            
            if real_move:
                shutil.move(full_path, target_path)
                print(f"移动并重命名: {filename} -> {new_filename}")
            else:
                print(f"[模拟] 移动并重命名: {filename} -> {new_filename}")
    
    # 重新获取文件列表
    if real_move:
        file_list_b = []
        for root, dirs, files in os.walk(directory_a):
            if any(subdir in root for subdir in subdirs):
                continue
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), directory_a)
                file_list_b.append((os.path.join(root, file), relative_path, file))
    
    # 步骤5: 处理 .html 文件
    print("\n=== 处理HTML文件 ===")
    for full_path, relative_path, filename in file_list_b:
        if filename.lower().endswith('.html'):
            target_path = os.path.join(directory_a, 'html', relative_path)
            target_dir = os.path.dirname(target_path)
            
            if real_move:
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(full_path, target_path)
                print(f"移动HTML文件: {relative_path} -> html/{relative_path}")
            else:
                print(f"[模拟] 移动HTML文件: {relative_path} -> html/{relative_path}")
    
    print("\n=== 操作完成 ===")
    if not real_move:
        print("注意: 当前为模拟模式，未实际执行文件操作")
        print("要实际执行，请设置 real_move=True")

def preview_directory_structure(directory):
    """预览目录结构"""
    print("目录结构预览:")
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

# 使用示例
if __name__ == "__main__":
    # 设置您的目录A路径
    directory_a = r"E:\旭尧\有声读物"  # 请替换为实际路径
    
    # 首先预览目录结构
    preview_directory_structure(directory_a)
    
    print("\n" + "="*50)
    print("开始文件归类操作")
    print("="*50)
    
    # 先进行模拟运行（不实际移动文件）
    print("=== 模拟运行 ===")
    organize_files_with_complex_rules(directory_a, real_move=True)
    
    # 确认无误后，取消注释下面的代码进行实际操作
    # print("\n" + "="*50)
    # print("开始实际文件操作")
    # print("="*50)
    # organize_files_with_complex_rules(directory_a, real_move=True)