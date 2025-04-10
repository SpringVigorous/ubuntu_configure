import ffmpeg
import os
import re

from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import  logger_helper,UpdateTimeType,download_sync,read_content_by_encode,unique,fill_adjacent_rows


from scenedetect import detect, ContentDetector, split_video_ffmpeg

from scenedetect.detectors import ContentDetector
from concurrent.futures import ThreadPoolExecutor
import hashlib
from functools import lru_cache
import subprocess
import json
import pandas as pd
from openpyxl import load_workbook
from base import merge_all_identical_column_file,move_columns_to_front,columns_index,copy_file,move_file,path_equal
from dy_unity import OrgInfo,DestInfo,dy_root
from datetime import datetime, timedelta




class DYFileUnity:
    
    def __init__(self) -> None:
        self.dir_dict={}
        pass
    def update_dir(self,dest_dir):
        self.dir_dict[dest_dir]=DYFileUnity.dir_file_names(dest_dir)
    def get_video_names(self,dest_dir):
        if dest_dir not in self.dir_dict:
            self.update_dir(dest_dir)
        return self.dir_dict[dest_dir]
    def exists(self,dir_path,video_path):
        name=OrgInfo(video_path).org_name
        return name in self.get_video_names(dir_path)


    #仅仅获取目标文件夹的 文件名eg:  顾村公园樱花_001-1080x1920_001.mp4  -> 顾村公园樱花_001
    @staticmethod
    def dir_file_names(dir_path):
        results=[]
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                cur_name=DestInfo(file).org_name
                if not cur_name or cur_name in results:
                    continue
                results.append(cur_name)
        return results
    
    
    

    @staticmethod
    def check_src_file(file_path):
        cur_path=Path(file_path)
        name=cur_path.stem
        logger=logger_helper("检查文件名",file_path)
        
        #文件名若是有 - 则替换成 _
        if "-" in name:
            new_name = name.replace('-', '_')
            
            org_path=str(cur_path)
            file_path=str(cur_path.with_stem(new_name))
            
            # 重命名文件
            os.rename(org_path, file_path)
            logger.info("重命名",f"{org_path} -> {file_path}")
        
        return file_path
    @staticmethod
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

    @staticmethod
    def get_mp4_files_info():
        video_info = []
        files_to_process = []
        
        # 收集文件路径
        for root, _, files in os.walk(dy_root.dest_root):
            for file in files:
                if file.lower().endswith('.mp4'):
                    files_to_process.append(os.path.join(root, file))
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(DYFileUnity.get_video_duration, files_to_process)
            for path, duration in zip(files_to_process, results):
                if duration is not None:
                    video_info.append((os.path.basename(path), duration))
        
        return video_info
    
class SplitBase:
    def __init__(self) -> None:
        self.file_manager= DYFileUnity()
    
    @staticmethod
    def load_split_xlsx(self)->pd.DataFrame:
        xls_path,sheet_name=dy_root.split_info_xlsx_path
        df=pd.read_excel(xls_path,sheet_name=sheet_name)
        df=fill_adjacent_rows(df,['原始文件', '分辨率', '序列号','总时长'])
        return df
    
    @staticmethod
    def save_split_xlsx():
        dest_dir=dy_root.split_info_root

        file_path,sheet_name=dy_root.split_info_xlsx_path
        
        logger=logger_helper("结果汇总",f"{dest_dir}->{file_path}")
        logger.trace("开始")   
        #获取视频信息
        lst=[{"文件名":path,"时长s":duration} for path,duration in DYFileUnity.get_mp4_files_info()]
        logger.info("获取时长信息",update_time_type=UpdateTimeType.STAGE)   
        
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
        #加载用户选择的列
        for file in os.listdir(dy_root.usage_src_root):
            file_path=os.path.join(dy_root.usage_src_root,file)
        
        front_index=[index+1 for index in columns_index(df,front_cols)]
        merge_all_identical_column_file(file_path,sheet_name=sheet_name,col_index=front_index)
        logger.info("完成",update_time_type=UpdateTimeType.ALL)
        return 
    def classify_files_by_series(self,src_dir,dest_dir):
        results={}
        # 遍历源目录下的所有文件
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                info=DestInfo(file)
                org_path=os.path.join(root,file)
                dest_sub_dir=os.path.join(dest_dir,info.series_name)
                
                if path_equal(root,dest_sub_dir):
                    continue
                
                if dest_sub_dir in results:
                    results[dest_sub_dir].append(org_path)
                else:
                    results[dest_sub_dir]=[org_path]
                    
                    
        for dest_dir in  results:
            os.makedirs(dest_dir,exist_ok=True)
            for src_path in results[dest_dir]:
                move_file(src_path,dest_dir)


