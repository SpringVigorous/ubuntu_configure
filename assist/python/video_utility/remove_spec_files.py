import os
import re




from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import recycle_bin
def process_file_paths(directory):
    """
    获取指定目录下所有文件名中含有~1、~2等模式的文件路径，并返回去掉这些模式的全路径
    
    参数:
        directory: 要搜索的目录路径
        
    返回:
        一个字典，键是原始文件路径，值是处理后的文件路径
    """
    # 用于匹配~数字的正则表达式模式
    pattern = r'~(\d+)'
    
    # 存储结果的字典
    result = {}
    
    # 检查目录是否存在
    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是一个有效的目录")
        return result
    
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # 只处理文件，不处理目录
        if os.path.isfile(file_path):
            # 检查文件名中是否包含~数字模式
            if re.search(pattern, filename):
                # 去掉~数字部分
                new_filename = re.sub(pattern, '', filename)
                new_file_path = os.path.join(directory, new_filename)
                
                # 添加到结果字典
                result[file_path] = new_file_path
    
    return result

# 使用示例
if __name__ == "__main__":
    # 替换为你要搜索的目录路径
    target_directory = r"E:\video\20250804"
    
    # 处理文件路径
    processed_paths = process_file_paths(target_directory)
    
    # 打印结果
    if processed_paths:
        print("找到以下符合条件的文件:")
        for original, processed in processed_paths.items():
            recycle_bin(processed)
            # print(f"del /Q {processed} ")

    else:
        print(f"在 {target_directory} 中没有找到符合条件的文件")
