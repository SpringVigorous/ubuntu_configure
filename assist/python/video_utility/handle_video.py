
import os


from pathlib import Path
import sys




from base import rotate_video_by_metadata,mp4_files,pool_executor,add_first_frame_as_cover,logger_helper,UpdateTimeType,ffmpeg_extract
from split_video import ManerSplit
from collections.abc import Iterable
#文件列表操作
def handle_lst_video(file_lst,func, pool_count:int=0):
    lst=[(func,file_path) for file_path in file_lst]
    pool_executor(lst,pool_count)

#文件夹操作
def handle_dir_video(dir_path,func, is_recurse=False,pool_count:int=0):
    loggger=logger_helper(f"文件夹操作:{func}",dir_path)
    files=mp4_files(dir_path,is_recurse=is_recurse)   
    handle_lst_video(files,func,pool_count)
    loggger.info("完成",update_time_type=UpdateTimeType.ALL)
#旋转视频
def rotate_video(dir_path,is_recurse=False):
    handle_dir_video(dir_path,rotate_video_by_metadata,is_recurse,3)

#添加封面
def add_cover(dir_path,is_recurse=False):
    handle_dir_video(dir_path,add_first_frame_as_cover,is_recurse,3)
    
from base import get_video_duration,split_pairs_diff,new_path_by_rel_path,get_folder_path_by_rel
#分割视频
def split_videos(file_path,out_dir,split_times:Iterable[int|float]):
    duration=get_video_duration(file_path)
    if not duration: return
    time_lst=split_pairs_diff(0,duration,split_times)
    lst=[]
    cur_path=Path(file_path)
    for i,(start,duration) in enumerate(time_lst):
        
        dest_path=os.path.join(out_dir,cur_path.with_stem(f"{cur_path.stem}_{i+1:02}").name)
        lst.append( (ffmpeg_extract,
                   file_path,
                   dest_path,
                   start,
                   duration))
    
    

    pool_executor(lst,4)
    
    
    # impl=ManerSplit()
    # impl.maner_split_times()
    # impl.precise_cut()

    # 示例：从30秒截取20秒（零转码）
    # ffmpeg_extract(r"E:\video\20250804\video_20250804_162015.mp4", r"E:\video\20250804\split\video_20250804_162015-1080x1920_001.mp4", 0, 6)
def main():
    file_path=r"E:\video\20250804\video_20250804_162015.mp4"
    out_dir=os.path.join(get_folder_path_by_rel(file_path,0),"split")
    os.makedirs(out_dir,exist_ok=True)
    split_videos(r"E:\video\20250804\video_20250804_162015.mp4",out_dir,[6,12,18,24,30])
    return
    video_dir=r"E:\video\20250804\split"
    # rotate_video_by_metadata(os.path.join(video_dir,"video_20250805_124626.mp4"))
    # return
    # rotate_video(video_dir,is_recurse=False)
    # add_cover(video_dir,is_recurse=False)
    

    
    
if __name__ == '__main__':
    main()