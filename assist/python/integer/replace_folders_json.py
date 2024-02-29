
import sys
import os
import json


from pathlib import Path
# 将当前脚本所在项目的根路径添加到sys.path
project_root =str(Path(__file__).resolve().parent.parent)
for module_path in [project_root,os.path.join(project_root,"base")]:
    if not module_path in sys.path:
        sys.path.insert(0,module_path)


# import base.add_sys_path as asp
# asp.add_sys_path(os.path.join(project_root,"base"))
from base.com_log import logger as logger


# logger.info(sys.path)

import  base.replace_files_str as rf
import  base.hold_on as ho
import  base.com_decorator as cd

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
    if logger :
        logger.Warning("json文件示例如下：")
        logger.Warning(json.dumps(template_json, indent=4))




@cd.details_decorator
@cd.exception_decorator
def main():
    # 检查是否有足够的参数被提供
    if len(sys.argv) < 2:
        if logger:
            logger.error("Not enough arguments provided.")
            return
    _,json_file,*args=sys.argv
    if not (os.path.exists(json_file) and os.path.isfile(json_file)):
        if logger:
            logger.error("json文件未找到")
        show_error()
        return 
    # 使用内置的open()函数以读模式打开文件
    with open(json_file, 'r') as file:
        # 使用json.load()方法将文件内容解析为Python对象（通常是字典）
         data= json.load(file)
    
    if not "items" in data:
        if logger:
            logger.error("json文件格式错误:")
        show_error()
        return

    has_error=False
    for index,item  in  enumerate(data["items"]):
        try:
            if logger :
                logger.info(f"第{index}个替换数据：{str(item) }")      
            if not rf.replace_files_str(item["source_folder"],item["dest_folder"],item["replace_args"]):
                has_error=True
            if logger :
                result_str="成功" if not has_error else "失败"
                fun=logger.error if has_error else logger.info
                fun(f"第{index}个替换: {result_str}")      

        except KeyError:
            has_error=True
    if has_error:
        show_error()

if __name__ == "__main__":
    main()
    if logger :
        logger.info("替换完成")
    ho.hold_on()