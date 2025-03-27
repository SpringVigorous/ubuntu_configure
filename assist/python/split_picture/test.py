import os
from collections import defaultdict

def classify_files(directory):
    # 初始化字典存储文件名（不含扩展名）与路径的映射
    dll_dict = defaultdict(list)
    lib_dict = defaultdict(list)

    # 遍历目录及子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 统一转换为小写以忽略大小写差异
            filename, ext = os.path.splitext(file)
            normalized_name = filename.lower()  # 按名称分组时忽略大小写

            if ext.lower() == '.dll':
                dll_dict[normalized_name].append(file_path)
            elif ext.lower() == '.lib':
                lib_dict[normalized_name].append(file_path)

    # 获取所有文件名集合
    dll_names = set(dll_dict.keys())
    lib_names = set(lib_dict.keys())

    # 分类逻辑
    common_names = dll_names & lib_names           # 同时存在.dll和.lib
    only_dll_names = dll_names - lib_names          # 只有.dll
    only_lib_names = lib_names - dll_names          # 只有.lib

    # 按类别整理结果
    result = {
        "both_dll_and_lib": {name: {"dll": dll_dict[name], "lib": lib_dict[name]} for name in common_names},
        "only_dll": {name: dll_dict[name] for name in only_dll_names},
        "only_lib": {name: lib_dict[name] for name in only_lib_names}
    }
    return result

def print_results(result):
    # 输出第一类：同时存在.dll和.lib
    print("===== 同时存在同名 DLL 和 LIB 的文件 =====")
    for name, files in result["both_dll_and_lib"].items():
        print(f"名称: {name}")
        print("  DLL路径:", '\n    '.join(files["dll"]))
        print("  LIB路径:", '\n    '.join(files["lib"]))
        print("-" * 50)

    # 输出第二类：只有.dll
    print("\n===== 只有 DLL 没有对应 LIB 的文件 =====")
    for name, paths in result["only_dll"].items():
        print(f"名称: {name}")
        print("  DLL路径:", '\n    '.join(paths))
        print("-" * 50)

    # 输出第三类：只有.lib
    print("\n===== 只有 LIB 没有对应 DLL 的文件 =====")
    for name, paths in result["only_lib"].items():
        print(f"名称: {name}")
        print("  LIB路径:", '\n    '.join(paths))
        print("-" * 50)

if __name__ == "__main__":
    target_dir = r"F:\3rd_repositories\传宗接代模拟器\模拟器v1.0"
    
    if os.path.exists(target_dir):
        classification = classify_files(target_dir)
        dlls=list(classification["both_dll_and_lib"].keys())
        dlls.extend(list(classification["only_dll"].keys()))
        
        libs=list(classification["only_lib"].keys())
        print("\n".join(map(lambda x:f"{x}.dll",  dlls)))
        print("_"*20)
        print("\n".join(map(lambda x:f"{x}.lib",  libs)))

        
        # print_results(classification)
    else:
        print("错误：指定的目录不存在！")