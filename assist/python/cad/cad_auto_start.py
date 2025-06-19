import os
import threading
import multiprocessing
from multiprocessing import Pool
import win32com.client
import pythoncom
import time
from queue import Queue, Empty
from typing import List, Dict, Optional
from cad_tools import  find_cad_dirs_by_reg

import dill

class CADProcessor:
    """AutoCAD 多进程处理器"""
    
    def __init__(self, 
                 max_instances: int = 4,
                 threads_per_instance: int = 3,
                 autocad_visible: bool = False):
        """
        初始化 CAD 处理器
        :param max_instances: 最大 AutoCAD 进程数
        :param threads_per_instance: 每个进程的最大线程数
        :param autocad_visible: 是否显示 AutoCAD 界面
        """
        self.max_instances = min(max_instances, multiprocessing.cpu_count())
        self.threads_per_instance = threads_per_instance
        self.autocad_visible = autocad_visible
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.processes = []
        self.running = False
        
        # 查找 AutoCAD 安装路径
        self.autocad_path = self.find_autocad_installation()
    
    def find_autocad_installation(self) -> str:
        """自动查找 AutoCAD 安装路径"""
        # 常见安装路径
        dirs=find_cad_dirs_by_reg()
        for cur_dir in dirs:
            path=os.path.join(cur_dir, "acad.exe")
            if os.path.exists(path):
                return path
        return None
    def start(self):
        """启动 CAD 处理进程池"""
        if not self.autocad_path:
            raise FileNotFoundError("无法找到 AutoCAD 安装路径")
            
        self.running = True
        # 将工作函数打包
        worker_function = dill.dumps(self.autocad_worker)
        
        # 使用自定义进程池
        self.pool = Pool(processes=self.max_instances)
        for i in range(self.max_instances):
            self.pool.apply_async(self._run_in_subprocess, (worker_function, i))
        print(f"已启动 {self.max_instances} 个 AutoCAD 处理进程")
    
    def _run_in_subprocess(self, worker_func_dump, worker_id):
        """在子进程中运行打包的函数"""
        worker_func = dill.loads(worker_func_dump)
        worker_func(worker_id)
        

        
        
    def start_old(self):
        """启动 CAD 处理进程池"""
        if not self.autocad_path:
            raise FileNotFoundError("无法找到 AutoCAD 安装路径")
            
        self.running = True
        for i in range(self.max_instances):
            p = multiprocessing.Process(
                target=self.autocad_worker,
                args=(i,)
            )
            p.daemon = True
            p.start()
            self.processes.append(p)
        print(f"已启动 {self.max_instances} 个 AutoCAD 处理进程")
    
    def add_directory(self, directory_path: str, 
                      file_types: List[str] = [".dwg"]):
        """
        添加待处理的 CAD 目录
        :param directory_path: CAD 文件夹路径
        :param file_types: 文件类型列表，默认为 [".dwg"]
        """
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"路径 '{directory_path}' 不是一个有效目录")
        
        # 扫描目录中的 CAD 文件
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_lower = file.lower()
                if any(file_lower.endswith(ext) for ext in file_types):
                    full_path = os.path.join(root, file)
                    self.task_queue.put(full_path)
        print(f"已添加 {self.task_queue.qsize()} 个 CAD 文件到处理队列")
    
    def get_results(self, timeout: float = 0.1) -> List[Dict]:
        """
        获取处理结果
        :param timeout: 超时时间(秒)
        :return: 结果字典列表
        """
        results = []
        while True:
            try:
                result = self.result_queue.get(timeout=timeout)
                results.append(result)
            except Empty:
                break
        return results
    
    def wait_completion(self):
        """等待所有任务完成"""
        print("等待任务完成...")
        while not self.task_queue.empty():
            time.sleep(2)
            
        # 发送终止信号
        for _ in range(self.max_instances * self.threads_per_instance):
            self.task_queue.put(None)
            
        # 等待进程结束
        for p in self.processes:
            p.join(timeout=15)
        self.running = False
    
    def stop(self):
        """停止所有处理进程"""
        if self.running:
            # 清空任务队列
            while not self.task_queue.empty():
                try:
                    self.task_queue.get_nowait()
                except Empty:
                    break
                    
            # 发送终止信号
            self.wait_completion()
            print("所有处理进程已停止")
    
    def autocad_worker(self, instance_id: int):
        """AutoCAD 工作进程主函数"""
        # 初始化 COM 环境
        pythoncom.CoInitialize()
        
        try:
            # 创建 AutoCAD 实例
            acad_app = win32com.client.Dispatch("AutoCAD.Application")
            acad_app.Visible = self.autocad_visible
            
            # 配置静默模式
            if not self.autocad_visible:
                acad_app.SetSystemVariable("FILEDIA", 0)
                acad_app.SetSystemVariable("CMDDIA", 0)
                acad_app.SetSystemVariable("PRODUCT", "AutoCAD")  # 减少启动日志
            
            # 创建工作线程
            threads = []
            for i in range(self.threads_per_instance):
                t = threading.Thread(
                    target=self.document_worker,
                    args=(acad_app, instance_id, i)
                )
                t.daemon = True
                t.start()
                threads.append(t)
            
            # 监控线程状态
            while any(t.is_alive() for t in threads):
                time.sleep(1)
        
        except Exception as e:
            print(f"进程 {instance_id} 错误: {str(e)}")
        finally:
            # 清理 AutoCAD 实例
            try:
                if acad_app and hasattr(acad_app, "Quit"):
                    acad_app.Quit()
            except:
                pass
            
            # 释放 COM 资源
            pythoncom.CoUninitialize()


    
    
    def document_worker(self, acad_app, instance_id: int, thread_id: int):
        """文档处理工作线程"""
        print(f"实例 {instance_id} 线程 {thread_id}: 就绪")
        
        while True:
            try:
                # 获取任务 (超时5秒)
                file_path = self.task_queue.get(timeout=5)
                
                # 终止信号
                if file_path is None:
                    print(f"实例 {instance_id} 线程 {thread_id}: 收到终止信号")
                    self.task_queue.task_done()
                    break
                
                # 处理 CAD 文档
                result = self.process_cad_document(acad_app, file_path)
                result["instance_id"] = instance_id
                result["thread_id"] = thread_id
                self.result_queue.put(result)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                print(f"实例 {instance_id} 线程 {thread_id}: 处理错误 - {str(e)}")
                self.result_queue.put({
                    "error": str(e),
                    "file_path": file_path,
                    "status": "failed",
                    "instance_id": instance_id,
                    "thread_id": thread_id
                })
    
    @staticmethod
    def process_cad_document(acad_app, file_path: str) -> Dict:
        """
        处理单个 CAD 文档
        :return: 包含处理结果的字典
        """
        start_time = time.time()
        filename = os.path.basename(file_path)
        
        # 打开文档
        doc = acad_app.Documents.Open(file_path, not acad_app.Visible)
        time.sleep(0.5)  # 等待文档加载
        
        # 获取文档基本信息
        doc_info = {
            "file_name": filename,
            "file_path": file_path,
            "file_size": f"{os.path.getsize(file_path)/1024:.1f} KB",
            "creation_date": time.ctime(os.path.getctime(file_path))
        }
        
        # 获取实体统计信息
        entity_stats = {}
        try:
            # 示例：统计不同类型实体的数量
            entity_counts = {}
            for entity in doc.ModelSpace:
                entity_type = entity.ObjectName
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            doc_info["entity_counts"] = entity_counts
            
            # 示例：提取所有文本内容
            texts = []
            for entity in doc.ModelSpace:
                if entity.ObjectName in ["AcDbText", "AcDbMText"]:
                    try:
                        texts.append(entity.TextString)
                    except:
                        pass
            doc_info["text_samples"] = texts[:5]  # 只保存前5个文本
            
            # 示例：处理块参照中的圆（计算直径）
            circles_info = []
            for entity in doc.ModelSpace:
                if entity.ObjectName == "AcDbBlockReference":
                    try:
                        circles_info.extend(
                            CADProcessor.process_block_circles(entity)
                        )
                    except:
                        pass
            doc_info["block_circles"] = circles_info
            
        finally:
            # 确保关闭文档
            try:
                doc.Close(False)
            except:
                pass
        
        # 添加处理状态和时间
        doc_info["status"] = "success"
        doc_info["processing_time"] = f"{time.time() - start_time:.2f} 秒"
        return doc_info
    
    @staticmethod
    def process_block_circles(block_ref) -> List[Dict]:
        """处理块参照中的圆，获取真实直径"""
        circles_info = []
        try:
            block_name = block_ref.Name
            scale_factors = [
                block_ref.XScaleFactor, 
                block_ref.YScaleFactor, 
                block_ref.ZScaleFactor
            ]
            
            # 获取块定义
            block_def = block_ref.Block
            for sub_entity in block_def:
                if sub_entity.ObjectName == "AcDbCircle":
                    original_radius = sub_entity.Radius
                    effective_scale = max(scale_factors[0], scale_factors[1])
                    
                    # 处理非均匀缩放
                    if abs(scale_factors[0] - scale_factors[1]) > 1e-5:
                        effective_scale = (
                            (original_radius * scale_factors[0])**2 + 
                            (original_radius * scale_factors[1])**2
                        )**0.5 / original_radius
                    
                    true_diameter = 2 * original_radius * effective_scale
                    
                    circles_info.append({
                        "block_name": block_name,
                        "original_diameter": 2 * original_radius,
                        "true_diameter": true_diameter,
                        "scale_factors": scale_factors
                    })
        except:
            pass
        return circles_info
