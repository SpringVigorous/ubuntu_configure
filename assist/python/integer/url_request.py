import requests
from requests_toolbelt import MultipartEncoder

import argparse
import sys
import json
from base.com_log import logger as logger
def get_html(text_str:str):
    # 构造请求头
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '___rl__test__cookies=1723689997608; OUTFOX_SEARCH_USER_ID_NCOO=495220760.946177; ASPSESSIONIDQSSTABSS=AOEJBEICCFAKLKANPOLJLFOI; __51cke__=; __tins__1497471=%7B%22sid%22%3A%201723689275882%2C%20%22vd%22%3A%203%2C%20%22expires%22%3A%201723691739807%7D; __51laig__=8',
        'Host': 'www.mytju.com',
        'Origin': 'http://www.mytju.com',
        'Referer': 'http://www.mytju.com/classcode/tools/messyCodeRecover.asp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36'
    }

    # 构造请求体
    data = {
        'myAction': 'autoRecover',
        'inputStr': (text_str
        )
    }

    # 发送 POST 请求
    response = requests.post(
        'http://www.mytju.com/classcode/tools/messyCodeRecover.asp',
        headers=headers,
        data=data
    )
    
    logger.trace(f"请求内容：\n{json.dumps(data,indent=4,ensure_ascii=False)}")

    
    # 检查响应状态码
    if response.status_code == 200:
        logger.trace(f"请求成功\n{response.text}")
        with open("request.html","w",encoding="utf-8") as f:
            f.write(response.text)
        # print(response.text)
    else:
        logger.error(f"请求失败，状态码：{response.status_code}")
    # # 请求后关闭
    # response.close()
    return response.text

from bs4 import BeautifulSoup
import requests
import base.string_tools as st

def parse_html(html,srcCode="UTF-8",destCode="GBK"):
    # soup = BeautifulSoup(html, 'lxml')
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string
    # 查找所有的 <tr> 元素
    tr_elements = soup.find_all('tr')

    # 遍历每个 <tr> 元素并提取 <td> 数据
    for tr in tr_elements:
        td_elements = tr.find_all('td')
        if len(td_elements) !=3:
            continue
        # 输出每个 <td> 元素的文本内容
        dest_code,src_code,out_str=  [td.get_text(strip=True) for td in td_elements]
        logger.trace(f"目标编码：{dest_code}\t源编码：{src_code}\t输出结果：{out_str}")

        if st.equal_ignore_case(src_code,srcCode) and st.equal_ignore_case(dest_code,destCode):
            logger.info(f"转换成功{out_str.encode("utf-8")}")
            return

        
        


        
if __name__ == '__main__':
        # test_export_to_excel()
    # test_export_to_json()
    # sys.exit(0)
    args_str=' '.join(sys.argv)
    
    logger.trace(f"参数:\t{args_str}")
    
    parser = argparse.ArgumentParser(description=f'乱码转换工具\n')
    parser.add_argument('-t', '--orgstr', type=str,  help='待转化的文本')
    parser.add_argument('-s', '--sourcecode', type=str,  help='源码编码')
    parser.add_argument('-d', '--destcode', type=str,  help='目标编码')

    args = parser.parse_args()
    
    org_str = args.orgstr
    source_code = args.sourcecode
    dest_code = args.destcode
    
    if st.invalid(org_str):
        sys.exit(0)
    
    if st.invalid(source_code):
        source_code="UTF-8"
        logger.info(f"默认源码编码为：{source_code}")
    
    if st.invalid(dest_code):
        dest_code="GBK"
        logger.info(f"默认目标编码为：{dest_code}")
    
    parse_html(get_html(org_str),source_code,dest_code)


