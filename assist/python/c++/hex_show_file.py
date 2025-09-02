def file_to_hex_lines(file_path):
    """
    以UTF-8-SIG编码打开文件，按行读取并将每行内容转换为十六进制
    
    参数:
        file_path: 文件路径
    """
    try:
        # 以UTF-8-SIG编码打开文件，自动处理BOM
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            line_number = 1
            for line in file:
                # 保留换行符，因为strip()会去除它
                # 将字符串编码为字节，再转换为十六进制
                hex_str = line.encode('utf-8').hex(sep=" ")
                print(" ".join(line))
                print(f"行 {line_number}: {hex_str}")
                line_number += 1
                
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到")
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")

# 示例用法
if __name__ == "__main__":
    # 替换为你的文件路径
    target_file = r"F:\test\ubuntu_configure\assist\python\c++\cmake_project\hruntime_class.h"
    file_to_hex_lines(target_file)
