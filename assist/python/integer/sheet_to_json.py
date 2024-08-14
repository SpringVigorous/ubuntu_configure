import pandas as pd
import json
import argparse
import os
import __init__
from base.com_log import logger as logger
import base.string_tools as st
import sys
# 读取 xls 文件
def read_xls(file_path,sheet_name)->pd.DataFrame:
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    return data

# 转换为 JSON 并保存
def save_as_json(data:pd.DataFrame, output_file):
    # 将 DataFrame 转换为 JSON
    json_data = data.to_json(orient='records', force_ascii=False)

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json.loads(json_data), f, ensure_ascii=False, indent=4)
        
def read_json(file_path)->pd.DataFrame:
    # 从 JSON 文件中读取数据
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def save_to_excel(df:pd.DataFrame, output_file, sheet_name):
    # 将 DataFrame 写入 Excel 文件的指定 sheet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
def create_dir_recursive(path):
    try:
        os.makedirs(path, exist_ok=True)
        logger.trace(f"Directory created: {path}")
    except OSError as error:
        logger.error(f"Directory creation failed: {error}")     
        
test_val={"old_name":["glm","GLM"],
    "new_name":["glm_new","GLM_new" ]}
#测试导出到excel
def test_export_to_excel():

    data= pd.DataFrame(test_val)
    save_to_excel(data, os.path.join(st.cur_execute_path(),"data","replace_folder_params.xlsx"), "args")


#测试导出到json文件
def test_export_to_json():

    data= pd.DataFrame(test_val)
    save_as_json(data, os.path.join(st.cur_execute_path(),"data","replace_folder_params.json"))

if __name__ == "__main__":
    
    
    # test_export_to_excel()
    # test_export_to_json()
    # sys.exit(0)
    
    parser = argparse.ArgumentParser(description=f'excel表格数据转换为json格式并保存\n')

    parser.add_argument('-f', '--filepath', type=str,  help='excel文件全路径')
    parser.add_argument('-s', '--sheetname', type=str,  help='sheet名')
    parser.add_argument('-d', '--destdir', type=str,  help='保存的目标文件夹')

    args = parser.parse_args()
    
    file_path = args.filepath
    sheet_name = args.sheetname
    output_dir = args.destdir
    
    if file_path is None or  not os.path.exists(file_path):
        logger.error(f"文件 {file_path} 不存在")
        sys.exit(0)
    if sheet_name is None or  len(sheet_name)<1:
        logger.error(f"sheet名不能为空")
        sys.exit(0)
        
    if output_dir is  None or len(output_dir)<1:
        output_dir=os.path.dirname(file_path)
    create_dir_recursive(output_dir)
        
    output_file=output_dir+"/"+os.path.basename(file_path).split(".")[0]+".json"
    data = read_xls(file_path,sheet_name)
    save_as_json(data, output_file)
    logger.info(f"Data has been saved to {output_file}" )
  

#pyinstaller  --onefile --distpath exe -p . -p base -p integer  --add-data "config/settings.yaml:./config" --add-data "config/.secrets.yaml:./config" --distpath .\exe integer/sheet_to_json.py    