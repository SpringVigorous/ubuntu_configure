import os
import shutil
import sys
import ctypes
from ctypes import wintypes

def is_admin():
    """检查当前进程是否拥有管理员权限"""
    try:
        # 调用 Windows API 检查权限（仅 Windows 有效）
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员身份重新启动当前脚本（弹出 UAC 授权窗口）"""
    # 获取当前脚本的路径
    script_path = sys.argv[0]
    # 调用 ShellExecuteW 函数，请求管理员权限启动脚本
    ctypes.windll.shell32.ShellExecuteW(
        None,                  # 父窗口句柄（None 表示无父窗口）
        "runas",               # 操作类型："runas" 表示以管理员身份运行
        sys.executable,        # 要启动的程序（Python 解释器路径）
        script_path,           # 要传递的参数（当前脚本路径）
        None,                  # 工作目录（None 表示当前目录）
        1                      # 窗口显示方式（1 表示正常显示）
    )

def delete_directory(target_dir):
    """删除指定目录及其内容，返回清理结果信息"""
    if not os.path.exists(target_dir):
        return f"目录不存在，跳过：{target_dir}"
    
    try:
        # 递归删除目录（强制删除只读文件）
        shutil.rmtree(target_dir, ignore_errors=False, onerror=None)
        if not os.path.exists(target_dir):
            return f"删除成功：{target_dir}"
        else:
            return f"删除失败：{target_dir}（原因未知）"
    except PermissionError:
        return f"删除失败：{target_dir}（权限不足，请以管理员身份运行）"
    except OSError as e:
        if "被另一个程序使用" in str(e) or "正由另一进程使用" in str(e):
            return f"删除失败：{target_dir}（文件被占用，请关闭 VS Code 后重试）"
        else:
            return f"删除失败：{target_dir}（错误：{str(e)}）"

def main():
    # 1. 先检查权限，非管理员则自动请求
    if not is_admin():
        print("检测到当前无管理员权限，正在请求 UAC 授权...")
        run_as_admin()
        # 授权后会启动新的管理员进程，当前进程可退出
        sys.exit(0)
    
    # 2. 权限验证通过，执行清理流程
    print("=" * 60)
    print("✅ 已获取管理员权限，开始执行 VS Code 清理")
    print("注意：请确保 VS Code 已完全关闭（包括所有窗口）")
    print("=" * 60)
    input("按 Enter 键继续...")
    
    
    vscode_cpptools_dir = os.path.join(os.getenv("APPDATA"), r"Local\Microsoft\vscode-cpptools")
    delete_directory(vscode_cpptools_dir)
    # 定义 VS Code 主目录（对应 AppData\Roaming\Code）
    vscode_dir = os.path.join(os.getenv("APPDATA"), "Code")
    
    
    
    # 定义需要清理的目录列表（相对路径）
    clean_dirs = [
        "Cache",
        "Logs",
        "Backups",
        os.path.join("User", "History")
    ]
    
    # 循环清理每个目录
    print("\n开始清理...\n")
    for dir_rel in clean_dirs:
        dir_full = os.path.join(vscode_dir, dir_rel)
        result = delete_directory(dir_full)
        print(result)
    
    # 清理完成
    print("\n" + "=" * 60)
    print("全部清理操作完成！")
    print("如有删除失败项，请检查：1. VS Code 是否完全关闭 2. 目录是否被其他程序占用")
    print("=" * 60)
    input("按 Enter 键退出...")

if __name__ == "__main__":
    main()