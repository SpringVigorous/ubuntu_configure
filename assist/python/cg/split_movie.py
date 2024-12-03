from moviepy.editor import VideoFileClip, concatenate_videoclips
from concurrent.futures import ThreadPoolExecutor

import subprocess
from pathlib import Path
import os
import sys

root_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.extend([root_dir,os.path.join(root_dir,"base")])


from base.video_tools import merge_video
from base.com_log import logger_helper,UpdateTimeType
from base.except_tools import except_stack

from datetime import datetime, timedelta

#返回多少秒数
def time_str_to_timedelta(time_str):
    """
    将时间字符串转换为 timedelta 对象
    :param time_str: 时间字符串，格式为 "HH:MM:SS" 或 "SS.sss"
    :return: timedelta 对象
    """
    if '.' in time_str:
        # 处理带有毫秒的时间字符串
        time_format = "%S.%f"
    else:
        # 处理标准的时间字符串
        time_format = "%H:%M:%S"
    
    return datetime.strptime(time_str, time_format) - datetime(1900, 1, 1)

def timedelta_to_time_str(td):
    """
    将 timedelta 对象转换为时间字符串
    :param td: timedelta 对象
    :return: 时间字符串，格式为 "HH:MM:SS"
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def convert_start_end_to_start_duration(start_time, end_time):
    """
    将起止时间元组转换为起始时间和时长元组
    :param start_time: 起始时间字符串，格式为 "HH:MM:SS" 或 "SS.sss"
    :param end_time: 结束时间字符串，格式为 "HH:MM:SS" 或 "SS.sss"
    :return: (起始时间字符串, 时长字符串) 元组
    """
    start_td = time_str_to_timedelta(start_time)
    end_td = time_str_to_timedelta(end_time)
    
    duration_td = end_td - start_td
    
    start_str = timedelta_to_time_str(start_td)
    duration_str = timedelta_to_time_str(duration_td)
    
    return start_str, duration_str



def convert_medio_to_mp4(input_file, output_file):
    """
    使用 ffmpeg 将 RMVB 文件转换为 MP4 文件
    :param input_file: 输入的 RMVB 文件路径
    :param output_file: 输出的 MP4 文件路径
    """
    # 构建 ffmpeg 命令
    command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-c:a', 'aac', output_file]
    log=logger_helper("视频转换",f"{input_file} 转换为 {output_file}")
    log.trace("开始")
    try:
        # 执行命令
        subprocess.run(command, check=True)
        log.trace("成功",update_time_type=UpdateTimeType.ALL)
        return True
    except :
        log.trace("失败",except_stack(), update_time_type=UpdateTimeType.ALL)
        return False
        

def repair_mp4(input_file, output_file):

    command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-map', '0', '-movflags', '+faststart', output_file]


    try:
        subprocess.run(command, check=True)
        print(f"Successfully repaired {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error repairing {input_file}: {e}")

# 示例调用




def time_to_seconds(time_str):
    """
    将时间字符串转换为秒数
    :param time_str: 时间字符串，格式为 "HH:MM:SS"
    :return: 总秒数
    """
    # 按冒号分割时间字符串
    parts = time_str.split(':')
    
    # 提取小时、分钟和秒
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    
    # 计算总秒数
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return total_seconds

#使用VideoFileClip和concatenate_videoclips 进行处理
def split_movie(input_file, clip_times, output_file:str=""):
    
    org_path=Path(input_file)

    if not output_file:
        dest_path=org_path.with_stem(f"{org_path.stem}-split")
        output_file=str(dest_path)
        
    log=logger_helper("抽取视频内容",f"开始抽取{input_file}的{clip_times},内容到{output_file}")
    log.info("开始")

    # 截取视频片段
    video = VideoFileClip(input_file)
    clips=[video.subclip(start, end) for start, end in clip_times]
    log.info("抽取完成",update_time_type=UpdateTimeType.ALL)
    
    # 拼接视频片段
    final_clip = concatenate_videoclips(clips)
    log.info("拼接完成",update_time_type=UpdateTimeType.ALL)

    # 保存结果:太慢了
    final_clip.write_videofile(output_file,write_logfile=True,preset="ultrafast")
    log.info("保存完成",update_time_type=UpdateTimeType.ALL)
    
    """
