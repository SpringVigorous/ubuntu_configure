from bs4 import BeautifulSoup
from base import exception_decorator
from lxml import html
def set_count(lst, count,default=None):
    if not lst:
        return [default] * count
    
    # 如果列表长度已经大于或等于 count，直接返回
    if len(lst) >= count:
        return lst[:count]
    
    # 计算需要填充的次数
    fill_count = count - len(lst)
    
    # 用列表的最后一个元素进行填充
    filled_lst = lst + [lst[-1]] * fill_count
    
    return filled_lst
def get_node(soup, tag_name, **kwargs):
    tag = soup.find(tag_name,**kwargs)
    return tag

def set_node_attibute(node,attribute_name, attribute_value):
    set_node_attibutes(node,[attribute_name],[attribute_value])
def set_node_attibutes(node,attribute_names, attribute_values):
    if node:
        for attribute_name, attribute_value in zip(attribute_names,attribute_values):
            node[attribute_name] = attribute_value

def get_node_attibutes(node,attribute_names:list,default_vals:list=None):
    if not attribute_names:
        return default_vals
    
    
    default_vals=set_count(default_vals,len(attribute_names),0)
    if node:
        result=[]
        for attribute_name, attribute_value in  zip(attribute_names,default_vals):
            if attribute_name in node.attrs:
                result.append(node[attribute_name])
            else:
                result.append(attribute_value)
        return result
    return default_vals
def get_node_attibute(node,attribute_name,default_val):

    return get_node_attibutes(node,[attribute_name],[default_val])[0]

def set_attribute(html_str, tag_name, attribute_name, attribute_value, **kwargs):
    soup = BeautifulSoup(html_str, 'lxml')
    set_node_attibute(get_node(soup, tag_name,**kwargs),attribute_name, attribute_value)

    # return soup.prettify()
    return str(soup)

def set_attributes(html_str, tag_name, attribute_names:list, attribute_values:list, **kwargs):
    soup = BeautifulSoup(html_str, 'lxml')
    set_node_attibutes(get_node(soup, tag_name,**kwargs),attribute_names, attribute_values)
    # return soup.prettify()
    return str(soup)
def get_attribute(html_str, tag_name, attribute_name,default_val, **kwargs):
    soup = BeautifulSoup(html_str, 'lxml')
    return  get_node_attibute(get_node(soup, tag_name,**kwargs),attribute_name, default_val)


def get_attributes(html_str, tag_name, attribute_names:list,default_vals:list=None, **kwargs):
    soup = BeautifulSoup(html_str, 'lxml')
    return  get_node_attibutes(get_node(soup, tag_name,**kwargs),attribute_names, default_vals)


def get_nodes(html_str, tag_name, **kwargs):
    soup = BeautifulSoup(html_str, 'lxml')
    tag = soup.find_all(tag_name,**kwargs)
    return tag

def tree_by_str(html_str):
    return html.fromstring(html_str)


def pretty_tree(tree):
    if tree is None:
        return None

    
    return html.tostring(tree, pretty_print=True, encoding="unicode")


if __name__=="__main__":
    # 假设这是你的 HTML 文本
    html_text = """
    <div data-v-dc2e79da="" class="comments-container">
        <div data-v-31146f99="" data-v-dc2e79da="" class="end-container"> - THE END - </div>
        <!---->
    </div>
    """
    
    html_text=set_attribute(html_text, 'div', 'count', 10 ,class_='comments-container' )
    val=get_attribute(html_text, 'div', 'count' ,class_='comments-container')
    print(val)