# 示例1：简单使用（单目录处理）
def process_single_folder(folder_path: str):
    # 创建处理器（4进程，每个进程3线程）
    processor = CADProcessor(max_instances=4, autocad_visible=False)
    
    # 添加要处理的目录
    processor.add_directory(folder_path)
    
    # 启动处理
    processor.start()
    
    # 定时获取处理结果
    while True:
        results = processor.get_results()
        for result in results:
            print(f"处理完成: {result['file_name']} ({result['status']})")
            print(f"  实体统计: {result['entity_counts']}")
            print(f"  处理时间: {result['processing_time']}")
        
        if not processor.task_queue.qsize() and len(results) == 0:
            break
        
        time.sleep(5)
    
    # 等待所有任务完成
    processor.wait_completion()
    print("所有 CAD 文件处理完成")

# 示例2：多目录并行处理
def process_multiple_folders(folder_paths: list):
    # 创建处理器（每个CPU核心1个进程）
    processor = CADProcessor(
        max_instances=multiprocessing.cpu_count(),
        autocad_visible=False
    )
    
    # 添加多个目录
    for path in folder_paths:
        processor.add_directory(path)
    
    # 启动处理
    processor.start()
    
    # 定时打印进度
    total_files = processor.task_queue.qsize()
    processed_files = 0
    
    while True:
        # 获取已完成的处理结果
        results = processor.get_results()
        processed_files += len(results)
        
        # 打印进度
        print(f"\r处理进度: {processed_files}/{total_files} ({processed_files/total_files*100:.1f}%)", end="")
        
        # 检查是否完成
        if not processor.task_queue.qsize() and processed_files >= total_files:
            break
        
        time.sleep(2)
    
    # 保存所有结果
    final_results = processor.get_results(timeout=1)
    
    # 分析结果
    success = sum(1 for r in final_results if r.get("status") == "success")
    print(f"\n处理完成: {success}/{total_files} 个文件成功")
    
    # 生成报告
    with open("cad_processing_report.csv", "w") as f:
        f.write("文件名,状态,处理时间,实体数量\n")
        for r in final_results:
            entity_count = sum(r.get("entity_counts", {}).values())
            f.write(f"{r['file_name']},{r['status']},{r['processing_time']},{entity_count}\n")
    
    processor.stop()





