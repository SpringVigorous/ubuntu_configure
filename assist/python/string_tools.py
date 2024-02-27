def replace_list_tuple_str(content:str,replace_list_tuple=None)->str:
    if not replace_list_tuple or len(replace_list_tuple)==0:
        return content
    for c, d in replace_list_tuple:
        content = content.replace(c, d)
    return content