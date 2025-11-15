import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from base import logger_helper,exception_decorator,read_from_json_utf8_sig,write_to_json_utf8_sig,UpdateTimeType
#文件夹差异
class DirectoryTree:
    """功能1：递归遍历目录，生成树形结构并输出JSON"""
    
    def __init__(self):
        self.tree = {}
        self._logger=logger_helper("目录树")
    @property
    def logger(self):
        return self._logger
    def scan_directory(self, root_path):
        logger=self._logger
        logger.update_target(target=f"处理目录树{root_path}")
        logger.update_time(UpdateTimeType.ALL)
        """
        扫描指定目录，生成树形结构
        root_path: 要扫描的根目录路径
        """
        root_path = Path(root_path).resolve()
        self.tree = {
            "root": str(root_path),
            "type": "directory",
            "children": self._scan_recursive(root_path, root_path)
        }
        logger.info("成功",update_time_type=UpdateTimeType.ALL)
        return self.tree
    
    def _scan_recursive(self, current_path, root_path):
        """递归扫描目录"""
        result = {}
        with self._logger.raii_target(detail=f"当前目录: {current_path}") as logger:
            try:
                for item in current_path.iterdir():
                    relative_path = item.relative_to(root_path)
                    if item.is_file():
                        # 文件节点
                        result[str(relative_path)] = {
                            "type": "file",
                            "mtime": item.stat().st_mtime,
                            "mtime_str": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        }
                    elif item.is_dir():
                        # 目录节点，递归扫描
                        result[str(relative_path)] = {
                            "type": "directory",
                            "children": self._scan_recursive(item, root_path)
                        }
            except PermissionError:
                logger.error("失败",f"权限不足，无法访问")
            except Exception as e:
                logger.error("失败",f"扫描错误: \n{e}")
            
        return result
    
    def to_dict(self):
        """返回字典形式的树结构"""
        return self.tree
    
    def save_to_json_file(self, output_path):
        """将树结构保存为JSON文件"""
        with self._logger.raii_target(detail=f"保存到{output_path}") as logger:
            write_to_json_utf8_sig(output_path,self.tree)
            logger.info("成功")
    
    def load_from_json_file(self, json_path):
        with self._logger.raii_target(detail=f"从目录加载：{json_path}") as logger:
            """从JSON文件加载树结构"""
            if result := read_from_json_utf8_sig(json_path):
                self.tree = result
                logger.info("成功",update_time_type=UpdateTimeType.ALL)
            else:
                logger.error("失败",update_time_type=UpdateTimeType.ALL)
        return self.tree

    def to_flat_lst(self)->list[dict]:
        """将树结构转换为flat json"""

        def _to_flat_children(children:dict):
            results=[]
            if not children:
                return
            for name ,child in children.items:
                if child.get("type") == "file":
                    results.append({
                        "path": name,
                        "mtime": child.get("mtime", 0),
                        "mtime_str": child.get("mtime_str", "")
                    })
                elif child.get("type") == "directory":
                    if result:=self.to_flat_lst(child.get("children")):
                        results.extend(result)
                    
            return results

        return _to_flat_children(self.tree.get("children"))
    
    
    def from_flat_lst(self, flat_lst):
        """从flat json加载树结构"""
        self.tree = flat_lst
        return self.tree
    
    

class TreeComparator:
    """功能2：比较两个目录树，生成差异树"""
    
    def __init__(self):
        self.differences = {}
    
    def compare(self, tree_d, tree_f):
        """
        比较两个目录树D和F
        返回: {
            "added": E,  # F中有而D中没有的文件
            "updated": F  # F和D共有但F更新的文件
        }
        """
        if not tree_d or not tree_f:
            raise ValueError("输入树不能为空")
        
        # 确保我们在正确的根节点开始比较
        d_children = tree_d.get("children", {}) if "children" in tree_d else tree_d
        f_children = tree_f.get("children", {}) if "children" in tree_f else tree_f
        
        added = self._find_added_files(d_children, f_children, "")
        updated = self._find_updated_files(d_children, f_children, "")
        
        self.differences = {
            "added": added,
            "updated": updated
        }
        
        return self.differences
    
    def _find_added_files(self, d_node, f_node, current_path):
        """查找F中有但D中没有的文件/目录"""
        added = {}
        
        for name, f_item in f_node.items():
            full_path = os.path.join(current_path, name) if current_path else name
            
            if name not in d_node:
                # 完全新增的项目
                added[name] = f_item
            elif f_item.get("type") == "directory" and d_node[name].get("type") == "directory":
                # 如果是目录，递归比较
                sub_added = self._find_added_files(
                    d_node[name].get("children", {}),
                    f_item.get("children", {}),
                    full_path
                )
                if sub_added:
                    if "children" not in added:
                        added[name] = {"type": "directory", "children": {}}
                    added[name]["children"] = sub_added
        
        return added
    
    def _find_updated_files(self, d_node, f_node, current_path):
        """查找F中比D中更新的文件"""
        updated = {}
        
        for name, f_item in f_node.items():
            if name in d_node:
                d_item = d_node[name]
                full_path = os.path.join(current_path, name) if current_path else name
                
                if (f_item.get("type") == "file" and 
                    d_item.get("type") == "file" and
                    f_item.get("mtime", 0) > d_item.get("mtime", 0)):
                    # 文件且F的修改时间更晚
                    updated[name] = f_item
                elif (f_item.get("type") == "directory" and 
                      d_item.get("type") == "directory"):
                    # 目录，递归比较
                    sub_updated = self._find_updated_files(
                        d_item.get("children", {}),
                        f_item.get("children", {}),
                        full_path
                    )
                    if sub_updated:
                        if "children" not in updated:
                            updated[name] = {"type": "directory", "children": {}}
                        updated[name]["children"] = sub_updated
        
        return updated
    
    def generate_new_tree_g(self, tree_d, tree_f):
        """根据差异生成新的树G"""
        differences = self.compare(tree_d, tree_f)
        
        # G树包含所有需要更新的内容
        tree_g = {
            "root": f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "directory",
            "children": self._merge_trees(differences["added"], differences["updated"])
        }
        
        return tree_g
    
    def _merge_trees(self, added, updated):
        """合并新增和更新的文件"""
        merged = added.copy()
        
        for name, item in updated.items():
            if name in merged and item.get("type") == "directory":
                # 合并子目录
                merged_children = self._merge_trees(
                    merged[name].get("children", {}),
                    item.get("children", {})
                )
                merged[name]["children"] = merged_children
            else:
                merged[name] = item
        
        return merged


