

import os
from pathlib import Path
from path_tools import normal_path,windows_path
from com_exe_path import ffmpeg_path


from com_log import logger_helper,UpdateTimeType
import subprocess
from concurrent.futures import ThreadPoolExecutor
from com_decorator import  exception_decorator
from string_tools import hash_text
from remove_special_fold import recycle_bin
from file_tools import move_file
from path_tools import cache_temp_path
import json
import ffmpeg

@exception_decorator(error_state=False)
def get_video_metadata_ffmpeg(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        (s for s in probe["streams"] if s["codec_type"] == "video"), None
    )
    if not video_stream:
        raise ValueError("未找到视频流")
    
    return {
        "resolution": (int(video_stream["width"]), int(video_stream["height"])),
        "duration": float(video_stream["duration"]),  # 单位：秒
        "codec": video_stream["codec_name"],         # 编码格式（如 h264）
        "bitrate": int(video_stream.get("bit_rate", 0))  # 比特率（bps）
    }

def get_video_duration(video_path: str) -> float:
    """
    获取视频时长（秒）
    :param video_path: 视频文件路径
    :return: 视频时长（秒）
    """
    result=get_video_metadata_ffmpeg(video_path)
    if not result or "duration" not in result: return 0
    return float(result["duration"])


def get_video_rotation(video_path: str) -> int:
    """
    获取视频元数据中的旋转角度（rotate）
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        int: 旋转角度（0/90/180/270），无标记时返回0
        
    """
    
    logger=logger_helper("获取元信息-旋转角",video_path)
    
    try:
        # 构建ffprobe命令获取视频流信息
        cmd = [
            "ffprobe",
            "-v", "quiet",
            # "-logger.trace_format", "json",
            "-print_format", "json",
            "-show_streams",
            # "-show_format",
            video_path
        ]
        # 执行命令并捕获输出
        result = subprocess.run(
            cmd, 
            capture_output=True, text=True, timeout=10  # 防止阻塞
        )
        
        # 解析JSON输出
        
        result_data=result.stdout or result.stderr
        if not result_data:
            logger.error("ffprobe 输出为空")
            
            
            return 0
        
        probe_data = json.loads(result_data)
        
        # 遍历所有流寻找视频流
        for stream in probe_data.get("streams", []):
            if stream.get("codec_type") == "video":
                # 检查旋转标记（可能存在两种形式）
                rotation = 0
                if "rotate" in stream.get("tags", {}):
                    rotation = int(stream["tags"]["rotate"])
                elif "side_data_list" in stream:
                    for side_data in stream["side_data_list"]:
                        if side_data.get("displaymatrix"):
                            matrix = side_data["displaymatrix"]
                            # 根据旋转矩阵计算角度
                            if matrix.startswith("rotation of -90.00"):
                                rotation = 270
                            elif matrix.startswith("rotation of 90.00"):
                                rotation = 90
                            elif matrix.startswith("rotation of 180.00"):
                                rotation = 180
                return rotation
                
    except Exception as e:
        logger.error("异常",f"{e}")
        pass
    
    return 0

#仅仅清理旋转标签，而不更改视频
def remove_rotate_info_by_metadata(video_path: str):
    """
    清除视频的旋转标记并覆盖原始文件
    
    Args:
        video_path: 视频文件路径
    """
    
    logger=logger_helper("清除视频元数据-旋转值",video_path)
    
    
    rotation = get_video_rotation(video_path)
    log_info=f"旋转值：{rotation}"
    
    if rotation == 0:
        logger.trace("忽略",f"{log_info},直接返回",update_time_type=UpdateTimeType.STAGE)
        return  # 无需处理
    
    # 创建临时文件路径
    temp_path=cache_temp_path(video_path)
    
    try:
        # 构建FFmpeg命令清除旋转标记
        cmd = [
            ffmpeg_path(),
            "-i", video_path,
            "-c", "copy",           # 复制原始流不重编码
            "-metadata:s:v:0", f"rotate=0",  # 清除旋转标记
            "-map_metadata", "0",   # 保留其他元数据
            "-y",                    # 覆盖输出文件
            temp_path
        ]
        
        # 执行FFmpeg命令
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        
    except Exception as e:
        logger.error("失败",f"{e}")
        return False
    
    
    # 清理临时文件（如果存在）
    if os.path.exists(temp_path):
        # 用临时文件替换原始文件

        move_file(temp_path, video_path)
        
        logger.info("成功",f"{log_info}",update_time_type=UpdateTimeType.STAGE)
        
        return True
    
    return False

