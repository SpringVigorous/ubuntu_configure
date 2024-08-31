import os
import zipfile
from concurrent.futures import ThreadPoolExecutor

def create_zip_file(output_filename, source_dir):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)

def pack_folders_into_zips(directory):
    folders = [folder_name for folder_name in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder_name))]
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for folder_name in folders:
            folder_path = os.path.join(directory, folder_name)
            output_filename = os.path.join(os.path.dirname(directory),"zip", f"{folder_name}.zip")
            future = executor.submit(create_zip_file, output_filename, folder_path)
            futures.append(future)

        # 等待所有任务完成
        for future in futures:
            future.result()

if __name__ == '__main__':
    directory_to_pack = "E:/新建文件夹/2024-8-9ZEUGLODON/原图" # 替换为你的目录路径
    pack_folders_into_zips(directory_to_pack)