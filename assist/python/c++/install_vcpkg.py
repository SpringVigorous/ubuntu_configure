import subprocess
import sys
import os
from datetime import datetime

import re
from pathlib import Path

import sys






from base import logger_helper,UpdateTimeType,find_exe_path


def vcpkg_list_from_file(package_list_file:str):
    pattern=re.compile(r"^(\S+:\S+)\s+")
    # 读取包列表文件
    packages_to_install=[]
    try:
        with open(package_list_file, 'r') as f:
            # 读取每一行，忽略空行和以'#'开头的注释行
            for line in f.readlines():
                line_txt=line.strip() 
                if not line_txt or line.startswith('#'):
                    continue
                match = pattern.match(line_txt)
                if match:
                    packages_to_install.append(match.group(1))
            
    except FileNotFoundError:
        print(f"错误：找不到包列表文件 '{package_list_file}'。请创建该文件并每行写入一个包名。")
    
    return packages_to_install

#缓存原装的包列表
_installed_list=[]
def installed_list(vcpkg_exe_path:str,install_root:str=None):
    
    if not _installed_list:
        # 检查包是否已经安装
        check_installed_cmd = [vcpkg_exe_path, "list"]
        add_root_flag(check_installed_cmd,install_root)
        try:

            check_installed_cmd=" ".join(check_installed_cmd)

            check_result = subprocess.run(check_installed_cmd,  capture_output=True, text=True, check=True, timeout=180)

            _installed_list= check_result.stdout
        except:
            pass
    return _installed_list

def root_flag(install_root:str=None):
    return f'--x-install-root="{install_root}"' if install_root else ""

def add_root_flag(cmd:list,install_root:str=None):
    cmd.append(root_flag(install_root))
    
    

def install_vcpkg_package(vcpkg_exe_path:str,package_info:str,install_root:str=None,install_timeout:int = 1800)->bool:
    logger=logger_helper("安装包",package_info)

    # 检查包是否已经安装
    check_installed_cmd = [vcpkg_exe_path, "list"]
    add_root_flag(check_installed_cmd,install_root)

        
    try:
        logger.stack_target(f"检查安装状态-{package_info}",check_installed_cmd)
        if package_info in installed_list(vcpkg_exe_path,install_root):
            logger.trace("已安装，跳过",update_time_type=UpdateTimeType.STAGE)
            return True
    except:
        pass
    finally:
        logger.pop_target()  
        

    # 安装包
    install_cmd = [vcpkg_exe_path, "install", package_info]
    add_root_flag(install_cmd,install_root)
    install_cmd=' '.join(install_cmd)
    logger.trace(f"执行命令: {install_cmd}", update_time_type=UpdateTimeType.STAGE)

    try:
        logger.stack_target(f"安装{package_info}",install_cmd)

        # 执行安装命令，并将标准输出和标准错误直接重定向到日志文件
        process = subprocess.run(install_cmd,capture_output=True,text=True,check=True,timeout=install_timeout)
        if process.returncode == 0:
            logger.trace("成功",f"\n{process.stdout}\n",  update_time_type=UpdateTimeType.STAGE)
            return True
        else:
            logger.trace("失败",f"返回码: {process.returncode}。请查看日志详情。",update_time_type=UpdateTimeType.STAGE)
            return False

    except subprocess.TimeoutExpired:
        logger.trace("失败",f"超时（超过 {install_timeout} 秒），进程被终止。",update_time_type=UpdateTimeType.STAGE)
        return False

    except Exception as e:
        logger.trace("异常",f"{e}",update_time_type=UpdateTimeType.STAGE)
        return False

from collections.abc import Iterable
def install_vcpkg_packages(vcpkg_exe_path:str,package_infos:Iterable[str],install_root:str=None,install_timeout:int = 1800)->list[str]:
    if not package_infos:
        return
    logger=logger_helper("安装包列表",",".join(package_infos))    
    failed_installations = [] # 记录安装失败的包

    for pkg in package_infos:
        if not install_vcpkg_package(vcpkg_exe_path, pkg,install_root,install_timeout):
            failed_installations.append(pkg)

    if not failed_installations:
        logger.info("完成","所有包安装成功！",update_time_type=UpdateTimeType.ALL)
    else:
        logger.error("部分成功",f"以下包安装失败：\n{'\n'.join(failed_installations)}\n",update_time_type=UpdateTimeType.ALL)
    
    return failed_installations

    # install_timeout  # 每个包安装的超时时间（秒），例如1800秒=30分钟
def intall_vcpkg_from_list_file(vcpkg_exe_path:str,package_list_file:str,install_root:str=None,install_timeout:int = 1800):
    # 配置区域：请根据你的实际情况修改这些变量
    logger=logger_helper("从文件安装vcpkg包",package_list_file)
    packages_to_install=vcpkg_list_from_file(package_list_file)
    if not packages_to_install:
        logger.error("失败","文件中没有找到有效的包名。")
        return

    logger.update_target(detail=f"目标包列表: {', '.join(packages_to_install)}\n")

    logger.trace(f"开始安装包...",update_time_type=UpdateTimeType.STAGE)
    failed_installations = install_vcpkg_packages(vcpkg_exe_path,packages_to_install,install_root,install_timeout) # 记录安装失败的包
    
     



if __name__ == "__main__":
    vcpkg_exe_path = find_exe_path("vcpkg")  # 替换为你的 vcpkg.exe 完整路径
    package_list_file = r"F:\test\joy_project\3rd\vcpkg\installed_packages.txt"  # 包含包列表的文本文件，每行一个包
    install_root=r"F:/test/joy_project/3rd/vcpkg/installed"
    #通过文件安装包
    intall_vcpkg_from_list_file(vcpkg_exe_path,package_list_file,install_root)
    
    #单独安装一个包
    # install_vcpkg_package(vcpkg_exe_path,"magic-enum:x64-windows",install_root)
    
    
    # cmd=r'F:\vcpkg\vcpkg.exe list --x-install-root="F:/test/joy_project/3rd/vcpkg/installed" > "F:/test/joy_project/3rd/vcpkg/installed/temp_list.txt"'
    # cmd=r'F:\vcpkg\vcpkg.exe list --x-install-root="F:\test\joy_project\3rd\vcpkg\installed"'
    # process = subprocess.run(cmd,capture_output=True,text=True,check=True, timeout=180)
    # print(process.stdout)
    
    
    # cmd=r'F:\vcpkg\vcpkg.exe install magic-enum:x64-windows --x-install-root="F:\test\joy_project\3rd\vcpkg\installed"'
    # process = subprocess.run(cmd,capture_output=True,text=True,check=True, timeout=180)
    # print(process.stdout)
    
    
    # process = subprocess.run(cmd.replace("\\","/"),capture_output=True,text=True,check=True, timeout=180)
    # print(process.stdout)


    