import glob
import os
from path_tools import normal_path
def ffmpeg_path():
    # 获取环境变量 PATH 的值
    path_dirs = os.environ['PATH'].split(os.pathsep)

    # 遍历 PATH 中的每个目录
    for path_dir in path_dirs:
        # 构造 ffmpeg.exe 的模式匹配路径
        ffmpeg_pattern = os.path.join(path_dir, 'ffmpeg.exe')
        # 使用 glob 模块搜索 ffmpeg.exe
        ffmpeg_paths = glob.glob(ffmpeg_pattern)
        if ffmpeg_paths:
            return normal_path(ffmpeg_paths[0]) 