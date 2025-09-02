import os
import argparse
from pathlib import Path
import os
import sys
__root_path__=Path(__file__).parent.parent.resolve()
sys.path.append(str(__root_path__ ))
sys.path.append( os.path.join(__root_path__,'base') )



from base import logger_helper,UpdateTimeType,replace_content_same_encode,replace_file_str,CoverType,copy_folder

root_src=Path(r"F:\test\ubuntu_configure\assist\python\c++\cmake_project")
org_macro_path = os.path.join(root_src, "hm_module_macro.h")
org_header_path = os.path.join(root_src, "sample.h")
org_cpp_path = os.path.join(root_src, "sample.cpp")

org_project_cmake_path = os.path.join(root_src, "project_makelists.txt")
org_module_cmake_path = os.path.join(root_src, "module_makelists.txt")

org_project_name="hm_project"
org_module_name="hm_module"
org_cpp_name="sample"

org_cmake_script_path=root_src/"cmake"
org_test_root=root_src/"test"
org_test_cmake_path = root_src/"test_makelists.txt"


def create_macro_replace_list(module_name):
    logger=logger_helper("创建模块替换列表",module_name)
    if not module_name:
        logger.error("异常","模块名称不能为空")
        raise Exception("模块名称不能为空")
        
    return [
            (org_module_name.upper(),module_name.upper()),
            (org_module_name,module_name),
                        ]

def create_cpp_replace_list(module_name,cpp_name):
    result=create_macro_replace_list(module_name)
    result.append((org_cpp_name,cpp_name))
    result.append(("SAMPLE",cpp_name.upper()))
    return result


def create_macro_file(module_name,header_dir:Path):
    dest_macro_path = header_dir/ f"{module_name}_macro.h"
    logger=logger_helper("创建宏文件",dest_macro_path)
    replace_list_tuple=create_macro_replace_list(module_name)
    replace_file_str(org_macro_path,dest_macro_path,replace_list_tuple,cover_type=CoverType.NO_COVER)
    logger.trace("完成",update_time_type=UpdateTimeType.STAGE)

def create_src_files(module_name,cpp_name:Path|str,header_dir,src_dir):
    
    if isinstance(cpp_name,str):
        cpp_name=Path(*cpp_name.split("."))
    
    name=cpp_name.name
    name_parts=cpp_name.parts    
    
    logger=logger_helper(f"创建{module_name}源文件",name)
    replace_list_tuple=[] if len(name_parts)==1 else [(f"{org_cpp_name}.h",f"{"/".join(name_parts)}.h")]
    replace_list_tuple.extend(create_cpp_replace_list(module_name,name))
    #.header
    dest_header_path = os.path.join(header_dir, f"{name}.h")
    replace_file_str(org_header_path,dest_header_path,replace_list_tuple,cover_type=CoverType.NO_COVER)
    # .cpp
    dest_cpp_path = os.path.join(src_dir, f"{name}.cpp")
    replace_file_str(org_cpp_path,dest_cpp_path,replace_list_tuple,cover_type=CoverType.NO_COVER)
    
    logger.info("完成",f"头文件{dest_header_path}\n源文件{dest_cpp_path}",update_time_type=UpdateTimeType.STAGE)
    
def create_cmakelist(dest_dir,org_path,replace_list_tuple):
    
    dest_path=os.path.join(dest_dir, "CMakeLists.txt")
    logger=logger_helper("创建CMakeLists.txt",dest_path)
    replace_file_str(org_path,dest_path,replace_list_tuple,cover_type=CoverType.NO_COVER)
    logger.trace("完成",update_time_type=UpdateTimeType.STAGE)


def create_structer(cur_dir)->tuple[Path]:
    logger=logger_helper("创建目录结构",cur_dir)
    
    cur_dir=Path(os.path.abspath(cur_dir))
    cur_name=cur_dir.name
    include_root_dir = cur_dir/ "include"
    src_dir =cur_dir/cur_dir/ "src"
    header_dir = include_root_dir/cur_name
    os.makedirs(header_dir,exist_ok=True)
    os.makedirs(src_dir,exist_ok=True)
    
    logger.info("完成",f"头文件目录{header_dir},源文件目录{src_dir}")
    return cur_dir,header_dir,src_dir

