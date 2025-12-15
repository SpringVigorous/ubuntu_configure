import glob
import os
from base.path_tools import windows_path
from base.com_log import global_logger


def exe_path_from_environment(exe_name:str):
   with global_logger().raii_target(f"查找{exe_name}的路径") as logger:
        # 获取环境变量 PATH 的值
        path_dirs = os.environ['PATH'].split(os.pathsep)
        lst=[]
        # 遍历 PATH 中的每个目录
        for path_dir in path_dirs:
            # 构造 ffmpeg.exe 的模式匹配路径
            ffmpeg_pattern = os.path.join(path_dir, exe_name)
            # 使用 glob 模块搜索 ffmpeg.exe
            ffmpeg_paths = glob.glob(ffmpeg_pattern)
            if ffmpeg_paths:
                lst.append( windows_path(ffmpeg_paths[0]) )
                
        if lst:
            logger.trace("成功",f"共有{len(lst)}个，结果如下：\n{'\n'.join(lst)}\n，取最后一个")
            return lst[-1]
            
        logger.error("失败",f"未找到，请查看本地是否安装了此软件或环境变量path是否存在对应目录")

def ffmpeg_path():
    return exe_path_from_environment('ffmpeg.exe')