#按照视频元信息，旋转视频
def rotate_video_by_metadata(video_path: str):
    """
    根据旋转元数据物理旋转视频并清除旋转标记
    Args:
        video_path: 视频文件路径
    """
    logger=logger_helper("根据视频元数据-旋转",video_path)
    
    rotation = get_video_rotation(video_path)
    
    # 无需处理的情况
    if rotation == 0:
        logger.trace("忽略","角度为0，无需旋转",update_time_type=UpdateTimeType.STAGE)
        return
    #先清除旋转信息
    remove_rotate_info_by_metadata(video_path)
    #后真正旋转
    
    # 创建临时文件
    temp_output = cache_temp_path(video_path)
    
    # 确定FFmpeg旋转滤镜
    if rotation == 90:
        vf = "transpose=1"  # 90度顺时针
    elif rotation == 180:
        vf = "hflip,vflip"  # 180度
    elif rotation == 270:
        vf = "transpose=2"  # 270度（逆时针90度）
    else:
        logger.error("异常",f"不支持的旋转角度: {rotation}°",update_time_type=UpdateTimeType.STAGE)
        return
    
    try:
        # 构建FFmpeg命令（物理旋转+清除旋转标记）
        cmd = [
            ffmpeg_path(),
            "-i", video_path,
            "-vf", vf,                    # 应用旋转滤镜
            "-metadata:s:v:0", "rotate=0", # 清除旋转标记
            "-c:a", "copy",                # 复制音频流
            "-y",                          # 覆盖输出文件
            temp_output
        ]
        
        # 执行旋转操作
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.error("异常",f"旋转失败: {result.stderr}")
            return False
        
        # 安全覆盖原始文件
        move_file(temp_output, video_path)
        logger.trace("成功",f"旋转:{rotation}°",update_time_type=UpdateTimeType.STAGE)
        return True
        
    except Exception as e:
        logger.error("异常",str(e),update_time_type=UpdateTimeType.STAGE)
        # 清理临时文件
        if os.path.exists(temp_output):
            os.remove(temp_output)
        return False

    
    


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

#获取视频首帧图片
@exception_decorator(error_state=False)
def cover_video_pic(video_path,output_path):
    command = [ffmpeg_path(),'-i', windows_path(video_path),'-ss','00:00:00.050', '-vframes', '1', '-c:v', 'mjpeg','-q:v', '2', '-an' ,'-y', windows_path(output_path)]
    _= subprocess.run(command, capture_output=True, text=True,errors="ignore",check=True)
    

def merge_video(temp_paths,output_path):
    if not temp_paths or not output_path:
        return

    temp_file= windows_path(os.path.join(Path(temp_paths[0]).parent,'file_list.txt'))
    logger.trace(temp_file)

    merge_logger= logger_helper("合并视频",f"{temp_file} -> {output_path}")
    merge_logger.trace("开始")
    # 创建一个文件列表文件
    with open(temp_file, 'w') as file:
        for temp_path in temp_paths:
            if not os.path.exists(temp_path):
                continue
            file.write(f"file {windows_path(temp_path)}\n")

    # 使用 FFmpeg 合并文件

    # command = [ffmpeg_path(),'-y', '-f', 'concat', '-safe', '0', '-i', temp_file, '-c', 'copy', output_path]
    command = [ffmpeg_path(),'-y', '-f', 'concat', '-safe', '0', '-i', temp_file]
    if False:
        command.extend(['-vf', "crop=1920:800:0:130" ,'-c:v', 'libx264',"-c:a"])
    else:
        command.extend(['-c'])
    command.extend(['copy', output_path])
    
    
    merge_logger.update_target(detail=" ".join(command))
    merge_logger.trace("参数")

    # subprocess.run(command, check=True)
    # 运行命令并获取返回值
    # result = subprocess.run(command, capture_output=True, text=True,encoding="utf-8",errors="ignore",check=True)
    result = subprocess.run(command, capture_output=True, text=True,errors="ignore",check=True)



    # 获取标准输出和标准错误
    stdout = result.stdout
    stderr = result.stderr




    if stderr:
        merge_logger.error("失败",f"\n{stderr}\n",update_time_type=UpdateTimeType.ALL)
    if stdout:
        merge_logger.debug("成功",f"\n{stdout}\n",update_time_type=UpdateTimeType.ALL)

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
        logger.trace(f"转换成功: {video_path} -> {output_path}")
    except subprocess.CalledProcessError as e:
        logger.trace(f"转换失败: {video_path}")
        logger.trace(e)




#线程池处理
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
def merge_video_from_src_dir(src_dir,output_path,include_suffix:list=None):
    if not src_dir or not output_path:
        return
    merge_video(get_all_files_pathlib(src_dir,include_suffix),output_path)

