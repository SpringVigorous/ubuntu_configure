import win32com.client
from pyautocad import Autocad
import os
from math import pi
import numpy as np
import threading

# 用于确保线程安全
_instance_lock = threading.Lock()

class DwgReader:
    _instance = None
    _acad = None
    _acad_app = None
    _current_doc = None
    _open_documents = {}  # 跟踪所有打开的文档 {doc_path: doc_object}
    
    def __new__(cls):
        with _instance_lock:
            if cls._instance is None:
                cls._instance = super(DwgReader, cls).__new__(cls)
                # 延迟初始化AutoCAD - 第一次打开文档时再创建
        return cls._instance
    
    @classmethod
    def initialize_acad(cls):
        """在第一次使用时初始化AutoCAD实例"""
        if cls._acad is None:
            try:
                cls._acad = Autocad(create_if_not_exists=True, visible=False)
                cls._acad_app = win32com.client.Dispatch("AutoCAD.Application")
                print("AutoCAD实例已创建")
                # 注册退出时的清理函数
                import atexit
                atexit.register(cls.shutdown)
            except Exception as e:
                raise RuntimeError(f"初始化AutoCAD失败: {e}")
    
    @classmethod
    def open_document(cls, dwg_path):
        """打开指定的DWG文档"""
        cls.initialize_acad()
        
        if not os.path.exists(dwg_path):
            raise FileNotFoundError(f"DWG文件不存在: {dwg_path}")
        
        # 如果文档已经打开，直接返回现有文档
        if dwg_path in cls._open_documents:
            
           
            cls._current_doc = cls._open_documents[dwg_path]
            
            return cls._current_doc
        
        try:
            # 规范化路径以处理大小写问题
            normalized_path = os.path.abspath(dwg_path)
            doc=None
            for _doc in cls._acad_app.Documents:
                if _doc.FullName == normalized_path:
                    doc=_doc
                    break
            
            # 打开文档
            if not doc:
                doc = cls._acad_app.Documents.Open(normalized_path,False,None)
            
            # 存储文档引用
            cls._open_documents[normalized_path] = doc
            cls._current_doc = doc
            
            # 强制刷新文档
            # doc.Regen(0)  # acActiveViewport
            
            print(f"成功打开文档: {normalized_path}")
            return doc
        except Exception as e:
            raise RuntimeError(f"打开DWG文件失败: {e}")
    
    @classmethod
    def get_current_document(cls):
        """获取当前活动的文档"""
        return cls._current_doc
    @classmethod
    def close_current_document(cls):
        """关闭当前活动文档"""
        if cls._current_doc:
            cls.close_document(cls._current_doc.FullName)
            cls._current_doc = None
    
    @classmethod
    def close_document(cls, dwg_path=None, save_changes=False):
        """关闭指定文档"""
        if not dwg_path and cls._current_doc:
            dwg_path = cls._current_doc.FullName
        
        if not dwg_path or dwg_path not in cls._open_documents:
            print(f"文档未打开或不存在: {dwg_path}")
            return
        
        try:
            doc = cls._open_documents[dwg_path]
            # 确保文档是激活状态
            cls._acad_app.ActiveDocument = doc
            doc.Close(save_changes)
            
            # 移除引用
            del cls._open_documents[dwg_path]
            
            # 更新当前文档
            if cls._current_doc == doc:
                cls._current_doc = None
                if cls._open_documents:
                    # 激活另一个打开文档
                    cls._current_doc = next(iter(cls._open_documents.values()))
            
            print(f"已关闭文档: {dwg_path}")
        except Exception as e:
            print(f"关闭文档时出错: {e}")
    
    @classmethod
    def close_all_documents(cls, save_changes=False):
        """关闭所有打开的文档"""
        for path in list(cls._open_documents.keys()):
            cls.close_document(path, save_changes)
    
    @classmethod
    def shutdown(cls):
        """安全关闭AutoCAD实例"""
        try:
            cls.close_all_documents()
            
            if cls._acad_app:
                cls._acad_app.Quit()
                cls._acad_app = None
                cls._acad = None
                print("AutoCAD实例已关闭")
        except Exception as e:
            print(f"关闭AutoCAD时出错: {e}")
    
    @classmethod
    def iterate_modelspace(cls, callback, doc_path=None, ids=None, matrix=None):
        """
        遍历文档模型空间中的实体
        :param callback: 处理每个实体的回调函数
        :param doc_path: 可选-指定文档路径（默认为当前文档）
        :param ids: 可选的ID列表
        :param matrix: 可选的变换矩阵
        """
        doc = cls._get_document(doc_path)
        
        # 设置默认参数
        if ids is None:
            ids = []
        if matrix is None:
            matrix = np.identity(4)
        
        # 获取模型空间
        msp = doc.ModelSpace
        
        # 遍历所有实体
        for entity in msp:
            callback(entity, ids, matrix)
    
    @classmethod
    def get_modelspace_entities(cls, doc_path=None):
        """获取文档模型空间中的所有实体"""
        doc = cls._get_document(doc_path)
        return list(doc.ModelSpace)
    
    @classmethod
    def switch_document(cls, dwg_path):
        """切换到指定文档"""
        return cls.open_document(dwg_path)
    
    @classmethod
    def _get_document(cls, doc_path=None):
        """获取指定文档或当前文档"""
        if doc_path:
            doc = cls.open_document(doc_path)
        elif cls._current_doc:
            doc = cls._current_doc
        else:
            raise RuntimeError("没有活动的文档，请先打开一个文档")
        return doc

# 辅助函数
def identity_matrix():
    return np.identity(4)

def print_entity(entity, ids, matrix):
    """示例实体处理函数"""
    print(f"实体类型: {entity.ObjectName}, 句柄: {entity.Handle}")

# 使用示例
if __name__ == "__main__":
    # 使用单例类 - 不需要实例化
    file1 = r"F:\path\to\file1.dwg"
    file2 = r"F:\path\to\file2.dwg"
    
    try:
        # 打开第一个文档
        doc1 = DwgReader.open_document(file1)
        
        # 处理第一个文档
        DwgReader.iterate_modelspace(print_entity, file1, [], identity_matrix())
        
        # 切换到第二个文档（保持第一个文档打开）
        doc2 = DwgReader.switch_document(file2)
        
        # 处理第二个文档
        DwgReader.iterate_modelspace(print_entity, file2, [], identity_matrix())
        
        # 关闭文档
        DwgReader.close_document(file1)
        DwgReader.close_document(file2)
        
        # 或者使用自动关闭（程序退出时会自动调用）
        # DwgReader.shutdown()
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        # 确保资源被清理
        DwgReader.shutdown()