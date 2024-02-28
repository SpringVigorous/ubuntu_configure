
import sys
from pathlib import Path
# 将当前脚本所在项目的根路径添加到sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
# 现在尝试相对导入
from base import replace_files_str as rf

def main():
    # 检查是否有足够的参数被提供
    if len(sys.argv) < 4:
        print("Not enough arguments provided.")
        return
                    
    _,org_folder,dest_folder,*args=sys.argv

    params=[]
    for i in range(0,len(args),2):
        params.append( (args[i],args[i+1]) )

    rf.replace_files_str(org_folder, dest_folder,params )

if __name__ == "__main__":
    main()