from collections import Counter

def unique(original_list):
    counter = Counter(original_list)
    return list(counter.keys())

def dict_first_item(val:dict):
    if not dict:
        return
    
    key= next(iter(val))
    return key,val[key]

def dict_val(cols:dict,key):
    if not cols:
        return

    return cols.get(key)