

import sys
import os
import json
import argparse

#废弃，统一用 replace_folders_files.py代替


from base.com_log import logger_helper


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
    error_logger=logger_helper("json示例",json.dumps(template_json,indent=4)) 
    error_logger.warn("展示错误信息")




# 仅一个参数：json文件路径
@cd.details_decorator
@cd.exception_decorator()
def main():
    
    replace_logger=logger_helper("替换文件夹",sys.argv)
    
    # 检查是否有足够的参数被提供
    if len(sys.argv) < 2:

        replace_logger.error("失败","Not enough arguments provided.")
        return
    _,json_file,*args=sys.argv
    if not (os.path.exists(json_file) and os.path.isfile(json_file)):

        replace_logger.error("失败","json文件未找到")
        show_error()
        return 
    # 使用内置的open()函数以读模式打开文件
    with open(json_file, 'r',encoding="utf-8-sig") as file:
        # 使用json.load()方法将文件内容解析为Python对象（通常是字典）
         data= json.load(file)
    
    if not "items" in data:

        replace_logger.error("失败","json文件格式错误:")
        show_error()
        return

    has_error=False
    for index,item  in  enumerate(data["items"]):
        try:

            replace_logger.info("开始",f"第{index}个替换数据：{str(item) }")      
            if not rf.replace_dir_str(item["source_folder"],item["dest_folder"],item["replace_args"]):
                has_error=True

            result_str="成功" if not has_error else "失败"
            fun=replace_logger.error if has_error else replace_logger.info
            fun(f"第{index}个替换: {result_str}")      

        except KeyError:
            has_error=True
    if has_error:
        show_error()

if __name__ == "__main__":
    main()
    replace_logger=logger_helper("替换",sys.argv)

    replace_logger.info("成功")
    # ho.hold_on()