#是否内嵌封面
def has_embedded_cover(video_path: str) -> bool:
    """
    检测MP4文件是否已包含内嵌封面
    Args:
        video_path: 视频文件路径
    Returns:
        bool: True=已有封面, False=无封面
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_streams",
            "-logger.trace_format", "json",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                # 检查封面标记
                if stream.get("disposition", {}).get("attached_pic") == 1:
                    return True
                # 检查旋转值（某些设备将封面存储为旋转帧）
                if int(stream.get("tags", {}).get("rotate", 0)) != 0:
                    return True
        return False
    except Exception:
        return False
#首帧作为内嵌封面
def add_first_frame_as_cover(video_path: str):
    """
    为无封面的MP4添加第一帧作为封面
    Args:
        video_path: 视频文件路径
    """
    logger=logger_helper("添加封面",video_path)
    # 检查是否已有封面
    if has_embedded_cover(video_path):
        logger.trace("忽略","视频已有封面，跳过处理",update_time_type=UpdateTimeType.STAGE)
        return
    
    # 创建临时文件（确保与原文件同分区）
    
    
    temp_file=cache_temp_path(video_path)

    exe_path=ffmpeg_path()
    
    try:
        # 步骤1：提取第一帧到内存管道
        extract_cmd = [
            exe_path,
            "-i", video_path,
            "-ss", "0.1",  # 0秒可能无效，取0.1秒
            "-vframes", "1",
            "-f", "image2pipe",
            "-c:v", "mjpeg",
            "pipe:1"
        ]
        
        # 步骤2：添加封面到临时文件
        embed_cmd = [
            exe_path,
            "-i", video_path,          # 原始视频
            "-i", "pipe:0",            # 从管道接收封面
            "-map", "0",               # 原始所有流
            "-map", "1",               # 封面图像流
            "-c", "copy",              # 复制原始流
            "-c:v:1", "mjpeg",         # 封面编码格式
            "-disposition:v:1", "attached_pic",  # 设为封面
            "-y",                      # 覆盖输出
            temp_file
        ]
        
        # 管道连接两个进程
        p1 = subprocess.Popen(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(embed_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p1.stdout.close()  # 允许p1在p2终止时接收SIGPIPE
        
        # 等待执行完成
        stdout, stderr = p2.communicate()
        
        if p2.returncode != 0:
            logger.error("异常",f"添加封面失败: {stderr.decode('utf-8')}",update_time_type=UpdateTimeType.STAGE)
        else:
            
            # 安全替换原文件
            move_file(temp_file, video_path)
            logger.info(f"成功添加封面: {video_path}",update_time_type=UpdateTimeType.STAGE)
        
    except Exception as e:
        logger.error(f"处理错误: {str(e)}",update_time_type=UpdateTimeType.STAGE)
        # 清理临时文件
        recycle_bin(temp_file)
    finally:
        # 确保进程终止
        if 'p1' in locals() and p1.poll() is None:
            p1.terminate()
        if 'p2' in locals() and p2.poll() is None:
            p2.terminate()

#根据开始时间和时长分割视频
def ffmpeg_extract(input_path, output_path, start_time, duration):
    logger= logger_helper(f"视频切片:{input_path}->{output_path}",f"start:{start_time},duration:{duration}")
    # # 粗定位：提前1秒开始（避免遗漏）
    # rough_start = max(0, start_time - 1.0)
    # # 精定位：从粗定位点再偏移至目标时间
    # cmd = [
    #     "ffmpeg",
    #     "-ss", str(rough_start),    # 粗定位（关键帧快速跳转）
    #     "-i", input_path,
    #     "-ss", str(start_time - rough_start),  # 精定位（解码偏移）
    #     "-t", str(duration),
    #     "-c", "copy",               # 复制流（不转码）
    #     "-avoid_negative_ts", "1",  # 防止负时间戳
    #     output_path
    # ]
    
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-ss", str(start_time),      # 精确到帧（需解码）
        "-t", str(duration),
        "-c:v", "libx264",          # 重新编码视频
        "-c:a", "aac",              # 重新编码音频
        "-preset", "fast",           # 平衡速度与质量
        "-y",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("异常",f"Error: {e.stderr}")
        return False


if __name__ == "__main__":
    pass
    # 示例：从30秒截取20秒（零转码）
    ffmpeg_extract(r"E:\video\20250804\video_20250804_162015.mp4", r"E:\video\20250804\split\video_20250804_162015-1080x1920_001.mp4", 0, 6)