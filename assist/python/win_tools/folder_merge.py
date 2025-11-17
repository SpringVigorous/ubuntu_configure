import os
import shutil
import pandas as pd
from pathlib import Path

def merge_excel_files(src_excel_path, dst_excel_path, output_path):
    """
    合并两个Excel文件，按照sheet名称分类，合并同名sheet并按规则去重
    
    参数:
        src_excel_path: 源Excel文件路径
        dst_excel_path: 目标Excel文件路径
        output_path: 合并后的输出路径
    """
    try:
        # 读取源文件和目标文件的所有sheet
        src_sheets = pd.read_excel(src_excel_path, sheet_name=None)
        dst_sheets = pd.read_excel(dst_excel_path, sheet_name=None)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 获取所有唯一的sheet名称
            all_sheet_names = set(src_sheets.keys()) | set(dst_sheets.keys())
            
            for sheet_name in all_sheet_names:
                dfs_to_merge = []
                
                # 添加源文件的sheet（如果存在）
                if sheet_name in src_sheets:
                    dfs_to_merge.append(src_sheets[sheet_name])
                
                # 添加目标文件的sheet（如果存在）
                if sheet_name in dst_sheets:
                    dfs_to_merge.append(dst_sheets[sheet_name])
                
                if dfs_to_merge:
                    # 合并相同sheet名的DataFrame
                    if len(dfs_to_merge) == 1:
                        merged_df = dfs_to_merge[0]
                    else:
                        merged_df = pd.concat(dfs_to_merge, ignore_index=True)
                    
                    # 按href列去重，保留downloaded列值较大的行
                    if 'href' in merged_df.columns and 'downloaded' in merged_df.columns:
                        # 确保downloaded列是数值类型
                        merged_df['downloaded'] = pd.to_numeric(merged_df['downloaded'], errors='coerce')
                        # 按href分组，保留downloaded最大的行
                        merged_df = merged_df.sort_values('downloaded', ascending=False)
                        merged_df = merged_df.drop_duplicates('href', keep='first')
                    
                    # 将处理后的DataFrame写入到对应sheet
                    merged_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True
    except Exception as e:
        print(f"合并Excel文件时出错: {e}")
        return False

def copy_directory_with_excel_merge(src_dir, dst_dir, real_move=True):
    """
    复制目录结构，对xlsx文件进行特殊合并处理
    
    参数:
        src_dir: 源目录
        dst_dir: 目标目录
        real_move: 如果为False只打印操作，为True则实际执行
    """
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    
    # 确保目标目录存在
    if real_move and not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)
        print(f"创建目标目录: {dst_path}")
    
    # 用于记录操作
    operations = []
    
    # 遍历源目录
    for item in src_path.rglob('*'):
        if item.is_file():
            # 计算相对路径
            relative_path = item.relative_to(src_path)
            dst_file_path = dst_path / relative_path
            
            # 确保目标文件的父目录存在
            if real_move:
                dst_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 处理.xlsx文件
            if item.suffix.lower() == '.xlsx' and dst_file_path.exists():
                if real_move:
                    # 创建临时文件路径
                    temp_output = dst_file_path.with_suffix('.temp.xlsx')
                    
                    # 合并Excel文件
                    success = merge_excel_files(str(item), str(dst_file_path), str(temp_output))
                    
                    if success:
                        # 备份原文件
                        backup_path = dst_file_path.with_suffix('.backup.xlsx')
                        shutil.copy2(str(dst_file_path), str(backup_path))
                        
                        # 用合并后的文件替换原文件
                        shutil.move(str(temp_output), str(dst_file_path))
                        
                        # 删除临时文件
                        if temp_output.exists():
                            temp_output.unlink()
                        
                        operations.append(f"合并Excel: {relative_path} -> 已合并并备份原文件")
                    else:
                        operations.append(f"错误: 合并失败 {relative_path}, 使用覆盖复制")
                        shutil.copy2(str(item), str(dst_file_path))
                else:
                    operations.append(f"[模拟] 合并Excel: {relative_path} (目标文件已存在，将进行合并)")
            
            # 处理非.xlsx文件或目标不存在的.xlsx文件
            else:
                if real_move:
                    shutil.copy2(str(item), str(dst_file_path))
                    operations.append(f"复制文件: {relative_path}")
                else:
                    operations.append(f"[模拟] 复制文件: {relative_path}")
    
    return operations

def preview_directory_structure(directory):
    """预览目录结构"""
    print("目录结构预览:")
    dir_path = Path(directory)
    for item in dir_path.rglob('*'):
        level = len(item.relative_to(dir_path).parts) - 1
        indent = '  ' * level
        if item.is_dir():
            print(f"{indent}📁 {item.name}/")
        else:
            print(f"{indent}📄 {item.name}")

# 使用示例
if __name__ == "__main__":
    # 设置源目录和目标目录
    source_directory = "/path/to/source/folder/A"  # 请替换为实际的源目录路径
    destination_directory = "/path/to/destination/folder/B"  # 请替换为实际的目标目录路径
    
    print("=== 目录结构预览 ===")
    print("源目录结构:")
    preview_directory_structure(source_directory)
    
    if Path(destination_directory).exists():
        print("\n目标目录当前结构:")
        preview_directory_structure(destination_directory)
    
    print("\n" + "="*50)
    print("开始文件复制与合并操作")
    print("="*50)
    
    # 先进行模拟运行（不实际执行）
    print("=== 模拟运行 ===")
    simulated_operations = copy_directory_with_excel_merge(
        source_directory, 
        destination_directory, 
        real_move=False
    )
    
    for op in simulated_operations:
        print(op)
    
    # 用户确认后执行实际操作（取消注释以下代码）
    '''
    print("\n" + "="*50)
    print("开始实际文件操作")
    print("="*50)
    
    actual_operations = copy_directory_with_excel_merge(
        source_directory, 
        destination_directory, 
        real_move=True
    )
    
    for op in actual_operations:
        print(op)
    
    print("\n操作完成！")
    '''