class AutoSplit(SplitBase):
    
    def __init__(self) -> None:
        super().__init__()

        
        pass
    def split_videos(self):
        
        dir_path,dest_dir=dy_root.org_root,dy_root.dest_root

        
        for root, dirs, files in os.walk(dir_path):
            # 构建输出文件路径
            for file in files:
                #放到对应的系列目录下，方便管理
                cur_dest_dir=os.path.join(dest_dir,OrgInfo(file).series_name)
                os.makedirs(cur_dest_dir,exist_ok=True)
                org_file_path =DYFileUnity.check_src_file(os.path.join(root, file))
                logger=logger_helper("检测场景切换",f"{org_file_path}->{dest_dir}")
                
                if self.file_manager.exists(cur_dest_dir,org_file_path):
                    logger.info("跳过","已存在")
                    continue
                 
                

                #拆分到对应的目录下
                self.split_by_change(org_file_path,cur_dest_dir)
                
                self.file_manager.update_dir(cur_dest_dir)
                logger.info("完成",f"{file} -> {cur_dest_dir}")
    def split_by_change(self,video_path,outdir="out"):
    
    
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
        
        pass


class ManerSplit(SplitBase):
    
    __base_time= datetime(1970, 1, 1)
    def __init__(self) -> None:
        super().__init__()
   
    @staticmethod
    def float_seconds_to_timedelta(seconds:int|float)->timedelta:
        # 获取当前时间
        second=int(seconds)
        millisecond=int((float(seconds)-second)*1000)
        # 计算时间差
        return timedelta(seconds=seconds,microseconds=millisecond)
    @staticmethod
    def float_seconds_to_datetime(seconds:int|float)->datetime:


        # 创建一个 timedelta 对象，表示时间间隔
        time_interval = ManerSplit.float_seconds_to_timedelta(seconds)
        # 将基准时间和时间间隔相加，得到新的 datetime 对象
        new_time = ManerSplit.__base_time + time_interval
        return new_time
    @staticmethod
    def str_to_time(time_str:str)->datetime:
        """
        将时间字符串转换为 datetime 对象
        :param time_str: 时间字符串，格式为 'HH:MM:SS.sss'
        :return: 对应的 datetime 对象
        """
        return datetime.strptime(time_str, '%H:%M:%S.%f')




    @staticmethod
    def add_seconds(time_obj, seconds:int|float):
        """
        给 datetime 对象增加指定的秒数
        :param time_obj: datetime 对象
        :param seconds: 要增加的秒数
        :return: 增加秒数后的 datetime 对象
        """
        return time_obj +ManerSplit.float_seconds_to_timedelta(seconds)


    @staticmethod
    def time_to_str(time_obj):
        """
        将 datetime 对象转换为时间字符串
        :param time_obj: datetime 对象
        :return: 对应的时间字符串，格式为 'HH:MM:SS.sss'
        """
        return time_obj.strftime('%H:%M:%S.%f')[:-3]

    @staticmethod
    def float_seconds_to_datetime_str(seconds:int|float)->str:

        return ManerSplit.time_to_str(ManerSplit.float_seconds_to_datetime(seconds))
        
    def precise_cut_seg(self,input_video:str,output_file:str,start_time:str,duration:str,bit_rate,r_frame_rate):
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
            return True
        except ffmpeg.Error as e:
            logger.error("失败",f"{e}")
        return False
    def maner_split_times(self,segs:list[str],end_time:float,step_time:float=.1)->list[tuple[str,str]]:
        end_time= ManerSplit.float_seconds_to_datetime(end_time)
        start_time=ManerSplit.float_seconds_to_datetime(0)
        time_lst=[]
        cur_time=ManerSplit.float_seconds_to_datetime(0)
        for split_time in segs:
            split_time=ManerSplit.float_seconds_to_datetime(split_time)
            if split_time<=cur_time:
                continue
            delta=(split_time-cur_time).total_seconds()
            time_lst.append((ManerSplit.time_to_str(cur_time),ManerSplit.float_seconds_to_datetime_str(delta)))
            cur_time=ManerSplit.add_seconds(split_time,step_time)

        if cur_time<end_time:
            time_lst.append((ManerSplit.time_to_str(cur_time),ManerSplit.float_seconds_to_datetime_str((end_time-cur_time).total_seconds())))
        
        
        return time_lst
    
    #若是不是绝度路径，则采用org_root作为根目录
    def check_path(self,org_path:str,root_path:str=dy_root.org_root):
        if not (Path(org_path).drive):
            org_path=os.path.join(root_path,org_path)
        return org_path
    
    
    def precise_cut(self,input_video, split_times, dest_dir="output"):
        logger=logger_helper("分割视频",f"{input_video}->{dest_dir}")
        logger.trace("开始",f"{split_times}")
        if self.file_manager.exists(dest_dir,input_video):
            logger.info("跳过","已存在")
            return
        
        
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
        
        split_lst=self.maner_split_times(split_times,duration,0.1)
        
        # 循环处理每个时间段
        for idx, seg in enumerate(split_lst, start=1):
            output_file =os.path.join(dest_dir,f"{src_name}-{name_latter}_{idx:03}.mp4") 
            start_time ,duration = seg
            bit_rate = video_stream.get('bit_rate', '5000k')
            r_frame_rate = video_stream.get('r_frame_rate', '30')
            if not self.precise_cut_seg(input_video=input_video,output_file=output_file,start_time=start_time,duration=duration,bit_rate=bit_rate,r_frame_rate=r_frame_rate):
                failure_lst.append(idx)
                
        if not failure_lst:
            logger.info("成功",update_time_type=UpdateTimeType.ALL)
            self.file_manager.update_dir(dest_dir)
        else:
            logger.error("失败",update_time_type=UpdateTimeType.ALL)
            
    #lst:[(input_video, splits)]
    def precise_cuts(self,lst:list[list[str,list[str]]],dest_dir):
        #确保唯一性
        results={}
        for item in lst:
            input_video, splits=item
            results[self.check_path(input_video,dy_root.org_root)]=splits

        for input_video,splits in results.items():

            self.precise_cut(input_video, splits, self.check_path(dest_dir,dy_root.dest_root))

        #dict_data:
        # [
        #     {
        #         "path": "鼋头渚夜樱_002.mp4",
        #         "split_times": [
        #             4.9,
        #             10.8,
        #             13.6,
        #             25
        #         ],
        #         "dest_dir": "1"
        #     },
        # ]
        
        

    def _precise_cuts_from_dict(self,data_lst):
        if not data_lst:
            return
        # results:
        # {"dest_dir":[[input_video, splits]]}
        results={}
        for item in data_lst:
            input_video, splits,dest=item["path"],item["split_times"],item["dest_dir"]

            input_video=self.check_path(input_video,dy_root.org_root)
            info=OrgInfo(input_video)
            if not dest:
                dest=dy_root.dest_sub_dir(info.series_name)
            else:
                dest=self.check_path(dest,dy_root.dest_root)
                
            results[dest]=results.get(dest,[])+[[input_video,splits]]

        
        #目录一样的放一起
        for dest,items in results.items():
            self.precise_cuts(items,dest)
            
            
    def load_split_info(self,json_file):
        if not os.path.exists(json_file):
            return
        with open(json_file, 'r', encoding='utf-8') as file:
            return  json.load(file)
        
            

    def precise_cuts_by_file(self,json_file)->dict:
        dict_info=self.load_split_info(json_file)
        self._precise_cuts_from_dict(dict_info)


    def split_videos(self):
        src_dir= dy_root.split_src_root
        dict_info=[]
        
        logger=logger_helper("获取手动拆分信息")
        for root, _, files in os.walk(src_dir):
            for file in files:
                if not file.lower().endswith('.json'):
                    continue
                logger.update_target(target=file)
                file_path=os.path.join(root,file)
                result= self.load_split_info(file_path)
                logger.info("成功",update_time_type=UpdateTimeType.STAGE)
                if result:
                    dict_info.extend(result)
        
        logger.update_target("手动拆分视频",f"合计{len(dict_info)}条信息")
        self._precise_cuts_from_dict(dict_info)
        logger.info("成功",update_time_type=UpdateTimeType.ALL)


    



