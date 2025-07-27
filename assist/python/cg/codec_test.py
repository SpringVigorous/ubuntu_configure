

import os



from pathlib import Path

import sys

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import arrange_urls,postfix,codec_base64,codec_base,codec_aes

code_imp=codec_aes("1234567890123456", "1234567890123456")