def create_module_structue(module_name:str,src_names:list|str=None,root_dir="./"):
    """创建模块目录结构并生成 CMakeLists.txt"""
    module_names=module_name.split(".")
    module_name:str=module_names[-1]
    dest_dir = os.path.join(root_dir,"src", *module_names)
    
    logger=logger_helper("创建模块",module_name)
    dest_dir,header_dir,src_dir = create_structer(dest_dir)
    
    replace_list_tuple=create_macro_replace_list(module_name)
    create_cmakelist(dest_dir,org_module_cmake_path,replace_list_tuple)
    
    
    create_macro_file(module_name,header_dir)
    if not src_names:
        return
    if isinstance(src_names,str):
        src_names=[src_names]
    for name in src_names:
        names=name.split(".")
        name=names[-1]
        sub_path=Path(*names)
        
        dest_header_dir=header_dir
        dest_header_dir
        has_sub_dir=len(names)>1
        
        dest_header_dir=Path(header_dir,*names[:-1]) if has_sub_dir else header_dir
        dest_src_dir=Path(src_dir,*names[:-1]) if has_sub_dir else src_dir

        if has_sub_dir:
            os.makedirs(header_dir,exist_ok=True)
            header_dir.mkdir(parents=True, exist_ok=True)
           
        create_src_files(module_name,sub_path,header_dir=dest_header_dir,src_dir=dest_src_dir)
    
    logger.trace("完成",f"目录{dest_dir}",update_time_type=UpdateTimeType.STAGE)

    
def create_project_structure(project_name="my_project",root_dir="./",):
    """创建项目目录结构并生成 CMakeLists.txt"""
    # 定义目录路径
    project_dir =Path(os.path.abspath(root_dir))/ project_name
    logger=logger_helper(f"创建项目{project_name}",project_dir)
    
    vcpkg_dir = os.path.join(project_dir,"3rd","vcpkg")
    os.makedirs(vcpkg_dir,exist_ok=True)
    
    os.makedirs(project_dir/"src",exist_ok=True)
    os.makedirs(project_dir/"cmake",exist_ok=True)
    os.makedirs(project_dir/"test"/"data",exist_ok=True)
    os.makedirs(project_dir/"config",exist_ok=True)
    
    # project_dir,*arg= create_structer(project_dir)
    
    replace_list_tuple=[("hm_project",project_name)]
    create_cmakelist(project_dir,org_project_cmake_path,replace_list_tuple)
    
    
    copy_folder(org_cmake_script_path,project_dir/"cmake")
    copy_folder(org_test_root,project_dir/"test")

    logger.info("完成",update_time_type=UpdateTimeType.STAGE)
def main():
    """解析命令行参数并执行创建逻辑"""
    parser = argparse.ArgumentParser(description="生成 CMake 项目结构")
    parser.add_argument("-r","--root", default="../", help="路径，默认当前目录")
    parser.add_argument("-p", "--project_name", default="", help="项目名称（为空表示不创建项目）")
    parser.add_argument("-m", "--module_name", default="", help="模块名称,可以为多个 用','分割（为空表示不创建模块）")
    parser.add_argument("-f", "--file_name", default="", help="源文件名称,若是有子目录用'.'区分,可以为多个 用','分割（为空表示不创建源文件）")
    parser.add_argument('-v', '--create_vxpkg', action='store_true', help='是否创建vcpkg目录结构')
    args = parser.parse_args()
    
    root_dir = args.root
    if not root_dir:
        root_dir = os.getcwd()
        
    project_name = args.project_name
    if project_name:
        create_project_structure(project_name,root_dir)
        #修正当前目录
        root_dir=os.path.join(root_dir,project_name)

    module_name = args.module_name.split(",") if args.module_name else []
    file_name = args.file_name.split(",") if args.file_name else []
        
    for module in module_name:
        create_module_structue(module,file_name,root_dir)



if __name__ == "__main__":
    main()
    
    
""" 
    1. cmd中运行
    cd /d F:/test/ubuntu_configure/assist/python
    2.  激活环境：
    myenv/Scripts/activate

    3.运行
    python c++/create_c_project.py-r F:/test  -p joy_project -m joy_utility -f interface.serialize_interface,interface.member_rw_interface,interface.bin_archive,interface.json_archive,interface.xml_archive
    python c++/create_c_project.py -r F:/test  -p joy_project -m joy_utility -f tools.string_tools,tools.xml_tools,tools.json_tools
"""