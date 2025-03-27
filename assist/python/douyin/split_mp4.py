import ffmpeg
import os
import re

from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import  logger_helper,UpdateTimeType


from scenedetect import detect, ContentDetector, split_video_ffmpeg

from scenedetect.detectors import ContentDetector
from concurrent.futures import ThreadPoolExecutor
import hashlib
from functools import lru_cache
import subprocess
import json
import pandas as pd
from openpyxl import load_workbook
from base import merge_all_identical_column_file,move_columns_to_front,columns_index,copy_file


def get_video_duration(file_path):
    """增强版时长获取（带详细错误处理）"""
    try:
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        # 检查文件是否可读
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"无读取权限: {file_path}")

        # 执行 ffprobe 命令
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]
        
        # 处理子进程超时（10秒）
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            timeout=10,
            universal_newlines=True
        )
        
        # 解析 JSON 数据
        data = json.loads(output)
        if 'format' not in data or 'duration' not in data['format']:
            raise ValueError("无效的视频格式数据")
            
        return round(float(data['format']['duration']), 3)

    except subprocess.CalledProcessError as e:
        print(f"FFprobe 错误 ({file_path}): {e.output.strip()}")
    except json.JSONDecodeError:
        print(f"无效的 JSON 响应 ({file_path})")
    except Exception as e:
        print(f"处理 {file_path} 时发生意外错误: {str(e)}")
    
    return None
@lru_cache(maxsize=100)
def get_video_duration_cached(file_path):
    """带缓存机制的时长获取"""
    return get_video_duration(file_path)
def get_mp4_files_info(folder_path):
    video_info = []
    files_to_process = []
    
    # 收集文件路径
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp4'):
                files_to_process.append(os.path.join(root, file))
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(get_video_duration, files_to_process)
        for path, duration in zip(files_to_process, results):
            if duration is not None:
                video_info.append((os.path.basename(path), duration))
    
    return video_info

def detect_change(video_path,outdir="out"):
    
    
    logger=logger_helper("检测场景切换",video_path)
    # 初始化检测器
    detector = ContentDetector(
        threshold=27.0,
        min_scene_len=24,  # 约 1 秒（假设 24fps）
        luma_only=False
    )

    # 执行检测
    scenes = detect(
        video_path,
        detector=detector,
        start_in_scene=True,

    )
    # 结果输出
    logger.info(f"检测到 {len(scenes)} 个场景",update_time_type=UpdateTimeType.STAGE)
        # 获取原始视频信息（用于保持参数一致）
    probe = ffmpeg.probe(video_path)
    video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
    width,height=video_stream.get('width',640),video_stream.get('height',480)
    size_info=f"{width}x{height}"
    

    
    logger.update_target(target="分割视频")
    logger.info("获取视频分辨率",size_info,update_time_type=UpdateTimeType.STAGE)
    # 分割视频（需要 ffmpeg）
    split_video_ffmpeg(
        video_path, 
        scenes,
        output_dir=outdir,
        show_progress=True,
        output_file_template=f"$VIDEO_NAME-{width}x{height}_$SCENE_NUMBER.mp4",
    )
    logger.info("成功",update_time_type=UpdateTimeType.ALL)



dest_name_pattern = r'^(.*?)-'
dest_scene_pattern = r'-(\d+xd+)_(\d+).mp4'
def get_dest_name(file_name):
    match = re.search(dest_name_pattern, file_name)
    if match:
        return match.group(1)


#仅仅获取目标文件夹的 文件名eg:  顾村公园樱花_001-1080x1920_001.mp4  -> 顾村公园樱花_001
def dir_file_names(dir_path):
    results=[]
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            cur_name=get_dest_name(file)
            if cur_name in results:
                continue
            results.append(cur_name)
    return results
    

