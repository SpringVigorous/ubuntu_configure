import subprocess
import os
from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )
from base import path_equal,guid
from base import logger_helper,UpdateTimeType,copy_file,recycle_bin,normal_path,path_equal
from dy_unity import dy_root,OrgInfo,DestInfo
import json

class VideoMetadata:
    def __init__(self,code:int,infos:str) -> None:
        self.success=code
        self.infos=infos
        
    def has_check_flag(self,flags):
        for flag in flags:
            if flag in self.infos:
                return True
        return False
    
    

class VideoCleaner:
    def __init__(self) -> None:
        self.metadata_infos=[]
        self.load_cleaner()
        
   
    def meta_item(self,file_path):
        file_path=normal_path(file_path)
        for item in self.metadata_infos:
            if path_equal(item["file"],file_path):
                return item
            
        flag,info=VideoCleaner.has_metadata_flag(file_path)
        
        self.metadata_infos.append({"file":file_path,"meta":info.infos,"has_flag":flag, "handled":False})
        return self.metadata_infos[-1]

    @staticmethod
    def clean_json_path():
        return os.path.join(dy_root.video_create_root,"cleaned_videos.json")
    
    def load_cleaner(self):
        json_path=VideoCleaner.clean_json_path()
        if os.path.exists(json_path):
            with open(json_path,"r",encoding="utf-8") as f:
                self.metadata_infos=json.load(f)

    
    def save_cleaner(self):
        with open(VideoCleaner.clean_json_path(),"w",encoding="utf-8") as f:
            json.dump(self.metadata_infos,f,ensure_ascii=False)
            
    @staticmethod
    def metadata_info(file_path)->VideoMetadata:
        """ 使用 FFprobe 验证元数据清除情况 """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format_tags',
            '-of', 'default=noprint_wrappers=1',
            file_path
        ]
        result=subprocess.run(cmd, capture_output=True, text=True) 

        seccess=result.returncode==0
        infos=list( filter(lambda x:bool(x), [result.stdout,result.stderr]))
        return VideoMetadata(seccess,infos)

        
    @staticmethod
    def clean_metadata(input_path, output_path:str=None):
        
        if not output_path:
            output_path=input_path
        
        temp_path=output_path
        is_dest_same=path_equal(input_path,output_path) 
        if is_dest_same:
            cur_path=Path(input_path)
            temp_path=str(cur_path.with_stem(f"clean_{guid(6)}_{cur_path.stem}"))

                # FFmpeg 命令（保留原始编码参数）
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-map_metadata', '-1',  # 清除所有元数据
            '-c:v', 'copy',         # 复制视频流
            '-c:a', 'copy',         # 复制音频流
            '-movflags', 'use_metadata_tags',  # 处理 MP4 格式
            '-y',                   # 覆盖输出文件
            temp_path
        ]
        result =None
        try:
            result =subprocess.run(cmd, check=True, capture_output=True)
            success=result.returncode==0
            if success and is_dest_same:
                recycle_bin(input_path)
                os.rename(temp_path,output_path)
            return success
        except:
            return False

    @staticmethod
    def write_video_metadata(input_path, output_path, metadata_dict):
        
        if not output_path:
            output_path=input_path
        is_dest_same=path_equal(input_path,output_path) 
        temp_path=output_path
        if is_dest_same:
            cur_path=Path(input_path)
            temp_path=str(cur_path.with_stem(f"clean_{guid(6)}_{cur_path.stem}"))
        elif os.path.exists(output_path):
            recycle_bin(output_path)
            
        """
        通过 FFmpeg 将自定义元数据写入视频文件
        :param input_path: 输入视频路径
        :param output_path: 输出视频路径
        :param metadata_dict: 元数据字典（键值对）
        """
        # 构建 FFmpeg 命令基础部分
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-movflags', 'use_metadata_tags',  # 允许写入自定义元数据
            '-c:v', 'copy',                     # 复制视频流
            '-c:a', 'copy'                      # 复制音频流
        ]
        
        # 添加元数据参数
        for key, value in metadata_dict.items():
            cmd.extend(['-metadata', f'{key}={value}'])
        
        # 添加输出文件路径
        cmd.append(temp_path)
        
        # 执行命令并捕获输出（静默模式）
        try:
            result =subprocess.run(
                cmd,
                check=True,
                capture_output=True
            )
            success=result.returncode==0
            if success and is_dest_same:
                recycle_bin(input_path)
                os.rename(temp_path,output_path)
            
            
            print(f"元数据写入成功：{output_path}")
        except subprocess.CalledProcessError as e:
            print(f"错误：{e.stderr}")

    

    @staticmethod
    def has_metadata_flag(file_path):
        logger=logger_helper("检查视频元数据",file_path)
        output = VideoCleaner.metadata_info(file_path)
        try:
            if output.success :
                result=output.has_check_flag(flags=["com.apple.quicktime.make","MetaInfo"])
                logger.info("含有" if result else "不含有",f'\n{"\n".join(output.infos)}',update_time_type=UpdateTimeType.STAGE)
                return result,output
        except:
            pass
        return True,output
            
            

    def exist_unhandled_metadata(self,file_path):
        meta_info=self.meta_item(file_path)
        return meta_info["has_flag"] and not meta_info["handled"]
        




    def batch_clean_metadata(self,input_dir, output_dir=None):
        """
        批量处理目录中的所有视频文件
        支持格式: .mp4, .mov, .mkv
        """
        video_exts = ('.mp4', '.mov', '.mkv')
        if not output_dir:
            output_dir = input_dir
        
        for root, _, files in os.walk(input_dir):
            for file in files:
                if not file.lower().endswith(video_exts):
                    continue
                input_path = os.path.join(root, file)
                if not self.exist_unhandled_metadata(input_path):
                    continue
                
                if self.clean_metadata(input_path, os.path.join(output_dir, file)):
                    self.meta_item(input_path)["handled"]=True




if __name__ == "__main__":
    input_dir = dy_root.video_create_root
    output_dir = dy_root.video_cleaned_root
    os.makedirs(output_dir, exist_ok=True)
    
    
    # 示例：写入指定元数据
    metadata = {
        "compatible_brands": "isommp42",
        "creation_time": "2025-03-28T10:05:37.000000Z",
        "location": "+31.525+120.2144/",
        "location-eng": "+31.525+120.2144/",
        "com.android.version": "15",
        "com.video.file.type": "",
        "com.xiaomi.normal_video": "30"
    }
    
    # 输入输出路径（可修改为批量处理）
    input_file = "input.mp4"
    output_file = "output.mp4"
    
    # 执行写入操作

    VideoCleaner.write_video_metadata(r"F:\worm_practice\douyin\素材\create\鼋头渚晚樱.mp4",r"F:\worm_practice\douyin\素材\create\鼋头渚晚樱_4.mp4", metadata)
    
    # VideoCleaner.has_metadata_flag(r"F:\worm_practice\douyin\素材\create\鼋头渚晚樱.mp4")
    
    # exit()
    
    # # 处理单个文件
    # file_path=os.path.join(input_dir,"鼋头渚晚樱.mp4")
    # #先检查

    # cleaned_file = remove_metadata(file_path, input_dir)
    # if not cleaned_file:
    #     exit()
    # has_metadata(cleaned_file)

    # 批量处理目录
    manager=VideoCleaner() 
    
    # manager.clean_metadata(r"F:\worm_practice\douyin\素材\create\鼋头渚晚樱.mp4")
    # exit()
    # manager.batch_clean_metadata(input_dir,output_dir)
    manager.batch_clean_metadata(input_dir)
    manager.save_cleaner()
    
    
    
    