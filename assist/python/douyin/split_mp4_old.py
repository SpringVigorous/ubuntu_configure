import ffmpeg
import os

from datetime import datetime, timedelta
from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import  logger_helper,UpdateTimeType


from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector


def detect_change(video_path,diff_time=.05):
    # 初始化
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=27.0))

    # 处理视频
    video_manager.set_downscale_factor(2)
    video_manager.start()
    scene_manager.detect_scenes(video_manager)
    
    # 获取结果
    scene_list = scene_manager.get_scene_list()
    timestamps = [scene[0].get_seconds() for scene in scene_list]
    print(f"检测到 {len(scene_list)} 个场景")
    

    
    # return timestamps[1:]

# 定义基准时间
__base_time= datetime(1970, 1, 1)


def float_seconds_to_timedelta(seconds:int|float)->timedelta:
    # 获取当前时间
    second=int(seconds)
    millisecond=int((float(seconds)-second)*1000)
    # 计算时间差
    return timedelta(seconds=seconds,microseconds=millisecond)

def float_seconds_to_datetime(seconds:int|float)->datetime:


    # 创建一个 timedelta 对象，表示时间间隔
    time_interval = float_seconds_to_timedelta(seconds)
    # 将基准时间和时间间隔相加，得到新的 datetime 对象
    new_time = __base_time + time_interval
    return new_time
def str_to_time(time_str:str)->datetime:
    """
    将时间字符串转换为 datetime 对象
    :param time_str: 时间字符串，格式为 'HH:MM:SS.sss'
    :return: 对应的 datetime 对象
    """
    return datetime.strptime(time_str, '%H:%M:%S.%f')




def add_seconds(time_obj, seconds:int|float):
    """
    给 datetime 对象增加指定的秒数
    :param time_obj: datetime 对象
    :param seconds: 要增加的秒数
    :return: 增加秒数后的 datetime 对象
    """
    return time_obj +float_seconds_to_timedelta(seconds)


def time_to_str(time_obj):
    """
    将 datetime 对象转换为时间字符串
    :param time_obj: datetime 对象
    :return: 对应的时间字符串，格式为 'HH:MM:SS.sss'
    """
    return time_obj.strftime('%H:%M:%S.%f')[:-3]

def float_seconds_to_datetime_str(seconds:int|float)->str:

    return time_to_str(float_seconds_to_datetime(seconds))

def precise_cut_seg(input_video:str,output_file:str,start_time:str,duration:str,bit_rate,r_frame_rate):
    logger=logger_helper(input_video,output_file)
    try:
        (
            ffmpeg
            .input(input_video, ss=start_time)  # 设置起始时间
            .output(
                output_file,
                t=duration,               # 设置持续时间
                **{
                    'c:v': 'libx264',            # 视频编码器
                    'b:v': bit_rate,  # 保持原始码率
                    'r': r_frame_rate,   # 保持原始帧率
                    'c:a': 'aac',                # 音频编码器
                    'avoid_negative_ts': '1',    # 避免时间戳错误
                    'fps_mode': 'vfr',              # 可变帧率处理
                }
            )
            .overwrite_output()                  # 允许覆盖输出文件
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info("成功")
    except ffmpeg.Error as e:
        logger.error("失败")
        return False
    return True

def get_split_times(segs:list[str],end_time:float,step_time:float=.1)->list[tuple[str,str]]:
    end_time=float_seconds_to_datetime(end_time)
    start_time=float_seconds_to_datetime(0)
    time_lst=[]
    cur_time=float_seconds_to_datetime(0)
    for split_time in segs:
        split_time=float_seconds_to_datetime(split_time)
        if split_time<=cur_time:
            continue
        delta=(split_time-cur_time).total_seconds()
        time_lst.append((time_to_str(cur_time),float_seconds_to_datetime_str(delta)))
        cur_time=add_seconds(split_time,step_time)

    if cur_time<end_time:
        time_lst.append((time_to_str(cur_time),float_seconds_to_datetime_str((end_time-cur_time).total_seconds())))
    
    
    return time_lst
    


def precise_cut(input_video, splits, dest_dir="output"):
    
    logger=logger_helper("分割视频",input_video)
    logger.trace("开始",f"{splits}")
    src_path=Path(input_video)
    src_name=src_path.stem
    """
    精准切割视频（需重新编码）
    
    参数：
        input_video: 输入视频路径
        segments: 切割时间段列表，格式示例：
            [
                {"start": "00:00:00.000", "duration": "00:00:02.300"},
                {"start": "00:00:02.350", "duration": "00:00:01.950"},
            ]
        output_prefix: 输出文件名前缀
    """
    # 获取原始视频信息（用于保持参数一致）
    probe = ffmpeg.probe(input_video)
    video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
    width,height=video_stream.get('width',640),video_stream.get('height',480)
    duration=float(video_stream.get('duration','0'))
    name_latter=f"{width}x{height}"
    
    failure_lst=[]
    
    split_lst=get_split_times(splits,duration,0.1)
    
    # 循环处理每个时间段
    for idx, seg in enumerate(split_lst, start=1):
        output_file =os.path.join(dest_dir,f"{src_name}_{name_latter}_{idx:03}.mp4") 
        start_time ,duration = seg
        bit_rate = video_stream.get('bit_rate', '5000k')
        r_frame_rate = video_stream.get('r_frame_rate', '30')
        if not precise_cut_seg(input_video=input_video,output_file=output_file,start_time=start_time,duration=duration,bit_rate=bit_rate,r_frame_rate=r_frame_rate):
            failure_lst.append(idx)
            
    if not failure_lst:
        logger.info("成功",update_time_type=UpdateTimeType.ALL)
    else:
        logger.error("失败",update_time_type=UpdateTimeType.ALL)

#lst:[(input_video, splits)]
def precise_cuts(lst,dest_dir):

    for item in lst:
        input_video, splits=item
        precise_cut(input_video, splits, dest_dir)
        
        
def test(src_dir)->list:
    
    lst=[
        (os.path.join(src_dir,"鼋头渚夜樱_002.mp4"),[4.9,10.8,13.6,25,]),
        (os.path.join(src_dir,"鼋头渚夜樱_003.mp4"),[2.3,5.5,7.3,8.8,11.7,14,16.9,19.5,22.1,25.4]),
        (os.path.join(src_dir,"鼋头渚夜樱_004.mp4"),[1.7,3.5,5.4,6.9,]),
        (os.path.join(src_dir,"鼋头渚夜樱_005.mp4"),[2.8,4.5,6.2,8.1,9.7,10.9,12.4,16.8,18.6,19.8,]),
        (os.path.join(src_dir,"鼋头渚夜樱_006.mp4"),[0.7,1.4,2.7,3.5,4.5,6.5,]),
    ]
    return


def split_times(dir_path):
    results=[]
    for root, dirs, files in os.walk(dir_path):
        # 构建输出文件路径

        for file in files:

            org_file_path = os.path.join(root, file)
            times=detect_change(org_file_path)
            break
            if times:
                results.append((org_file_path,times))
    
    return results


def main():
    src_dir=r"F:\worm_practice\douyin\素材\org"
    dest_dir=os.path.abspath(os.path.join(src_dir,"../dest"))
    os.makedirs(dest_dir,exist_ok=True)

    lst=split_times(src_dir)
    logger=logger_helper(src_dir,dest_dir)
    logger.trace("开始")
    precise_cuts(lst, dest_dir=dest_dir)


    logger.info("成功",update_time_type=UpdateTimeType.ALL)

# 示例调用
if __name__ == "__main__":
    
    main()