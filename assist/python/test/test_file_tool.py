
import os

import sys

from pathlib import Path
from collections.abc import Iterable





from base import get_directory_sizes
    
    
def test_get_directory_sizes():

    
    results=get_directory_sizes(r"C:")

    import pandas as pd
    from base import worm_root

    df=pd.DataFrame([{"cur_path":key,"size":val} for key,val in  results.items() if os.path.isdir(key)])
    dest_path=worm_root/r"cache\目录文件大小详情.xlsx"
    os.makedirs(os.path.dirname(dest_path),exist_ok=True)
    df.to_excel(dest_path,index=False)
    
if __name__ == "__main__":
    test_get_directory_sizes()