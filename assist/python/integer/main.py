import argparse
import os
import sys
from functools import partial
import json
import sys
from pathlib import Path
# 将当前脚本所在项目的根路径添加到sys.path
project_root =str(Path(__file__).resolve().parent.parent)
for module_path in [project_root,os.path.join(project_root,"base")]:
    if not module_path in sys.path:
        sys.path.insert(0,module_path)
import base.string_tools as st
import base.com_decorator as cd 
import base.pipe_tools as  ppt 
import base.file_tools as  ft 
import base.check_file_encode as fe
import base.fold_tools as fo
import base.path_tools as pt
from base.com_log import logger as logger
import base.com_decorator as dr 
@dr.exception_decorator
def operate_imp(source_path,dest_path,dest_encoding,operate_func):
    source_encoding = fe.detect_encoding(source_path)
    if len(dest_path)==0:
        dest_path=source_path
    ft.operate_content_diff_encode(source_path,dest_path,source_encoding,dest_encoding,operate_func)
    logger.info(f"[{source_path}]->[{dest_path}]:{source_encoding}->{dest_encoding}")


if __name__ == '__main__':
        # 创建ArgumentParser对象，其中description参数用于提供程序的简短描述
    parser = argparse.ArgumentParser(description='整合工具合集')

    # 添加一个位置参数（positional argument），这里假设我们需要用户提供一个文件名
    parser.add_argument('-i', '--input', type=str,  help='输入文件(夹)的路径')

    # 添加一个可选参数（optional argument）--output或-o，后面跟随一个值，表示输出文件的路径
    parser.add_argument('-o', '--output', type=str, default='', help='输出文件的路径:为空时代表和源文件路径')


    parser.add_argument('-c', '--encoding', default='', help='指定编码模式,为空则使用源文件编码:gbk，gb2312,ascii,utf8,utf-8-sig')

    # 添加一个可选参数（optional argument）--output或-o，后面跟随一个值，表示输出文件的路径
    parser.add_argument('-r', '--replace_args', type=str,  help='替换参数文件的路径') 
    

    # 添加一个可选参数（optional argument）--output或-o，后面跟随一个值，表示输出文件的路径
    parser.add_argument('-f', '--filter', type=str,  help='筛选指定类型:多个值时以“;”分割;为空时取消该筛选类型 ') 
                                                                                                                 
    # 添加一个布尔标志（boolean flag）--verbose或-v，无须指定值，存在即为True
    parser.add_argument('-v', '--verbose', action='store_true', help='开启详细模式')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    # 解析命令行参数并存储到args变量中
    args = parser.parse_args()

    # 使用解析后的参数执行相应的操作
    value= args.verbose
    
    input_agrs = args.input
    if input_agrs is None or  not os.path.exists(input_agrs):
        logger.error(f"文件{input_agrs}不存在")
        sys.exit(0)
    # if len(args.output)>0 else input_agrs
    output=args.output
       
    is_file= os.path.isfile(input_agrs)
    has_replace_args=args.replace_args is not None and os.path.exists(args.replace_args)
    dest_encoding=args.encoding 
    has_encoding =len(args.encoding )>0
    operate_funcs=[]
    filter_agrs=args.filter.split(";") if args.filter is not None else []
    has_filter=len(filter_agrs)>0
    if has_replace_args:
        with open(args.replace_args, 'r') as file:
    # 使用json.load()方法将文件内容解析为Python对象（通常是字典）
            data= json.load(file)
        tupple_vals=data["replace_args"]
        if len(tupple_vals)>0:
            operate_funcs.append(partial(st.replace_list_tuple_str,replace_list_tuple=tupple_vals))
    
    operate_func=None
    if len(operate_funcs)>0:
        operate_func= lambda content: ppt.pipe(content, *operate_funcs)
    def get_real_name(name:str):
         return operate_func(name) if operate_func is not None else name
    
    
    if is_file: 
        operate_imp(input_agrs,get_real_name(output),dest_encoding,operate_func)
    elif os.path.isdir(input_agrs):
        org_base_dir=os.path.basename(input_agrs)
        
        folder_name = get_real_name(org_base_dir)
        output=os.path.join(output,folder_name)
        if output==folder_name :
            output=input_agrs
        if not pt.path_equal(input_agrs,output):
            fo.clear_folder(output)
        for root, dirs, files in os.walk(input_agrs):
            # 构建输出文件路径
            relative_path = get_real_name(os.path.relpath(root, input_agrs))
            dest_dir_path = os.path.abspath(os.path.join(output, relative_path)) 
            for file in files:
                if has_filter and  not any(file.endswith(ext) for ext in filter_agrs):
                   continue
                org_file_path = os.path.join(root, file)
                os.makedirs(dest_dir_path, exist_ok=True)
                dest_file_path=os.path.join(dest_dir_path, get_real_name(file))

                operate_imp(org_file_path, dest_file_path,dest_encoding,operate_func)


# 使用方法
# python main.py -i F:/test/ubuntu_configure/assist/c++/im_export_macro -o F:/test/test_c -r F:/test/ubuntu_configure/assist/python/integer/replace_folders_json_copy_copy.json 
    
# python main.py -i F:/test/co_async/co_async -c utf-8-sig -f .hpp;.cpp;.h;.cxx;.hxx;.c;.cc;.hh;.inl