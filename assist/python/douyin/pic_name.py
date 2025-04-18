import os
import re
import pandas as pd
import sys

from pathlib import Path

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import as_normal,logger_helper,UpdateTimeType


target_dir = r'F:\店铺素材'
xlsx_file = os.path.join(target_dir,'图片名.xlsx')
sheet_name="图片"

def to_xlsx(df:pd.DataFrame):
    """将DataFrame写入指定sheet，并保留其他sheet内容"""
    # 读取所有sheet
    all_sheets = pd.read_excel(xlsx_file, sheet_name=None, engine='openpyxl')
    # 更新目标sheet的数据
    all_sheets[sheet_name] = df
    # 使用openpyxl引擎写入，保留原有文件结构
    with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
        for name, data in all_sheets.items():
            data.to_excel(writer, sheet_name=name, index=False)

def from_xlsx():
    if os.path.exists(xlsx_file):
        df = pd.read_excel(xlsx_file,sheet_name=sheet_name)
        return df

def extract_file_info()->pd.DataFrame:
    # 定义目标目录和正则表达式
    pattern = re.compile(r'^([^_a-zA-Z]+)_([^_]+)_(\d+)$')  # 匹配 类型_特点_编号 结构
    results = []
    unmatch_results=[]
    logger=logger_helper("获取jpg文件",target_dir)
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            # 检查是否为jpg文件（不区分大小写）
            if file.lower().endswith('.jpg'):
                # 分离文件名和扩展名
                basename = os.path.splitext(file)[0]
                result={"图片名": file,}
                # 进行正则匹配
                match = pattern.match(basename)
                if match:
                    # 提取匹配信息并存储
                    type_, feature, number = match.groups()
                    result.update({
                        '类型': type_,
                        '视图': feature,
                        '编号': int(number)
                    })
                else:
                    result.update({
                        '类型': "",
                        '视图': "未定义",
                        '编号': -1
                    })
                
                dest=results if match else unmatch_results
                
                dest.append(result)

    results.extend(unmatch_results)
    # 创建DataFrame并导出Excel
    if results:
        logger.info(f'成功导出 {len(results)} 条记录到 图片名.xlsx')
        cur_df= pd.DataFrame(results)
        #获取xlsx文件的信息
        xls_df=from_xlsx()
        if xls_df is not None:
            # 获取df2中'图片名'列的所有值
            files = cur_df['图片名'].tolist()

            # 删除df1中'图片名'列不在files中的行
            cur_df = xls_df[xls_df['图片名'].isin(files)]
        return cur_df
    else:
        logger.info("没有找到匹配的文件")


def rename_files(df:pd.DataFrame):
    # 获取需要处理的行：当两列值不相等时
    different_rows = df[df['图片名'] != df['新文件名']]
    logger=logger_helper("重命名")
    # 遍历处理每一行
    for index, row in different_rows.iterrows():
        old_name = row['图片名']
        new_name = row['新文件名']
        
        # 构建完整路径
        src_path = os.path.join(target_dir, old_name)
        dst_path = os.path.join(target_dir, new_name)
        logger.update_target(detail=f"{old_name} -> {new_name}")
        # 验证源文件存在性
        if not os.path.exists(src_path):
            logger.warn(f"⚠️ 源文件不存在: {src_path}，跳过重命名")
            continue
            
        # 验证目标文件唯一性
        if os.path.exists(dst_path):
            logger.warn(f"⚠️ 目标文件已存在: {dst_path}，跳过重命名")
            continue
        
        # 执行重命名操作
        try:
            os.rename(src_path, dst_path)
            logger.info(f"✅ 成功重命名：{old_name} -> {new_name}")
        except Exception as e:
            logger.error(f"❌ 重命名失败：{old_name} -> {new_name}，错误信息：{str(e)}")

def reset_number(df:pd.DataFrame):
    # 新增名称列
    df['名称'] = df['类型'] + '_' + df['视图']
    
    df['编号']=df['编号'].fillna(-1)
    # 编号处理逻辑
    df['编号'] = df['编号'].astype(int)  # 转换为整数便于计算
    
    def assign_numbers(group):
        existing_numbers = set(group[group['编号'] > 0]['编号'])
        mask = group['编号'] <= 0
        
        current_num = 1
        available_nums:list[int] = []
        
        for _ in range(sum(mask)):
            while current_num in existing_numbers:
                current_num += 1
            available_nums.append(current_num)
            current_num += 1
        
        # 更新编号列
        group.loc[mask, '编号'] = available_nums if available_nums else None
        return group
    
    # 分组处理
    df = df.groupby('名称', group_keys=False).apply(assign_numbers, include_groups=False)
    df["新文件名"]=df.apply(lambda x:f"{x['类型']}_{x['视图']}_{int(x['编号']):03}.jpg" if x['类型'] and x['视图'] else x["图片名"],axis=1)
    rename_files(df)
    # # 清理临时列
    # df.drop(columns=['编号'], inplace=True)
    return df


if __name__ == '__main__':
    df=extract_file_info()
    df=reset_number(df)
    to_xlsx(df) 