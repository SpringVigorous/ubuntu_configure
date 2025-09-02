import subprocess
import os

def find_exe_path(exe_name:str)->str:
    """
    在系统的 PATH 环境变量中查找 vcpkg 或 vcpkg.exe 的真实全路径。
    返回:
        str: 如果找到，返回 vcpkg 的完整路径；否则返回 None。
    """
    # 根据操作系统选择合适的查找命令和可执行文件名
    if os.name == 'nt':  # Windows 系统
        command = ['where', f'{exe_name}.exe']
        # 也尝试查找无扩展名的 exe_name，以防万一
        command_no_ext = ['where', exe_name]
    else:  # Unix-like 系统 (Linux, macOS)
        command = ['which', exe_name]
        command_no_ext = command

    try:
        # 首先尝试查找 f'{exe_name}.exe' (Windows) 或 exe_name (Unix)
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
        paths = result.stdout.strip().splitlines()
        if paths:
            # 返回第一个找到的路径
            return paths[0]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # 如果没找到 f'{exe_name}.exe' 或命令执行失败，尝试查找无扩展名的 exe_name (主要针对Windows)
        try:
            result_no_ext = subprocess.run(command_no_ext, capture_output=True, text=True, check=True, timeout=30)
            paths_no_ext = result_no_ext.stdout.strip().splitlines()
            if paths_no_ext:
                return paths_no_ext[0]
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # 如果通过系统命令没找到，可以尝试手动检查 PATH 环境变量
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for dir_path in path_dirs:
        potential_path_win = os.path.join(dir_path, f'{exe_name}.exe')
        potential_path_nix = os.path.join(dir_path, exe_name)
        if os.path.isfile(potential_path_win):
            return potential_path_win
        if os.path.isfile(potential_path_nix):
            return potential_path_nix

    return None

if __name__ == '__main__':
    # 使用示例
    vcpkg_path = find_exe_path("vcpkg")
    if vcpkg_path:
        print(f"找到 vcpkg: {vcpkg_path}")
    else:
        print("未在 PATH 环境变量中找到 vcpkg 或 vcpkg.exe。")