("00:6:10","00:17:47"),
("00:21:16","00:23:10"),
("00:32:01","00:39:35"),

    """

def extract_video_segment(input_file, output_file, start_time, duration):
    """
    使用 ffmpeg 提取视频的指定时间段内容
    :param input_file: 输入的视频文件路径
    :param output_file: 输出的视频文件路径
    :param start_time: 开始时间，格式为 "HH:MM:SS" 或 "SS.sss"
    :param duration: 持续时间，格式为 "HH:MM:SS" 或 "SS.sss"
    """
    # 构建 ffmpeg 命令
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,
        '-t', duration,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_file
    ]
    log=logger_helper("抽取视频内容",f"开始抽取{input_file}的{start_time},时长{duration}的内容到{output_file}")
    log.info("开始")
    try:
        # 执行命令
        subprocess.run(command, check=True)
        log.info("成功",update_time_type=UpdateTimeType.ALL)
    except subprocess.CalledProcessError as e:
        log.info("失败",update_time_type=UpdateTimeType.ALL)


def extract_video_segments(input_file, segments,dest_dir="", max_workers=6):
    """
    使用多线程提取视频的多个指定时间段内容
    :param input_file: 输入的视频文件路径
    :param segments: 包含 (start_time, end_time) 元组的列表
    :param output_prefix: 输出文件的前缀
    :param max_workers: 最大线程数
    """
    
    org_path=Path(input_file)
    dest_dir=os.path.join(str(org_path.parent),"temp",org_path.stem) if (not dest_dir) or os.path.abspath( Path.parent)==os.path.abspath(dest_dir) else dest_dir
    os.makedirs(dest_dir,exist_ok=True)
    
    file_list=[str(os.path.join(dest_dir,f"{i+1}.mp4"))  for i in range(len(segments)) ]
    
    

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        i=0
        for output_file, (start_time, end_time) in zip(file_list,segments):
            i=i+1
            if i<9:
                continue

            _,duration=convert_start_end_to_start_duration(start_time,end_time)
            futures.append(executor.submit(extract_video_segment, input_file, output_file, start_time, duration))
            
        # 等待所有任务完成
        for future in futures:
            future.result()

    return file_list

def extract_and_concatenate_video(input_file, segments):
    log=logger_helper(f"截取视频{input_file}的{len(segments)}段内容",str(segments))
    log.info("开始")
    org_path=Path(input_file)
    if False and  org_path.suffix.lower()!=".mp4":
        temp_path=str(org_path.with_suffix(".mp4"))
        log.update_target(f"转换{input_file}为{temp_path}")
        log.info("开始转换")
        if not convert_medio_to_mp4(input_file, temp_path):
            return
        log.info("转换成功")
        input_file=temp_path
        org_path=Path(input_file)
        log.update_target(f"截取视频{input_file}的{len(segments)}段内容")

    
    dest_path=str(org_path.with_name(f"{org_path.stem}_split.mp4"))
    video_lst=extract_video_segments(input_file, segments)
    log.info(f"抽取成功->{video_lst}",update_time_type=UpdateTimeType.ALL)
    
    # video_lst=[str(os.path.join(org_path.parent,"temp",org_path.stem,f"{i+1}.mp4")) for i in range(len(segments))]
    
    merge_video(video_lst,dest_path)
    log.info(f"合并成功->{dest_path}", update_time_type=UpdateTimeType.ALL)


if __name__=="__main__":
    
    
    
    
    # repair_mp4(r'F:\temp\1.mp4', r'F:\temp\2.mp4')
    # exit(0)
        # 定义视频片段的起始点和终止点
    # clip_times = [
    #     (0, 10),  # 从第0秒到第10秒
    #     (20, 30), # 从第20秒到第30秒
    #     (40, 50)  # 从第40秒到第50秒
    # ]
    """

    
    
1
("00:0:1","00:6:45"),
("00:10:01","00:17:37"),
("00:23:36","00:26:40"),
("00:28:50","00:38:42"),
("00:42:01","00:54:30"),



    """

    # 示例调用
    input_file = r"F:\数据库\1.mp4"
    time_seg = [
("00:4:29","00:5:20"),
("00:7:40","00:15:25"),
("00:23:54","00:40:22"),
("00:41:16","01:06:25"),
    ]

    #方式1：
    # extract_and_concatenate_video(input_file, time_seg)
    # exit(0)
    
    #方式2：保存的太慢了
    params=[
                ("1.mp4",
                    [
                        ("00:0:1","00:6:45"),
                        ("00:10:01","00:17:37"),
                        ("00:23:36","00:26:40"),
                        ("00:28:50","00:38:42"),
                        ("00:42:01","00:54:30"),
                    ]
                ),
                ("2.mp4",
                    [
                        ("00:5:20","00:08:59"),
                        ("00:10:17","00:27:01"),
                        ("00:34:10","00:38:55"),
                        ("00:44:30","01:9:55"),
                        ("01:1:30","01:11:54"),
                    ]
                ),
             ]
    
    cur_dir=r"F:\数据库"
    # for name,time_seg in params:
    #     clip_times=[(time_to_seconds(start),time_to_seconds(end))  for start,end in time_seg]
    #     split_movie(os.path.join(cur_dir,name), clip_times)
    # import time

    # # 设置 1 秒后关机
    # subprocess.run(['shutdown', '/s', '/t', '1'])

    # # 等待 1 秒，以便观察效果
    # time.sleep(2)

    # 取消关机（可选）
    # subprocess.run(['shutdown', '/a'])
    
    for name in ["立花里子-白衣护士.wmv","立花里子-女佣-02.wmv"]:
        cur_path=Path(os.path.join(cur_dir,name))
        dest_path=cur_path.with_suffix(".mp4")
        convert_medio_to_mp4(cur_path,  dest_path)