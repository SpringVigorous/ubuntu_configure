
import sys
from pathlib import Path
import os

#废弃，统一用 replace_folders_files.py代替

# 将当前脚本所在项目的根路径添加到sys.path
# 将当前脚本所在项目的根路径添加到sys.path
project_root =str(Path(__file__).resolve().parent.parent)
for module_path in [project_root,os.path.join(project_root,"base")]:
    if not module_path in sys.path:
        sys.path.insert(0,module_path)


from base import replace_files_str as rf
from base import hold_on as ho
from base import com_log as logger
def main():
    # 检查是否有足够的参数被提供
    if len(sys.argv) < 4:
        
        logger.info("Not enough arguments provided.")
        return
                    
    _,org_folder,dest_folder,*args=sys.argv

    params=[]
    for i in range(0,len(args),2):
        params.append( (args[i],args[i+1]) )

    rf.replace_dir_str(org_folder, dest_folder,params )

if __name__ == "__main__":
    main()
    ho.hold_on()
