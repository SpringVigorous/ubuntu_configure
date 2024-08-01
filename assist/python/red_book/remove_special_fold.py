import os
import shutil
import argparse
import send2trash
import sys
import __init__
from base.com_log import logger as logger

#判断字符串是否在列表中,忽略大小写
def check_str_in_list(str,str_list):
    if str_list == None or len(str_list) < 1:
        return False
    lower_str = str.lower()
    return any(s.lower()  in lower_str for s in str_list)

#判断路径中 是否全部 不包含 排除的字符串,忽略大小写
def check_str_exclude_list(path,exclude_strs):
    if(exclude_strs == None or len(exclude_strs) < 1):
        return True
    return not check_str_in_list(path,exclude_strs)
    
    

def del_dir_file(cur_path,exclude_strs):
    if not os.path.exists(cur_path) or not check_str_exclude_list(cur_path,exclude_strs):
        return 
    
    expression_str="directory" if os.path.isdir(cur_path) else "file"
    
    try:
        cur_path = cur_path.replace("/","\\") #send2trash 需要目录中 使用\\而不是 /
        # shutil.rmtree(dir_path)
        send2trash.send2trash(cur_path)
        logger.error(f"Removed {expression_str} {cur_path}") 
    except FileNotFoundError:
        logger.error(f"Error: The {expression_str} '{cur_path}' does not exist.")
    except PermissionError:
        logger.error(f"Error: Permission denied when trying to move '{cur_path}' to the recycle bin.")
    except Exception as e:
        logger.error(f"Error removing {cur_path}: {e}")
    

def remove_directories_and_files(root_dir,del_folder,del_filter,exclude_strs):
    # 遍历目录树
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # 删除debug, release, ipch目录
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name).replace("\\" , "/")
            if(check_str_in_list(dir_path,del_folder)):
                del_dir_file(dir_path,exclude_strs)

        # 删除.suo和.db文件
        for file_name in files:
            # 使用splitext()函数分割路径
            file_path, file_extension = os.path.splitext(file_name)
            if check_str_in_list(file_extension,del_filter):
                file_path = os.path.join(root, file_name).replace("\\" , "/")
                del_dir_file(file_path,exclude_strs)


def unique(original_list):
    from collections import Counter
    counter = Counter(original_list)
    return list(counter.keys())


if __name__ == '__main__':
# 调用函数并传入目录路径

    parser = argparse.ArgumentParser(description='删除特定文件夹及特定类型的文件,放到回收站中\n eg:  -r  G:/练习集/C++/6.20 -d Debug,Release,ipch,.vs -f .sdf,.suo,.db -x 3rd[删除roott目录下所有Debug,Release,ipch,.vs文件夹及 排除3rd文件夹后所有的.sdf,.suo,.db文件,]')
    
    parser.add_argument('-r', '--root', type=str,  help='当前目录,默认（空、.、为赋值）为当前exe所在目录')
    parser.add_argument('-d', '--fold', type=str,  help='删除特定文件夹列表,默认（空、.、为赋值）为--root目录')
    parser.add_argument('-f', '--filter', type=str,  help='特定类型的文件列表')
    parser.add_argument('-x', '--exclude', type=str,  help='排除的特定名称列表')

    args = parser.parse_args()
    
    root_agrs = args.root
    if root_agrs == None or len(root_agrs) < 1 or root_agrs.strip() == ".":
        root_agrs = os.path.dirname(sys.argv[0]) 
    
    folder_agrs = args.fold.split(',') if not args.fold==None else ["."] #默认删除当前目录
    filter_agrs = args.filter.split(',') if not args.filter==None else []
    exclude_agrs = args.exclude.split(',') if not args.exclude==None else []
    
    folder_agrs=[ s.strip() if s.strip() != "." else root_agrs for s in folder_agrs]
    
    #添加默认值，严格来说 没必要
    # if len(folder_agrs) < 1 :
    #     folder_agrs == ["Debug","Release","ipch"]
    # if len(filter_agrs) < 1 :
    #     filter_agrs == [".sdf"]
    # if len(exclude_agrs) < 1 :
    #     exclude_agrs == ["3rd"]
    
    # remove_directories_and_files('your_{expression_str}_path_here',["Debug","Release","ipch"],[".suo",".db"]) 
    remove_directories_and_files(root_agrs,unique(folder_agrs),unique(filter_agrs),unique(exclude_agrs)) 
    
        
# 打包说明：pyinstaller --onefile --distpath exe -p . --distpath ./exe remove_special_fold.py
# 生成./exe/remove_special_fold.exe，运行即可

# exe运行
# remove_special_fold.exe -r  G:/练习集/C++/6.20 -d Debug,Release,ipch,.vs -f .sdf,.suo,.db -x 3rd


# 删除临时文件：remove_special_fold.exe -r F:/test/ubuntu_configure/assist/python/red_book/ -d exe,log,build
# 删除临时文件：remove_special_fold.exe -r "F:/test/ubuntu_configure/assist/python/red_book/" -d . -f .spec

#当前目录 cd F:/test/ubuntu_configure/assist/python/
# red_book/remove_special_fold.py -r  F:/test/ubuntu_configure/assist/python/ -d logs,exe,log,build -f .spec,.log

