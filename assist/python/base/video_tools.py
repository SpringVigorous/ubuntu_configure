

import os
from pathlib import Path
from path_tools import normal_path
from com_exe_path import ffmpeg_path
import subprocess

def merge_video(temp_paths,dest_path):
    if not temp_paths or not dest_path:
        return
    
    
    temp_file= normal_path(os.path.join(Path(temp_paths[0]).parent,'file_list.txt'))
    
    # 创建一个文件列表文件
    with open(temp_file, 'w') as file:
        for temp_path in temp_paths:
            file.write(f"file {temp_path}\n")
    
    # 使用 FFmpeg 合并文件

    command = [ffmpeg_path(), '-f', 'concat', '-safe', '0', '-i', temp_file, '-c', 'copy', dest_path]
    subprocess.run(command, check=True)

    print(f"Merged video saved as {dest_path}")

    # 清理临时文件
    # for temp_path in temp_paths:
    #     os.remove(temp_path)   

    os.remove(temp_file)