def split_times(dir_path,dest_dir):

    already_lst=dir_file_names(dest_dir)

    for root, dirs, files in os.walk(dir_path):
        # 构建输出文件路径
        for file in files:
            logger=logger_helper("检测场景切换",file)
            
            filename, ext = os.path.splitext(file)
            if filename in already_lst:
                logger.info("跳过","已存在")
                continue
            
            #文件名若是有 - 则替换成 _
            if "-" in filename:
                new_file = file.replace('-', '_')
                logger.info("重命名",f"{file} -> {new_file}")
                
                # 重命名文件
                os.rename(os.path.join(root, file), os.path.join(root, new_file))
                file=new_file

            org_file_path = os.path.join(root, file)
            detect_change(org_file_path,dest_dir)
            logger.info("完成",f"{file} -> {new_file}")

def dest_to_excel(dest_dir):
    
    sheet_name="视频信息"
    file_path=os.path.abspath(os.path.join(dest_dir,"../视频分割信息.xlsx"))
    
    logger=logger_helper("结果汇总",f"{dest_dir}->{file_path}")
    logger.trace("开始")   
        #获取视频信息
    lst=[{"文件名":path,"时长s":duration} for path,duration in get_mp4_files_info(dest_dir)]
    df=pd.DataFrame(lst)
    # 使用正则表达式提取三个部分
    df[['原始文件', '分辨率', '序列号']] = df['文件名'].str.extract(
        r'^(.+?)-(\d+x\d+)_.+?(\d+)\.mp4$'
    )
    # 按 原始文件 列分组，对 时长s 列求和
    grouped = df.groupby('原始文件')['时长s'].sum().reset_index(name='总时长')
    # 合并原始 DataFrame 和求和结果
    df = pd.merge(df, grouped, on='原始文件')
    front_cols=['原始文件', '分辨率', '序列号','总时长']
    
    df=move_columns_to_front(df,front_cols)
    df.to_excel(file_path,sheet_name=sheet_name,index=False)
    front_index=[index+1 for index in columns_index(df,front_cols)]
    merge_all_identical_column_file(file_path,sheet_name=sheet_name,col_index=front_index)
    logger.info("完成",update_time_type=UpdateTimeType.ALL)
    


def usage_segs(src_dir,org_paths,subdir):
    
    name_pattern = r'[^,\s]+'
    lst=[os.path.join(src_dir,item) for item in  re.findall(name_pattern, org_paths)]
    dest_dir=os.path.abspath(os.path.join(src_dir,f"../usage/{subdir}"))
    os.makedirs(dest_dir,exist_ok=True)
    
    copy_file(lst,dest_dir)
    pass    
    

def main(src_dir,dest_dir):

    
    os.makedirs(dest_dir,exist_ok=True)
    logger=logger_helper(src_dir,dest_dir)
    logger.trace("开始")
    split_times(src_dir,dest_dir)
    logger.info("成功",update_time_type=UpdateTimeType.ALL)

    dest_to_excel(dest_dir)
    
    
    
# 示例调用
if __name__ == "__main__":
    src_dir=r"F:\worm_practice\douyin\素材\org"
    dest_dir=os.path.abspath(os.path.join(src_dir,"../dest"))
    
    org_paths="""
    鼋头渚夜樱_001-1080x1920_002.mp4, 鼋头渚夜樱_001-1080x1920_004.mp4, 鼋头渚夜樱_001-1080x1920_006.mp4, 鼋头渚夜樱_001-1080x1920_008.mp4, 鼋头渚夜樱_003-720x1560_001.mp4, 鼋头渚夜樱_003-720x1560_003.mp4, 鼋头渚夜樱_003-720x1560_005.mp4, 鼋头渚夜樱_003-720x1560_007.mp4, 鼋头渚夜樱_004-720x1280_001.mp4, 鼋头渚夜樱_004-720x1280_003.mp4, 鼋头渚夜樱_004-720x1280_005.mp4
    """
    sub_dir="1"
    
    usage_segs(dest_dir,org_paths,sub_dir)
    exit()
    main(src_dir,dest_dir)