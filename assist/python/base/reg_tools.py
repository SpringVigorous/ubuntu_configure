import re

def find_all(input_string,pattern,keys:list|tuple):
    matches=re.findall(pattern, input_string)
    if keys:
        return [ dict(zip(keys, item)) for item in  matches]

    return matches
    
