
import sys
import os
import json


from pathlib import Path
# 将当前脚本所在项目的根路径添加到sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
# 现在尝试相对导入
from base import replace_files_str as rf



def show_error():
    template_json={
    "items": [
        {
            "source_folder": "F:/test_data/glm",
            "dest_folder": "F:/test_data/",
            "replace_args": [
                [
                    "glm",
                    "glm_new"
                ],
                [
                    "GLM",
                    "GLM_new"
                ]
            ]
        }
    ]
}
    print("json文件示例如下：")
    print(json.dumps(template_json, indent=4))
def main():
    # 检查是否有足够的参数被提供
    if len(sys.argv) < 2:
        print("Not enough arguments provided.")
        return
                    
    _,json_file,*args=sys.argv
    if not (os.path.exists(json_file) and os.path.isfile(json_file)):
        print("json文件未找到")
        show_error()
        return 
    # 使用内置的open()函数以读模式打开文件
    with open(json_file, 'r') as file:
        # 使用json.load()方法将文件内容解析为Python对象（通常是字典）
         data= json.load(file)
    
    if not "items" in data:
        print("json文件格式错误:")
        show_error()
        return

    has_error=False
    for item  in data["items"]:
        try:
            rf.replace_files_str(item["source_folder"],item["dest_folder"],item["replace_args"])
        except KeyError:
            has_error=True
    if has_error:
        show_error()

if __name__ == "__main__":
    main()