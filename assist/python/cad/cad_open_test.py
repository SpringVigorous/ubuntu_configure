import os
from pyautocad import Autocad
import pythoncom



def print_entities_in_folder(folder_path):
    # 连接AutoCAD（需提前打开AutoCAD软件）
    pythoncom.CoInitialize()  # 初始化COM组件
    acad = Autocad(create_if_not_exists=True)
    app = acad.app
    
    # 获取文件夹下所有DWG文件
    dwg_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.dwg')]
    
    entity_type_names = set()
    layout_type_names = set()
    
    for dwg_file in dwg_files:
        file_path = os.path.join(folder_path, dwg_file)
        print(f"\n处理文件: {dwg_file}")
        
        try:
            # 打开DWG文件
            doc = app.Documents.Open(file_path)
            acad.prompt(f"Opened: {dwg_file}\n")
            
            # 遍历模型空间所有实体
            for entity in acad.iter_objects():
                entity_type_names.add(entity.ObjectName)

                
            # 2. 打印图纸空间实体类型（PaperSpace）
            print("--- 图纸空间实体 ---")
            layouts = doc.Layouts
            for layout in layouts:
                # 获取布局对应的图纸空间Block[7,8](@ref)
                block = layout.Block
                for entity in block:
                    layout_type_names.add(entity.ObjectName)

                    
                    
            # 关闭文档（不保存）
            doc.Close(False)
            print(f"已关闭: {dwg_file}")
            
        except Exception as e:
            print(f"处理失败: {dwg_file} | 错误: {str(e)}")
            
            
    print(f"模型空间_实体类型:\n {"\n".join(entity_type_names)}")
    print(f"图纸空间_实体类型:\n {"\n".join(layout_type_names)}")
    
 
    
    pythoncom.CoUninitialize()  # 释放COM资源

# 示例调用
folder_path = r"F:\hg\BJY\drawing_recogniton_dispatch\dwg_to_image\dwgs"  # 替换为实际文件夹路径
print_entities_in_folder(folder_path)