﻿
import os

import sys

from pathlib import Path
from collections.abc import Iterable

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import get_directory_sizes
    
    
def test_get_directory_sizes():

    
    results=get_directory_sizes(r"C:")

    import pandas as pd
    df=pd.DataFrame([{"cur_path":key,"size":val} for key,val in  results.items() if os.path.isdir(key)])
    dest_path=r"F:\worm_practice\cache\目录文件大小详情.xlsx"
    os.makedirs(os.path.dirname(dest_path),exist_ok=True)
    df.to_excel(dest_path,index=False)
    
if __name__ == "__main__":
    test_get_directory_sizes()