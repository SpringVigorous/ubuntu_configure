import os
import zipfile
import shutil
from pathlib import Path
from string_tools import cur_datetime_str

class ZipUtility:
    def __init__(self):
        self.default_chunk_size = 1024 * 1024 * 100  # 默认分卷大小100MB

    def compress(self, source_path, output_dir=None, volume_size=None):
        """
        压缩文件/文件夹，支持分卷压缩
        :param source_path: 源文件/文件夹路径
        :param output_dir: 输出目录（默认源路径父目录）
        :param volume_size: 分卷大小（字节），None表示不分卷
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"源路径不存在: {source_path}")

        # 1. 处理输出目录和文件名
        timestamp = cur_datetime_str()
        if output_dir is None:
            output_dir = os.path.join(source.parent,"zip")
            zip_name = f"{source.name}_{timestamp}"
        else:
            zip_name = f"{source.stem}_{timestamp}" if source.is_file() else f"{source.name}_{timestamp}"

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 2. 选择压缩模式
        if volume_size is None:
            self._single_compress(source, output_dir / f"{zip_name}.zip")
        else:
            self._volume_compress(source, output_dir, zip_name, volume_size)

    def _single_compress(self, source, zip_path):
        """普通压缩"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if source.is_file():
                zipf.write(source, source.name)
            else:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source)  # 保持目录结构
                        zipf.write(file_path, arcname)
                    if not dirs and not files:  # 空目录
                        rel_dir = Path(root).relative_to(source)
                        zipf.mkdir(str(rel_dir))  # 显式创建空目录
                    
        print(f"压缩完成: {zip_path}")

    def _volume_compress(self, source, output_dir, base_name, volume_size):
        """分卷压缩核心逻辑 [7,9](@ref)"""
        temp_dir = output_dir / "temp_zip"
        temp_dir.mkdir(exist_ok=True)
        
        # 先创建临时完整压缩包
        temp_zip = temp_dir / f"{base_name}.zip"
        self._single_compress(source, temp_zip)
        
        # 分卷切割
        part_num = 1
        with open(temp_zip, 'rb') as f:
            while chunk := f.read(volume_size):
                part_name = output_dir / f"{base_name}.z{part_num:02d}.zip"
                with open(part_name, 'wb') as part_file:
                    part_file.write(chunk)
                part_num += 1
        
        shutil.rmtree(temp_dir)  # 清理临时文件
        print(f"分卷压缩完成: 共{part_num-1}个分卷, 前缀 {base_name}")

    @staticmethod
    def extract(zip_path, output_dir=None, password=None):
        """
        解压文件（支持分卷自动合并）
        :param zip_path: 压缩包路径（或分卷首文件）
        :param output_dir: 输出目录（默认压缩包所在目录）
        """
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"压缩文件不存在: {zip_path}")

        # 处理分卷合并 [11](@ref)
        if zip_path.suffix.startswith('.z'):
            base_name = zip_path.stem.rsplit('.', 1)[0]
            parent_dir = zip_path.parent
            combined_zip = parent_dir / f"{base_name}_combined.zip"
            with open(combined_zip, 'wb') as out_file:
                part_num = 1
                while part_file := parent_dir / f"{base_name}.z{part_num:02d}":
                    if not part_file.exists(): break
                    with open(part_file, 'rb') as pf:
                        out_file.write(pf.read())
                    part_num += 1
            zip_path = combined_zip

        # 执行解压
        output_dir = output_dir or zip_path.parent
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if password:
                zip_ref.setpassword(password.encode('utf-8'))
            zip_ref.extractall(output_dir)
        print(f"解压完成至: {output_dir}")

# 使用示例
if __name__ == "__main__":
    

    
    
    zipper = ZipUtility()
    
    # 单文件压缩（默认输出路径）
    # zipper.compress(r"F:\worm_practice\taobao\五味食养\images_prohibite")
    
    # # 文件夹分卷压缩（200MB分卷）
    zipper.compress(r"F:\数据库\数据库-002.db", volume_size=200 * 1024 * 1024)
    
    # # 解压分卷（自动合并）
    # zipper.extract("project_files_20250727_110405.z01")