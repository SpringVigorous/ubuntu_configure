from lxml import etree
from base import global_logger
# {"href": "链接", "text": "文本"}
def extract_href_and_text_from_html(html_str: str) -> list:
    """
    从HTML字符串中提取符合条件的href和对应a节点的文本值
    匹配规则：
    1. main节点的class属性包含"main-content"（模糊匹配）
    2. div节点的class属性包含"tab-content active"连续子串（模糊匹配）
    3. 提取该div下所有ul/li/a的href属性和文本值
    
    :param html_str: 待解析的HTML字符串
    :return: 提取到的结果列表（元素为字典），格式：[{"href": "链接", "text": "文本"}, ...]
             解析失败/无匹配时返回空列表
    """
    # 初始化返回列表
    result_list = []
    
    # 边界条件：入参为空字符串/非字符串时直接返回空列表
    if not isinstance(html_str, str) or len(html_str.strip()) == 0:
        return result_list
    with global_logger().raii_target("网页提取urls",html_str) as logger:
        try:
            # 1. 解析HTML（修复不规范HTML，指定编码避免乱码）
            parser = etree.HTMLParser(encoding='utf-8')
            tree = etree.HTML(html_str.strip(), parser=parser)
            
            # 2. 核心XPath表达式：定位到符合条件的a节点（而非直接提取href）
            xpath_expr = (
                "//main[contains(@class, 'main-content')]"  # 匹配class含main-content的main节点
                "//div[contains(@class, 'tab-content active')]"  # 匹配class含tab-content active的div
                "//ul/li/a"  # 定位到a节点（后续提取href和文本）
            )
            
            # 3. 执行XPath查询，获取所有符合条件的a节点
            a_nodes = tree.xpath(xpath_expr)
            
            # 4. 遍历a节点，提取href和文本值
            for a_node in a_nodes:
                # 提取href属性（无href时设为空字符串）
                href = a_node.get('href', '').strip()
                # 提取a节点的文本（去除首尾空格，无文本时设为空字符串）
                text = a_node.text.strip() if a_node.text else ''
                # 仅当href非空时添加到结果（避免空链接）
                if href:
                    result_list.append({
                        "href": href,
                        "text": text
                    })
            
        except Exception as e:
            # 捕获解析异常，返回空列表并打印错误信息
            logger.error("异常",f"解析HTML时发生错误：{str(e)}")
    
    return result_list


# ------------------- 函数使用示例 -------------------
if __name__ == "__main__":
    # 测试用的HTML字符串
    test_html = """
    <main class="main-content boeEdd">
        <div class="tab-container Bzdfce">
            <div class="other-div">
                <div class="DCzDDz tab-content active 123">
                    <ul>
                        <li><a href="/d/18843/684600f02c21a.html">第50集完结</a></li>
                        <li><a href="/d/18843/684600f02c208.html">第49集</a></li>
                        <li><a href="">空链接</a></li>  <!-- 空href会被过滤 -->
                    </ul>
                </div>
            </div>
        </div>
    </main>
    <main class="other-main 12345">
        <div class="tab-content active">
            <ul><li><a href="/无效链接.html">无效内容</a></li></ul>
        </div>
    </main>
    """
    
    # 调用函数提取href和文本
    result = extract_href_and_text_from_html(test_html)
    
    # 输出结果
    print("提取到的href和文本列表：")
    for item in result:
        print(f"文本：{item['text']} | 链接：{item['href']}")
    # 也可直接打印整个列表
    # print(result)