class FileCopier:
    """功能3：根据树G复制文件到目标目录，保留目录结构"""
    
    def __init__(self):
        self.copied_files = []
    
    def copy_files_from_tree(self, tree_g, base_folder_h, target_folder):
        """
        根据树G复制文件
        tree_g: 差异树
        base_folder_h: 基准文件夹H
        target_folder: 目标目录
        """
        base_folder_h = Path(base_folder_h)
        target_folder = Path(target_folder)
        
        # 创建目标目录
        target_folder.mkdir(parents=True, exist_ok=True)
        
        children = tree_g.get("children", tree_g)
        self._copy_recursive(children, base_folder_h, target_folder, "")
        
        return self.copied_files
    
    def _copy_recursive(self, node, base_folder, target_folder, relative_path):
        """递归复制文件和目录"""
        for name, item in node.items():
            current_relative_path = os.path.join(relative_path, name) if relative_path else name
            source_path = base_folder / current_relative_path
            
            if item.get("type") == "file":
                # 复制文件
                target_path = target_folder / current_relative_path
                self._copy_file(source_path, target_path, current_relative_path)
            elif item.get("type") == "directory":
                # 创建目录并递归复制
                target_dir = target_folder / current_relative_path
                target_dir.mkdir(parents=True, exist_ok=True)
                
                if "children" in item:
                    self._copy_recursive(
                        item["children"], 
                        base_folder, 
                        target_folder, 
                        current_relative_path
                    )
    
    def _copy_file(self, source_path, target_path, relative_path):
        """复制单个文件"""
        try:
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            self.copied_files.append(str(relative_path))
            print(f"已复制: {relative_path}")
            
        except FileNotFoundError:
            print(f"文件不存在: {source_path}")
        except PermissionError:
            print(f"权限不足: {source_path}")
        except Exception as e:
            print(f"复制错误 {source_path}: {e}")


# 使用示例
if __name__ == "__main__":
    from base import audio_root
    # 示例用法
    try:
        # 功能1示例：扫描目录并生成JSON
        print("=== 功能1: 扫描目录 ===")
        scanner = DirectoryTree()
        root_dir=audio_root
        json_path=os.path.join(root_dir, "directory_tree.json")
        scanner.load_from_json_file(json_path)
        result=scanner.to_flat_lst()
        
        exit()
        
        
        
        
        tree_c = scanner.scan_directory(root_dir)  # 替换为你的目录
        scanner.save_to_json_file(json_path)
        
        # 功能2示例：比较两个目录树
        print("\n=== 功能2: 比较目录树 ===")
        comparator = TreeComparator()
        
        # 加载两个树进行比较（这里用同一个树示例，实际应该用不同的）
        tree_d = scanner.to_dict()
        tree_f = scanner.to_dict()  # 实际应用中应该是不同的树
        
        tree_g = comparator.generate_new_tree_g(tree_d, tree_f)
        print("差异分析完成")
        
        # 功能3示例：复制文件
        print("\n=== 功能3: 复制文件 ===")
        copier = FileCopier()
        copied_files = copier.copy_files_from_tree(
            tree_g, 
            "./source_folder",  # 基准文件夹H
            "./target_folder"   # 目标目录
        )
        print(f"已复制 {len(copied_files)} 个文件")
        
    except Exception as e:
        print(f"执行错误: {e}")