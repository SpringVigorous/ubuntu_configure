

import os
from pathlib import Path
from path_tools import normal_path,windows_path
from com_exe_path import ffmpeg_path
import subprocess

from com_log import logger_helper,UpdateTimeType

def merge_video(temp_paths,dest_path):
    if not temp_paths or not dest_path:
        return

    temp_file= windows_path(os.path.join(Path(temp_paths[0]).parent,'file_list.txt'))
    merge_logger= logger_helper("合并视频",f"{temp_file} -> {dest_path}")
    merge_logger.trace("开始")
    # 创建一个文件列表文件
    with open(temp_file, 'w') as file:
        for temp_path in temp_paths:
            file.write(f"file {windows_path(temp_path)}\n")

    # 使用 FFmpeg 合并文件

    command = [ffmpeg_path(),'-y', '-f', 'concat', '-safe', '0', '-i', temp_file, '-c', 'copy', dest_path]
    # subprocess.run(command, check=True)
    # 运行命令并获取返回值
    result = subprocess.run(command, capture_output=True, text=True)



    # 获取标准输出和标准错误
    stdout = result.stdout
    stderr = result.stderr
    if stderr:
        merge_logger.error("失败",stderr,update_time_type=UpdateTimeType.ALL)
    if stdout:
        merge_logger.info("成功",stdout,update_time_type=UpdateTimeType.ALL)




    # 清理临时文件
    # for temp_path in temp_paths:
    #     os.remove(temp_path)   

    # os.remove(temp_file)