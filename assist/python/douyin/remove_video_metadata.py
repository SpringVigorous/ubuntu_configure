import subprocess
import os
from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import path_equal,guid
from base import logger_helper,UpdateTimeType,copy_file

#返回处理成功的文件路径
def remove_metadata(input_path, output_dir=None):
    """
    使用 FFmpeg 移除视频元信息
    参数：
        input_path: 输入视频路径
        output_dir: 输出目录路径
    返回：
        处理后的文件路径
    """
    if not output_dir:
        output_dir = os.path.dirname(input_path)
    else:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出路径
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, filename)
    

    is_dest_same=path_equal(input_path,output_path)
    is_metadata=has_metadata(input_path)
    logger=logger_helper("去除视频元数据",f"{filename}->{output_path}")
    
    #没有源数据信息，则提前结束
    if not is_metadata:
        if is_dest_same:
            logger.info("跳过","不含有元数据")
        else:
            copy_file(input_path,output_path)
        return output_path
    
    
    temp_path=output_path if not  is_dest_same else  os.path.join(output_dir, f"clean_{guid(6)}_{filename}")
    
    # FFmpeg 命令（保留原始编码参数）
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-map_metadata', '-1',  # 清除所有元数据
        '-c:v', 'copy',         # 复制视频流
        '-c:a', 'copy',         # 复制音频流
        '-movflags', 'use_metadata_tags',  # 处理 MP4 格式
        '-y',                   # 覆盖输出文件
        temp_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.trace("成功")
        if is_dest_same:
            os.remove(input_path)
            os.rename(temp_path,output_path)
        
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"失败",f"{filename}\n错误信息: {e.stderr.decode()}")
        return None
    finally:
        if is_dest_same and os.path.exists(temp_path):
            os.remove(temp_path)

def has_metadata(file_path):
    """ 使用 FFprobe 验证元数据清除情况 """
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format_tags',
        '-of', 'default=noprint_wrappers=1',
        file_path
    ]
    logger=logger_helper("检查视频元数据",file_path)
    
    try:
        output = subprocess.run(cmd, capture_output=True, text=True)
        flags=["com.apple.quicktime.make","MetaInfo"]
        for flag in flags:
            if flag in output.stdout:
                logger.info("检测到元数据",output.stdout,update_time_type=UpdateTimeType.STAGE)
                return True

        logger.info("无元数据",output.stdout,update_time_type=UpdateTimeType.STAGE)

    except Exception as e:
        logger.error(f"失败",f"{str(e)}",update_time_type=UpdateTimeType.STAGE)

def batch_clean_metadata(input_dir, output_dir):
    """
    批量处理目录中的所有视频文件
    支持格式: .mp4, .mov, .mkv
    """
    video_exts = ('.mp4', '.mov', '.mkv')
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(video_exts):
                input_path = os.path.join(root, file)
               
                cleaned_file =remove_metadata(input_path, output_dir)
                if cleaned_file:
                    has_metadata(cleaned_file)
                # 可选：深度清理（需要 ExifTool）
                # deep_clean_metadata(input_path, output_dir)



if __name__ == "__main__":
    input_dir = r"F:\worm_practice\douyin\素材\合成"
    output_dir = os.path.join(input_dir, "cleaned_videos")
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理单个文件
    file_path=os.path.join(input_dir,"鼋头渚夜樱合成_001.mp4")
    #先检查

    cleaned_file = remove_metadata(file_path, input_dir)
    if not cleaned_file:
        exit()
    has_metadata(cleaned_file)

    # 批量处理目录
    # batch_clean_metadata(input_dir,output_dir)
    