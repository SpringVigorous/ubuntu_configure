import os
from pyautocad import Autocad
import pythoncom
import win32com.client
from cad_tools import  find_cad_dirs_by_reg


def quit_app(acad_app):
    # 清理 AutoCAD 实例
    try:
        if acad_app and hasattr(acad_app, "Quit"):
            acad_app.Quit()
    except:
        pass
    
def find_autocad_installation() -> str:
    """自动查找 AutoCAD 安装路径"""
    # 常见安装路径
    dirs=find_cad_dirs_by_reg()
    for cur_dir in dirs:
        path=os.path.join(cur_dir, "acad.exe")
        if os.path.exists(path):
            return path
    return None
def get_app(autocad_visible:bool=False):
    
    acad_path =find_autocad_installation()
    print(acad_path)
    
    """AutoCAD 工作进程主函数"""
    # 初始化 COM 环境
    # pythoncom.CoInitialize()
    try:
        # 创建 AutoCAD 实例
        acad_app = win32com.client.Dispatch("AutoCAD.Application")
        # acad_app.Visible = autocad_visible
        # 配置静默模式
        # if not autocad_visible:
        #     acad_app.SetSystemVariable("FILEDIA", 0)
        #     acad_app.SetSystemVariable("CMDDIA", 0)
        #     acad_app.SetSystemVariable("PRODUCT", "AutoCAD")  # 减少启动日志
        
        return acad_app

    except Exception as e:
        print(f"错误: {str(e)}")


def print_entities_in_folder(folder_path):
    # 连接AutoCAD（需提前打开AutoCAD软件）
    pythoncom.CoInitialize()  # 初始化COM组件
    acad =get_app()
    if not acad:
        return
    app = acad
    
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
    
    
    quit_app(acad)
    pythoncom.CoUninitialize()  # 释放COM资源

# 示例调用
folder_path = r"F:\hg\BJY\drawing_recogniton_dispatch\dwg_to_image\dwgs"  # 替换为实际文件夹路径
print_entities_in_folder(folder_path)