class CADProcessingAPI:
    """高级 CAD 处理 API（单例模式）"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.processor = CADProcessor()
            cls._instance.status = "idle"
            cls._instance.current_job_id = None
            cls._instance.results_store = {}
        return cls._instance
    
    def start_processing(self, folders: list, job_id: str = None):
        """启动新的处理任务"""
        if self.status != "idle":
            return {"status": "error", "message": "处理器忙碌中"}
        
        if not job_id:
            job_id = f"job_{int(time.time())}"
        
        # 重置存储
        self.results_store[job_id] = {
            "start_time": time.time(),
            "folders": folders,
            "results": [],
            "file_count": 0
        }
        
        # 添加文件夹
        for folder in folders:
            self.processor.add_directory(folder)
        
        # 保存文件总数
        file_count = self.processor.task_queue.qsize()
        self.results_store[job_id]["file_count"] = file_count
        
        # 启动处理
        self.processor.start()
        self.status = "processing"
        self.current_job_id = job_id
        
        return {"status": "started", "job_id": job_id, "file_count": file_count}
    
    def get_progress(self, job_id: str = None):
        """获取处理进度"""
        if not job_id:
            job_id = self.current_job_id
        
        if job_id not in self.results_store:
            return {"status": "error", "message": "无效的 job_id"}
        
        # 获取新结果
        new_results = self.processor.get_results()
        if new_results:
            self.results_store[job_id]["results"].extend(new_results)
        
        job_data = self.results_store[job_id]
        processed = len(job_data["results"])
        total = job_data["file_count"]
        
        return {
            "status": self.status,
            "job_id": job_id,
            "processed_files": processed,
            "total_files": total,
            "progress": f"{processed}/{total}",
            "percentage": processed / total * 100 if total > 0 else 0,
            "duration": f"{time.time() - job_data['start_time']:.1f} 秒"
        }
    
    def get_results(self, job_id: str = None):
        """获取处理结果（完成后使用）"""
        if not job_id:
            job_id = self.current_job_id
        
        if job_id not in self.results_store:
            return {"status": "error", "message": "无效的 job_id"}
        
        return {
            "status": "completed" if self.status == "idle" else "partial",
            "job_id": job_id,
            "results": self.results_store[job_id]["results"]
        }
    
    def stop_processing(self, job_id: str = None):
        """停止当前处理任务"""
        if not job_id or job_id == self.current_job_id:
            self.processor.stop()
            self.status = "idle"
            return {"status": "stopped", "job_id": self.current_job_id}
        
        return {"status": "error", "message": "指定的 job_id 不是当前任务"}

# # 实际使用
# if __name__ == "__main__":
#     # 处理单个目录
#     # process_single_folder(r"E:\工程图纸\项目A")
    
#     # 处理多个目录
#     folders = [
#         r"E:\工程图纸\项目A",
#         r"E:\工程图纸\项目B",
#         r"F:\archive\2023年设计图纸"
#     ]
#     process_multiple_folders(folders)


# 使用高级API
if __name__ == "__main__":
    # 创建API实例
    api = CADProcessingAPI()
    
    # 启动处理任务
    response = api.start_processing(
        folders=[
            r"F:\TH\bridge_desinger\bridge_desinger\main\th_subsystem\gw_x64_release_bin\template\drawpaper\附属结构\后张空心板（部颁简变连）",
            r"F:\TH\bridge_desinger\bridge_desinger\main\th_subsystem\gw_x64_release_bin\template\drawpaper\附属结构\T梁"
        ],
        job_id="building_project_2023"
    )
    
    if response["status"] == "started":
        print(f"启动任务: {response['job_id']}，文件数: {response['file_count']}")
        
        # 监控进度
        while True:
            progress = api.get_progress()
            print(f"\r进度: {progress['progress']} ({progress['percentage']:.1f}%)", end="")
            
            if progress["processed_files"] >= progress["total_files"]:
                break
                
            time.sleep(5)
        
        # 获取最终结果
        results = api.get_results()
        print(f"\n处理完成，共处理 {len(results['results'])} 个文件")
        
        # 分析结果
        success_count = sum(1 for r in results["results"] if r.get("status") == "success")
        print(f"成功文件数: {success_count}")