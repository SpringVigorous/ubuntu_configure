import os
import send2trash
import sys
from pathlib import Path



from base import logger_helper,path_equal
#针对视频中添加了 广告片段，根据特定 名称删除（有局限性，用时需要核对）
#是否递归
def move_numeric_files_to_recycle(root_dir,min_num=74,max_num=80,is_recursive=False):
    """
    遍历指定目录的子目录，将文件名(不含后缀)为74-80之间数值的文件移动到回收站
    
    参数:
        root_dir: 要遍历的根目录
    """
    
    logger=logger_helper(f"在{root_dir}下 删除特定名称的文件",f"min:{min_num} max:{max_num}")
    
    # 检查根目录是否存在
    if not os.path.exists(root_dir):
        print(f"错误: 目录 {root_dir} 不存在")
        return
    
    # 遍历所有子目录和文件
    for dirpath, _, filenames in os.walk(root_dir):
        if not is_recursive and not path_equal(Path(dirpath).parent ,root_dir):
            continue
        
        for filename in filenames:
            # 分离文件名和后缀
            name_without_ext = os.path.splitext(filename)[0]
            
            # 尝试将文件名转换为数字
            try:
                num = float(name_without_ext)
                # 检查是否为整数且在min_num-max_num范围内
                if num.is_integer() and min_num <= num <= max_num:
                    file_path = os.path.join(dirpath, filename)
                    # 移动到回收站
                    send2trash.send2trash(file_path)
                    logger.trace("已移动到回收站",file_path)
            except ValueError:
                # 文件名不是数字，跳过
                continue

if __name__ == "__main__":
    # 目标根目录
    target_directory = r"F:\worm_practice\player\temp"
    move_numeric_files_to_recycle(target_directory,74,80)

