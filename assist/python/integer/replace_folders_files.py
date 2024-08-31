

import sys
import os
import json
import argparse

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

from base.string_tools import *



        
        
        
        

replace_strs=[ [ "glm", "glm_new" ], [ "GLM", "GLM_new" ] ]



def full_json_str():
    template_json={
    "items": [
        {
            "source_folder": "F:/test_data/glm",
            "dest_folder": "F:/test_data/",
            "replace_args": replace_strs
        }
    ]}
    return json.dumps(template_json,indent=4)

class EachReplaceData:
    def __init__(self, source: str, dest: str, replace_args: list):
        self.source_folder = source.strip()
        self.dest_folder = dest.strip()
        self.replace_args =replace_args
        # self.replace_args =[i.strip() for i in replace_args]
        
    def __str__(self) -> str:
        return json.dumps(self.__dict__,indent=4)
        

def args_json_str():
    template_json={"replace_args": replace_strs}
    return json.dumps(template_json,indent=4)

def each_json_str():
    data=[
    {
        "old_name": "tools",
        "new_name": "hm_kernel"
    },
    {
        "old_name": "TOOLS",
        "new_name": "HM_KERNEL"
    },
    {
        "old_name": "ExampleClass",
        "new_name": "hm_test"
    },
    {
        "old_name": "EXAMPLE_CLASS",
        "new_name": "HM_TEST"
    },
    {
        "old_name": "example_class",
        "new_name": "hm_test"
    }
    ]
    return json.dumps(data,indent=4)



def show_error():

    if logger :
        logger.warning("json文件示例如下：\n{}".format(full_json_str()))




@cd.details_decorator
@cd.exception_decorator
def main():
    # 检查是否有足够的参数被提供
    # if len(sys.argv) < 2:
        # if logger:
        #     logger.error("Not enough arguments provided.")
        #     return
    
    eg_example="""    
 #1[ -o F:/test_data/glm -d F:/test_data/ -r glm@glm_new|GLM@GLM_new ]
 #2[ -r G:/练习集/C++/6.20/1.json ]
 #3[ -o F:/test_data/glm -d F:/test_data/ -r G:/练习集/C++/6.20/2.json ]

    """
    
    parser = argparse.ArgumentParser(description=f'替换文件夹或文件中的特定名称\n eg: {eg_example}')

    parser.add_argument('-r', '--replace', type=str,  help=f'必选项：替换的特定名称对 1.列表或者2.json路径（仅替换参数{replace_strs}\n或全参数{full_json_str()}\n或表格形式{each_json_str()}）')
    parser.add_argument('-o', '--org', type=str,  help='原始文件（夹）')
    parser.add_argument('-d', '--dest', type=str,  help='目标文件（夹）')

    args = parser.parse_args()
    
    org_agrs = args.org
    dest_agrs = args.dest
    replace_agrs = args.replace

    
    has_org=not invalid(org_agrs)
    has_dest=not invalid(dest_agrs)
    has_replace= not invalid(replace_agrs)
    


    if not has_replace:
        error_str=f"必须参数 -r(--replace)缺失：\n\
            1.参数为json路径(-o和-d参数可不填写),内容如下：\n{full_json_str()}\n\
            2.json文件路径(-o和-d参数必须填写),内容如下：\n{replace_strs}或{each_json_str()}\n\
            3.参数为替换对列表(-r参数必须填写),内容如下：\n{args_json_str()}"
        
        logger.error("error_str")
        return


    full_json=False
    replace_json=False   
    replace_list=not (os.path.exists(replace_agrs) and os.path.isfile(replace_agrs))
    json_data=None
    if not replace_list:
        # 使用内置的open()函数以读模式打开文件
        with open(replace_agrs, 'r',encoding="utf-8-sig") as file:
            # 使用json.load()方法将文件内容解析为Python对象（通常是字典）
                json_data= json.load(file)
        full_json="items" in json_data
        replace_json="replace_args" in json_data
        items_json="old_name" in json_data[0] and "new_name" in json_data[0]
        # if not(full_json or replace_json or items_json) or full_json==replace_json:
        if not(full_json or replace_json or items_json):
            logger.error(f"json文件格式错误,示例如下：\n{full_json_str()}\n或者{args_json_str()}")
            return
    

    #填充替换数据
    dest_datas= []
    if full_json :
        for index,item  in  enumerate(json_data["items"]):
            dest_datas.append(EachReplaceData(item["source_folder"],item["dest_folder"],item["replace_args"]))
    elif replace_json:
        dest_datas.append(EachReplaceData(org_agrs,dest_agrs,json_data["replace_args"]))
    elif items_json:
        each_data=[]
        
        for one_data in json_data:
            each_data.append([one_data["old_name"],one_data["new_name"]])
        
        dest_datas.append(EachReplaceData(org_agrs,dest_agrs,each_data))
    else:
        cur_datas=[]
        for items in replace_agrs.split("|"):
            cur_datas.append( items.split("@"))
        dest_datas.append(EachReplaceData(org_agrs,dest_agrs,cur_datas))           
                
    for index,item  in  enumerate(dest_datas):
        success=False
        try:
            info_pre=f"第{index}个替换数据：{str(item) }"
            cur_source=item.source_folder
            cur_dest=item.dest_folder
                
            is_fold=os.path.isdir(cur_source)
            if not is_fold:
                if invalid(cur_dest):
                    cur_dest=os.path.dirname(cur_source)
                elif os.path.isfile(cur_dest):
                    cur_dest=os.path.dirname(cur_dest)
            
            repalce_fun= rf.replace_dir_str if is_fold else rf.replace_file_str        
            success=repalce_fun(cur_source,cur_dest,item.replace_args)
            flag=f"成功" if success else "失败"
            func= logger.trace if success else logger.error
            func(f"{info_pre}替换{flag}")
        except Exception as e:
            logger.error(f"{info_pre}替换失败,原因：{e}")

if __name__ == "__main__":
    logger.info("替换开始")
    main()
    logger.info("替换完成")
    # ho.hold_on()
    
    
#打包成exe
#pyinstaller  --onefile --distpath exe -p . -p base -p integer  --add-data "config/settings.yaml:./config" --add-data "config/.secrets.yaml:./config" --distpath .\exe integer/replace_folders_files.py    