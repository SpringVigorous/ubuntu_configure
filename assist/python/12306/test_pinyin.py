from pypinyin import pinyin,  Style

from prettytable import PrettyTable

def to_pinyin(word):
    
    ls=pinyin(word, style=Style.NORMAL)
    
    return "".join("".join(i) for i in ls)
    
    



if __name__ == '__main__':
    
    ls=["上海","北京","天津","郑州"]
    dest=list(map(to_pinyin,ls))
    merge=list(zip(ls,dest))
    
    
    table=PrettyTable()
    table.field_names=["城市","拼音"]
    for i in merge:
        table.add_row(i)
    print(table)