def main():

    src_dir,dest_dir=dy_root.org_root,dy_root.dest_root

    logger=logger_helper(src_dir,dest_dir)
    logger.info("开始")
    
    #手动拆分
    logger.info("手动拆分",update_time_type=UpdateTimeType.STAGE)
    maner_split=ManerSplit()
    maner_split.split_videos()
    #自动拆分
    logger.info("自动拆分",update_time_type=UpdateTimeType.STAGE)
    auto_split=  AutoSplit()
    auto_split.split_videos()

    logger.info("拆分信息输出",update_time_type=UpdateTimeType.STAGE)
    SplitBase.save_split_xlsx()
    logger.info("成功",update_time_type=UpdateTimeType.ALL)
    
    
    
    
# 示例调用
if __name__ == "__main__":

    
    
    # lst=[
    #     ("鼋头渚夜樱_002.mp4",[4.9,10.8,13.6,25,]),
    #     ("鼋头渚夜樱_003.mp4",[2.3,5.5,7.3,8.8,11.7,14,16.9,19.5,22.1,25.4]),
    #     ("鼋头渚夜樱_004.mp4",[1.7,3.5,5.4,6.9,]),
    #     ("鼋头渚夜樱_005.mp4",[2.8,4.5,6.2,8.1,9.7,10.9,12.4,16.8,18.6,19.8,]),
    #     ("鼋头渚夜樱_006.mp4",[0.7,1.4,2.7,3.5,4.5,6.5,]),
    # ]
    
    # results=[{"path":item[0],"split_times":item[1],"dest_dir":"1"} for item in lst]
    # json.dump(results,open("split.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
    
    # exit()
    
    #版本问题，先按照系列名分目录；2025/3/29之后的不需要调用
    # classify_files_by_series(dest_dir,dest_dir)
    # exit()
    
    #获取目录文件夹中所有的MP4全路径（递归）
    # info=get_mp4_files_info(dest_dir)
    #筛选路径下的文件,拷贝到目标目录下
    # org_paths="""
    # 鼋头渚夜樱_001-1080x1920_002.mp4, 鼋头渚夜樱_001-1080x1920_004.mp4, 鼋头渚夜樱_001-1080x1920_006.mp4, 鼋头渚夜樱_001-1080x1920_008.mp4, 鼋头渚夜樱_003-720x1560_001.mp4, 鼋头渚夜樱_003-720x1560_003.mp4, 鼋头渚夜樱_003-720x1560_005.mp4, 鼋头渚夜樱_003-720x1560_007.mp4, 鼋头渚夜樱_004-720x1280_001.mp4, 鼋头渚夜樱_004-720x1280_003.mp4, 鼋头渚夜樱_004-720x1280_005.mp4
    # """
    # sub_dir="1"
    # HandleUsage.set_usage_segs(os.path.join(dest_dir,"鼋头渚夜樱"),org_paths,sub_dir)
    # exit()
    main()

    #保存用户选择.json
    # HandleUsage.save_usage("1")
    # HandleUsage.copy_by_json("1")