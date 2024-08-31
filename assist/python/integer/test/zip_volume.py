import os
import zipfile
from collections import defaultdict

def get_folder_size(folder):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def create_zip_file(output_filename, source_dir,dir_list):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        cur_dir=os.path.dirname(source_dir)
        dir_list.append(cur_dir)
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, cur_dir)
                zipf.write(file_path, arcname)

def pack_folders_into_zips(folders, max_size=100 * 1024 * 1024):
    # 创建一个字典来存储文件夹及其大小
    folder_sizes = {folder: get_folder_size(folder) for folder in folders}
    
    # 创建一个字典来存储压缩包及其当前大小
    zip_files = defaultdict(int)

    # 按文件夹大小排序，从大到小
    sorted_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)

    for folder, size in sorted_folders:
        added = False
        dir_list=[]
        # 尝试将文件夹添加到已有的压缩包中
        for zip_name, current_size in zip_files.items():
            if current_size + size <= max_size:
                pass

def pack_folders_into_zips(directory):
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        if os.path.isdir(folder_path):
            output_filename = os.path.join(os.path.dirname(directory),"zip", f"{folder_name}.zip")
            create_zip_file(output_filename, folder_path)
            print(f"Created {output_filename}")

if __name__ == '__main__':
    directory_to_pack = "E:/新建文件夹/2024-8-9ZEUGLODON/原图"  # 替换为你的目录路径
    pack_folders_into_zips(directory_to_pack)
