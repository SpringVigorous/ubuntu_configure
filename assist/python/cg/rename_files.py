import sys
import os
from pathlib import Path
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import rename_files_with_pattern
   
   
   
# 示例用法
directory_path = r'F:\教程\短视频教程\抖音\轻松学堂\21天课\钉钉消息\实战'
rename_files_with_pattern(directory_path)