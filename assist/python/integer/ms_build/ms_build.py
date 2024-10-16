import subprocess
import os


"""
msbuild_command = [
    'msbuild',
    solution_path,
    '/p:Configuration=Debug',
    '/p:Platform=x64',
    '/v:d',
    '/fl',
    f'/flp:logfile={log_file_path}'
]

参数详解
    msbuild:

    这是 Microsoft Build Engine (MSBuild) 的命令行工具，用于构建基于 MSBuild 的项目和解决方案。
YourSolution.sln:

    这是你想要构建的解决方案文件的路径。解决方案文件（.sln）是一个包含多个项目文件（.csproj, .vcxproj 等）的文件，定义了整个解决方案的结构。
/p:Configuration=Debug:

    /p: 是 Property 的缩写，用于设置项目的属性。
    Configuration=Debug 指定了构建配置为 Debug。常见的构建配置有 Debug 和 Release，分别用于调试和发布版本。
/p:Platform=x64:

    同样使用 /p: 设置项目的属性。
    Platform=x64 指定了目标平台为 x64。常见的平台有 x86（32位）和 x64（64位）。
/v:d:

    /v: 是 Verbosity 的缩写，用于设置日志的详细程度。
    d 表示 Detailed，即详细模式。其他可用的详细程度选项包括：
    q（Quiet）：仅显示错误。
    m（Minimal）：显示错误、警告和消息。
    n（Normal）：默认详细程度。
    d（Detailed）：详细模式，显示更多详细信息。
    diag（Diagnostic）：诊断模式，显示最详细的日志信息。
/fl:

    /fl 是 FileLogger 的缩写，表示启用文件日志记录。
    这个参数告诉 MSBuild 将日志输出到文件中，而不是仅仅显示在控制台。
/flp:logfile=YourSolution.log:

    /flp: 是 FileLoggerParameters 的缩写，用于设置文件日志记录的参数。
    logfile=YourSolution.log 指定了日志文件的路径和名称。在这个例子中，日志将被保存到 YourSolution.log 文件中。"""
    

def ms_build(solution_path,config, log_file_path):
    
    # 定义解决方案文件路径

    # 定义 MSBuild 命令参数
    msbuild_command = [
        r'D:\Soft\VS2022\MSBuild\Current\Bin\msbuild.exe',
        solution_path,
        f'/p:Configuration={config}',
        '/p:Platform=x64',
        '/v:m',
        '/fl',
        f'/flp:logfile={log_file_path}'
    ]

    # 执行 MSBuild 命令
    try:
        # 创建子进程并捕获输出
        print(" ".join(msbuild_command))
        result = subprocess.run(msbuild_command, check=True, text=True, capture_output=True)
        
        # 输出命令的标准输出
        print("Standard Output:")
        print(result.stdout)
        
        # 输出命令的标准错误
        print("Standard Error:")
        print(result.stderr)
        
        # 检查日志文件是否生成成功
        if os.path.exists(log_file_path):
            print(f"编译日志已成功生成到 {log_file_path}")
        else:
            print(f"编译日志生成失败，请检查路径 {log_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"MSBuild 命令执行失败: {e}")
        print(f"返回码: {e.returncode}")
        print(f"标准输出: {e.output}")
        print(f"标准错误: {e.stderr}")
    except Exception as e:
        print(f"发生错误: {e}")
        
def main():
    
    root=r"F:\test\cmake_project\build"
    solution="test_cmake.sln"
    config="Debug"
        # 定义解决方案文件路径
    solution_path = os.path.join(root, solution)

    # 定义日志文件路径
    log_file_path = os.path.join(root, config,"logs", "ms_build.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    ms_build(solution_path=solution_path,config=config, log_file_path=log_file_path)

if __name__ == '__main__':
    main()