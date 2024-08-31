
#sec_symbol_show.json信息整理的json文件
from dataclasses import replace
from itertools import count
from sys import meta_path
from matplotlib.pyplot import axis
import pandas as pd
import json
from os import path, system
import os



def read_json(filefullpath: str):
    data = None
    with open(filefullpath, "r", encoding='utf-8-sig') as f:
        data = json.loads(f.read())

    pf = pd.json_normalize(
        data["data"]["View"]["ugc_season"],record_path=["sections","episodes"], meta=["id", "title", "mid"] ,meta_prefix="sec.", max_level=10, errors="ignore")



    # 输出到excel文档
    (filePath, __) = path.splitext(filefullpath)
    outPath = f"{filePath}-tab.xlsx"
    with pd.ExcelWriter(outPath) as writer:
        pf.to_excel(writer, sheet_name="calalog")

    system(outPath)
if __name__ == '__main__':

    read_json(r"F:\教程\哔哩哔哩\双笙子佯谬\现代C++项目实战\html\0_现代C++项目实战.json")
