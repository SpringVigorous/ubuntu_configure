

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



        
        
        
        

replace_strs=[ [ "glm", "glm_new" ,False,False ], [ "GLM", "GLM_new" ,False,False ] ]



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
        self.dest_folder =dest.strip() 
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
        "new_name": "hm_kernel",
        "is_reg":False,
        "ignore_case":False,
    },
    {
        "old_name": "TOOLS",
        "new_name": "HM_KERNEL",
        "is_reg":False,
        "ignore_case":False,
    },
    {
        "old_name": "ExampleClass",
        "new_name": "hm_test",
        "is_reg":False,
        "ignore_case":False,
    },
    {
        "old_name": "EXAMPLE_CLASS",
        "new_name": "HM_TEST",
        "is_reg":False,
        "ignore_case":False,
    },
    {
        "old_name": "example_class",
        "new_name": "hm_test",
        "is_reg":False,
        "ignore_case":False,
    }
    ]
    return json.dumps(data,indent=4)

def project_json_str():
    data={
        "project": [
            {
                "old_name": "project_template",
                "new_name": "world",
                "is_reg": True,
                "ignore_case": True
            },
            {
                "old_name": "class_template",
                "new_name": "kitty",
                "is_reg": True,
                "ignore_case": True
            }
        ],
        "copy_files": [
            {
                "old_name": "(.*?)(class_template)\\.(h|cpp|hpp)$",
                "new_name": ["hello1","hello2","hello3","kitty1","kitty2","kitty3"],
                "is_reg": True,
                "ignore_case": True
            }
        ]
    }
    return json.dumps(data,indent=4)

def show_error():

    if logger :
        logger.warning("json文件示例如下：\n{}".format(full_json_str()))

def show_eg():
    error_str=f"必须参数 -r(--replace)缺失：\n\
    1.参数为json路径(-o和-d参数可不填写),内容如下：\n{full_json_str()}\n\
    2.json文件路径(-o和-d参数必须填写),内容如下：\n{json.dumps(replace_strs,indent=4)}\n或{each_json_str()}\n或{project_json_str()}\n\
    3.参数为替换对列表(-r参数必须填写),内容如下：\n{args_json_str()}"

    logger.error(f"参数示例如下：{error_str}")

#针对所有参数均在 json中
def handle_full_json(json_data):
    dest_datas= []
    for index,item  in  enumerate(json_data):
        dest_datas.append(EachReplaceData(item["source_folder"],item["dest_folder"],item["replace_args"]))
    return dest_datas

#针对 替换参数在 字段 "replace_args"
def handle_replace_json(org_agrs,dest_agrs,json_data):
    dest_datas= [EachReplaceData(org_agrs,dest_agrs,json_data)]
    return dest_datas


#针对 json中仅有  替换字段，按顺序取其值
def handle_items_json(org_agrs,dest_agrs,json_data):
    dest_datas= []
    each_data=[]
    
    for one_data in json_data:
        
        # each_data.append([one_data["old_name"],one_data["new_name"]])
        each_data.append(list(one_data.values()))
    
    dest_datas.append(EachReplaceData(org_agrs,dest_agrs,each_data))
    return dest_datas

#针对 参数是 替换值的组合文本
def handle_params(org_agrs,dest_agrs,replace_agrs):
    dest_datas= []
    cur_datas=[]
    for items in replace_agrs.split("|"):
        cur_datas.append( items.split("@"))
    dest_datas.append(EachReplaceData(org_agrs,dest_agrs,cur_datas))     

    return dest_datas



def handle_replace_all(org_agrs,dest_agrs,replace_agrs):
    pass



class ParseParams:
    def __init__(self):
        self.special_files=None
        self.dest_datas= []
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
            show_eg()
            return


        full_json=False
        replace_json=False   
        is_replace_list=not (os.path.exists(replace_agrs) and os.path.isfile(replace_agrs))
        json_data=None
        items_json=None
        project_json=None

        copy_files=None
        if not is_replace_list:
            # 使用内置的open()函数以读模式打开文件
            with open(replace_agrs, 'r',encoding="utf-8-sig") as file:
                # 使用json.load()方法将文件内容解析为Python对象（通常是字典）
                    json_data= json.load(file)
            full_json=json_data["item"] if "items" in json_data else None
            replace_json=json_data["replace_args"] if "replace_args" in json_data else None
            
            project_json=json_data["project"] if "project" in json_data else None
   
            copy_files=json_data["copy_files"] if "copy_files" in json_data else None
            
            first_data=json_data[0] if not copy_files else None
            items_json=json_data if  first_data and "old_name" in first_data and "new_name" in first_data else None
            # if not(full_json or replace_json or items_json) or full_json==replace_json:
            if not(full_json or replace_json or items_json or project_json):
                logger.error(f"json文件格式错误,示例如下：\n{full_json_str()}\n或者{args_json_str()}")
                return

        #填充替换数据
        
        if full_json :
            self.dest_datas=handle_full_json(json_data)
        elif replace_json:
            self.dest_datas=handle_replace_json(org_agrs,dest_agrs,json_data)
        elif items_json:
            self.dest_datas=handle_items_json(org_agrs,dest_agrs,json_data)
        elif project_json:
            self.dest_datas=handle_items_json(org_agrs,dest_agrs,project_json)
            if copy_files:
                self.special_files=handle_items_json(org_agrs,dest_agrs,copy_files)
        else:
            self.dest_datas=handle_params(org_agrs,dest_agrs,replace_agrs)    
        
        
        

@cd.exception_decorator(show_eg)
@cd.details_decorator
def main():
       
    parser=ParseParams()
               
    for index,items  in  enumerate(zip(parser.special_files,parser.dest_datas)):
        
        
        special,item=items
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
            if not special:
                repalce_fun= rf.replace_dir_str if is_fold else rf.replace_file_str        
                success=repalce_fun(cur_source,cur_dest,item.replace_args,rf.CoverType.NO_COVER)
            elif is_fold:
                success=rf.clone_dir_str(cur_source,cur_dest,item.replace_args,special.replace_args,rf.CoverType.NO_COVER)
            flag=f"成功" if success else "失败"
            func= logger.trace if success else logger.error
            func(f"{info_pre}替换{flag}")
        except Exception as e:
            logger.error(f"{info_pre}替换失败,原因：{e}")
            
            
            
            

if __name__ == "__main__":
    logger.info("替换开始")

    show_eg()
    main()
    
    logger.info("替换完成")
    # ho.hold_on()
    
    
#打包成exe
#pyinstaller  --onefile --distpath exe -p . -p base -p integer  --add-data "config/settings.yaml:./config" --add-data "config/.secrets.yaml:./config" --distpath .\exe integer/replace_folders_files.py    

# 使用方式：
 #1[ -o F:/test_data/glm -d F:/test_data/ -r glm@glm_new|GLM@GLM_new ]
 #2[ -r G:/练习集/C++/6.20/1.json ]
 #3[ -o F:/test_data/glm -d F:/test_data/ -r G:/练习集/C++/6.20/2.json ]


#推荐用例 F:\test\ubuntu_configure\assist\python\assist\replace_params.json
# -o F:/test_data/glm -d F:/test_data/ -r assist\replace_params.json
# python.exe integer\replace_folders_files.py -o 'F:/test/cmake_project/src/project_template' -d 'F:/test/cmake_project/src/' -r 'assist/replace_params.json'  
# python.exe integer\replace_folders_files.py -o 'F:/test/cmake_project/src/project_template' -d 'F:/test/cmake_project/src/' -r 'assist/replace_params_project_files.json'  

