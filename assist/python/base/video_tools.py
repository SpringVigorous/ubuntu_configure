

import os
from pathlib import Path
from path_tools import normal_path,windows_path
from com_exe_path import ffmpeg_path
import subprocess

from com_log import logger_helper,UpdateTimeType
import subprocess
from concurrent.futures import ThreadPoolExecutor
def get_all_files_pathlib(directory,include_suffix:list=None):
    """
    获取指定目录下的所有文件的全路径
    :param directory: 目标目录
    :return: 文件全路径列表
    """
    file_paths = []
    for file in Path(directory).rglob('*'):
        org_path=str(file.resolve())
        if include_suffix and not file.suffix in include_suffix:
            continue
        if file.is_file():
            file_paths.append(str(file.resolve()))
    return file_paths



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
    # result = subprocess.run(command, capture_output=True, text=True,encoding="utf-8",errors="ignore",check=True)
    result = subprocess.run(command, capture_output=True, text=True,errors="ignore",check=True)



    # 获取标准输出和标准错误
    stdout = result.stdout
    stderr = result.stderr
    if stderr:
        merge_logger.error("失败",stderr,update_time_type=UpdateTimeType.ALL)
    if stdout:
        merge_logger.info("成功",stdout,update_time_type=UpdateTimeType.ALL)

#转换文件
def convert_video_to_mp4(video_path,output_path=None):
    if not video_path or not os.path.exists(video_path):
        return
    
    if not output_path:
        org_path=Path(video_path)
        output_path = os.path.join(f"{org_path.parent}_output",org_path.stem + '.mp4')
        os.makedirs(os.path.dirname(output_path) ,exist_ok=True)
    if os.path.exists(output_path):
        return
    
    # 使用 ffmpeg 进行转换
    command = [
        'ffmpeg',
        '-i', video_path,  # 输入文件
        '-c:v', 'libx264',  # 视频编码器
        '-c:a', 'aac',      # 音频编码器
        output_path         # 输出文件
    ]
    
    try:
        # 执行命令
        subprocess.run(command, check=True)
        print(f"转换成功: {video_path} -> {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败: {video_path}")
        print(e)

    # 清理临时文件
    # for temp_path in temp_paths:
    #     os.remove(temp_path)   

    # os.remove(temp_file)

def convert_video_to_mp4_from_src_dir(src_dir,include_suffix:list=None):
    if not src_dir:
        return
    lst=get_all_files_pathlib(src_dir,include_suffix)
    with ThreadPoolExecutor(max_workers=20) as executor:
        # 提交任务到线程池
        futures = [executor.submit(convert_video_to_mp4, video_path) for video_path in lst]
        
        # 等待所有任务完成
        for future in futures:
            future.result()  #
def merge_video_from_src_dir(src_dir,dest_path,include_suffix:list=None):
    if not src_dir or not dest_path:
        return
    merge_video(get_all_files_pathlib(src_dir,include_suffix),dest_path)