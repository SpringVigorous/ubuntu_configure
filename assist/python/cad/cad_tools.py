import winreg

import win32gui
import win32con
import time
import subprocess
import os

import psutil

def is_exe_running(exe_name):
    """
    检查指定名称的 EXE 是否正在运行
    参数:
        exe_name (str): 可执行文件名（如 "acad.exe"）
    返回:
        bool: 是否正在运行
    """
    # 处理大小写问题（Windows 不区分大小写）
    exe_name_lower = exe_name.lower()
    
    for process in psutil.process_iter(['name', 'exe']):
        try:
            # 检查进程名
            name=process.info['name']
            if name and exe_name_lower == name.lower():
                return True
            
            # 检查完整路径
            full_path = process.info['exe']
            if full_path and exe_name_lower in full_path.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # 忽略已结束或无法访问的进程
            pass
    
    return False


def find_cad_dirs_by_reg():
    base_key = winreg.HKEY_LOCAL_MACHINE
    base_path = r"SOFTWARE\Autodesk\UPI2"
    access = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
    
    try:
        with winreg.OpenKey(base_key, base_path, 0, access) as upi2_key:
            # 遍历 UPI2 下的所有子键（GUID）
            index = 0
            found_dirs = []
            
            while True:
                try:
                    # 获取子键名称和其句柄
                    subkey_name = winreg.EnumKey(upi2_key, index)
                    index += 1
                    
                    # 打开子键并查找 INSTALLDIR
                    try:
                        subkey_path = f"{base_path}\\{subkey_name}"
                        with winreg.OpenKey(base_key, subkey_path, 0, access) as subkey:
                            try:
                                value, reg_type = winreg.QueryValueEx(subkey, "INSTALLDIR")
                                
                                found_dirs.append(value)
                                
                                # # 将找到的值添加到列表
                                # found_dirs.append({
                                #     "guid": subkey_name,
                                #     "path": value,
                                #     "full_path": f"{subkey_path}\\INSTALLDIR"
                                # })
                            except FileNotFoundError:
                                # INSTALLDIR 值不存在，跳过
                                pass
                    except (PermissionError, FileNotFoundError, OSError):
                        # 无法打开子键，跳过
                        continue
                
                except OSError:
                    # 已遍历所有子键，退出循环
                    break
            
            return list(filter(lambda x:bool(x),list(dict.fromkeys(found_dirs)))) if found_dirs else []
    
    except FileNotFoundError:
        print("错误：基础注册表路径不存在")
        return []
    except PermissionError:
        print("错误：权限不足（请以管理员身份运行）")
        return []
    except Exception as e:
        print(f"未知错误: {e}")
        return []

def start_exe_hidden(exe_path, args=None):
    """
    启动 .exe 程序并完全隐藏窗口
    
    参数:
        exe_path (str): .exe 文件的完整路径
        args (list): 命令行参数列表
    """
    if args is None:
        args = [            
            "/nologo",  # 禁用启动logo
            # "/b", r"C:\Scripts\startup.scr",  # 运行启动脚本
            # "/p", r"C:\Profiles\MyProfile.arg",  # 指定配置文件
            "/nohardware" , # 禁用硬件加速（减少启动资源）
            ]
    
    # Windows 平台
    if os.name == 'nt':
        # 设置启动信息
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = win32con.SW_MINIMIZE  # 0 = SW_HIDE
        
        subprocess.Popen(
            [exe_path] + args,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            close_fds=True
        )
    # Unix/Linux 平台
    else:
        # 使用 nohup 并在后台运行，不显示任何窗口
        command = f'nohup "{exe_path}" {" ".join(args)} > /dev/null 2>&1 &'
        subprocess.Popen(command, shell=True)


def find_autocad_installation() -> str:
    """自动查找 AutoCAD 安装路径"""
    # 常见安装路径
    dirs=find_cad_dirs_by_reg()
    for cur_dir in dirs:
        path=os.path.join(cur_dir, "acad.exe")
        if os.path.exists(path):
            return path
    return None


def start_autocad():
    
    exe_to_check = "acad.exe"  # 替换为你要检查的 EXE 名称
    if is_exe_running(exe_to_check):
        return
    exe_path =find_autocad_installation()
    start_exe_hidden(exe_path)
    time.sleep(10)

if __name__ == "__main__":
    # 查找并显示结果
    install_dirs = find_cad_dirs_by_reg()
    if install_dirs:
        print("找到的 INSTALLDIR 值:")
        for i, item in enumerate(install_dirs, 1):
            print(f"{i}. path: {item}")

    exe_path =find_autocad_installation()
    start_exe_hidden(exe_path)
    print(1)
