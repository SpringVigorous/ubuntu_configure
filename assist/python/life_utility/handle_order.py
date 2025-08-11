from bs4 import BeautifulSoup
import os
import pandas as pd

import sys

from pathlib import Path
import os




def handle_sku(file_path):
    """
    解析XML文件，提取每个item-live的src属性和prop-item-text的文本
    
    参数:
        file_path: XML文件路径
        
    返回:
        包含提取信息的列表，每个元素是一个字典
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        return []
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # 解析XML内容
        soup = BeautifulSoup(xml_content, 'lxml')
        
        # 查找所有带有item-live类的元素
        item_live_elements = soup.find_all('div', class_='item-live')
        
        result = []
        # 提取每个元素的信息
        for element in item_live_elements:
            # 获取img标签的src属性
            img_tag = element.find('img')
            src = img_tag.get('src') if img_tag else None
            
            # 获取prop-item-text类的span标签文本
            text_tag = element.find('span', class_='prop-item-text')
            text = text_tag.get_text(strip=True) if text_tag else None
            
            if src or text:
                result.append({
                    'src': src,
                    'text': text
                })
        
        return result
    
    except Exception as e:
        print(f"解析文件时出错: {str(e)}")
        return []
def export_to_excel(table_data, file_path):
    
    # 打印结果
    if table_data:
        df=pd.DataFrame(table_data)
        dest_path=Path(file_path).with_suffix(".xlsx")
        df.to_excel(dest_path)
def test_sku(xml_file_path):
    
    # 解析文件并获取结果
    items = handle_sku(xml_file_path)
    
    # 打印结果
    if items:
        export_to_excel(items, xml_file_path)


def handle_order(xml_file_path):
    """
    从XML文件中提取表格数据
    
    参数:
        xml_file_path: XML文件路径
        
    返回:
        表格数据列表，每个元素是一行数据的字典
    """
    # 检查文件是否存在
    if not os.path.exists(xml_file_path):
        print(f"错误: 文件 '{xml_file_path}' 不存在")
        return []
    
    try:
        # 读取XML文件内容
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # 解析XML内容
        soup = BeautifulSoup(xml_content, 'lxml')
        
        # 找到表格主体
        table_body = soup.find('tbody')
        if not table_body:
            print("未找到表格主体(tbody)")
            return []
        
        # 存储所有行数据
        table_data = []
        
        # 遍历每一行
        for row in table_body.find_all('tr'):
            row_data = {}
            
            # 获取第一列数据 (产品描述)
            col1 = row.find('td', {'data-next-table-col': '0'})
            if col1:
                
                img_url=col1.find('img',class_="selector-prop-img")
                if img_url:
                    row_data['链接']=img_url.get('src')
                
                product_text = col1.find('span', class_='gyp-order-cell-text')
                row_data['产品描述'] = product_text.get_text(strip=True) if product_text else None
            
            # 获取第二列数据 (属性)
            col2 = row.find('td', {'data-next-table-col': '1'})
            if col2:
                attribute_text = col2.find('span', class_='gyp-order-cell-text')
                row_data['属性'] = attribute_text.get_text(strip=True) if attribute_text else None
            
            # 获取第三列数据 (价格)
            col3 = row.find('td', {'data-next-table-col': '2'})
            if col3:
                price_text = col3.find('span', class_='gyp-order-price-value')
                row_data['价格'] = price_text.get_text(strip=True) if price_text else None
            
            # 获取第四列数据 (数量)
            col4 = row.find('td', {'data-next-table-col': '3'})
            if col4:
                quantity_text = col4.find('span', class_='gyp-order-num-value')
                row_data['数量'] = quantity_text.get_text(strip=True) if quantity_text else None
            
            # 获取第五列数据 (选择数量)
            col5 = row.find('td', {'data-next-table-col': '4'})
            if col5:
                input_element = col5.find('input')
                row_data['选择数量'] = input_element.get('value') if input_element else None
            
            table_data.append(row_data)
        
        return table_data
    
    except Exception as e:
        print(f"解析文件时出错: {str(e)}")
        return []

def _get_table_data(soup,root_fag:str,cell_flag:str):
    table_body = soup.find(root_fag)
    if not table_body:
        return 
    table_rows = table_body.find_all("tr")
        # 存储所有行数据
    table_data = []
    
    # 遍历每一行
    for row in table_body.find_all('tr'):
        row_cells = []
        tables=row.find_all(cell_flag)
        # 遍历当前行中的所有td
        for td in tables:
            # 初始化单元格数据
            cell_data = {
                'col_index': None,  # 存储data-next-table-col属性值
                'text': None,       # 单元格文本内容
                'img_src': None     # 图片src属性
            }
            
            # 获取data-next-table-col属性
            if 'data-next-table-col' in td.attrs:
                # 尝试转换为整数（属性值通常是数字）
                try:
                    cell_data['col_index'] = int(td['data-next-table-col'])
                except ValueError:
                    cell_data['col_index'] = td['data-next-table-col']
            
            # 检查td中是否有img元素，获取src属性
            img_element = td.find('img')
            if img_element and 'src' in img_element.attrs:
                cell_data['img_src'] = img_element['src']
            
            # 检查td中是否有input元素（如数量选择器）
            input_element = td.find('input')
            if input_element and 'value' in input_element.attrs:
                cell_data['text'] = input_element['value']
            else:
                # 获取td中的文本内容
                cell_text = ' '.join(td.get_text(strip=True, separator=' ').split())
                cell_data['text'] = cell_text if cell_text else None
            
            row_cells.append(cell_data)
        
        table_data.append(row_cells)
    
    return table_data
def extract_complete_table_data(xml_file_path):
    """
    从XML文件中提取表格完整数据，包括：
    - td的data-next-table-col属性
    - 单元格文本内容
    - 单元格内img的src属性
    
    参数:
        xml_file_path: XML文件路径
        
    返回:
        表格数据列表，每个元素是一行数据的列表，
        每个单元格是包含'col_index'、'text'和'img_src'的字典
    """
    # 检查文件是否存在
    if not os.path.exists(xml_file_path):
        print(f"错误: 文件 '{xml_file_path}' 不存在")
        return []
    
    try:
        # 读取XML文件内容
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # 解析XML内容
        soup = BeautifulSoup(xml_content, 'lxml')
        
        def _property_value(lst:list[dict],property_name):
            results=[]
            for item in lst:
                result=[]
                for inner in item:
                    result.append(inner.get(property_name,None))
                results.append(result)
            return results

        headers=_get_table_data(soup,"thead","th")
        rows=_get_table_data(soup,"tbody","td")

        table_names=_property_value(headers,"text")
        if not table_names:
            return
        table_names=table_names[0]
        
        row_names=_property_value(rows,"text")
        row_urls=_property_value(rows,'img_src')
        
        
        results=[]
        for names_row,urls_row in zip(row_names,row_urls):
            result={}
            for header,name,url in zip(table_names,names_row,urls_row):
                if not name:
                    continue
                result[header]=name
                if url:
                    result[header+"_url"]=url
            results.append(result)
        return results
    except Exception as e:
        print(f"解析文件时出错: {str(e)}")
        return []

        
    
def test_order(xml_file_path):

    
    # 提取表格数据
    table_data = handle_order(xml_file_path)
    table_data = extract_complete_table_data(xml_file_path)
    
    # 打印结果
    if table_data:
        export_to_excel(table_data,xml_file_path)

        

    

if __name__ == "__main__":
    # 替换为你的XML文件路径
    xml_file_path = r"F:\test\ubuntu_configure\assist\python\life_utility\sku.xml"
    
    # 解析文件并获取结果
    test_sku(xml_file_path)
    

    xml_file_path = r"F:\test\ubuntu_configure\assist\python\life_utility\order_detail.xml"
    test_order(xml_file_path)