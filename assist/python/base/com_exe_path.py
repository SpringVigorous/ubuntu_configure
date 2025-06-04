import glob
import os
from path_tools import windows_path
def ffmpeg_path():
    # 获取环境变量 PATH 的值
    path_dirs = os.environ['PATH'].split(os.pathsep)
    lst=[]
    # 遍历 PATH 中的每个目录
    for path_dir in path_dirs:
        # 构造 ffmpeg.exe 的模式匹配路径
        ffmpeg_pattern = os.path.join(path_dir, 'ffmpeg.exe')
        # 使用 glob 模块搜索 ffmpeg.exe
        ffmpeg_paths = glob.glob(ffmpeg_pattern)
        if ffmpeg_paths:
            lst.append( windows_path(ffmpeg_paths[0]) )
    if lst: return lst[-1]
        
    print(f"ffmpeg 未找到，请查看本地是否安装了此软件或环境变量path是否存在对应目录")