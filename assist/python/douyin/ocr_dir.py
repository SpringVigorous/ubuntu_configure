import sys

from pathlib import Path
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import OCRProcessor,img_files
from ocr_result_to_word import ocr_results_to_word

import json

def main(org_dir):
    # 初始化处理器
    processor = OCRProcessor(lang='ch')
    org_dir=Path(org_dir)
    dest_pic_dir=org_dir.parent.joinpath(f'{org_dir.name}_ocr')
    dest_text_dir=org_dir.parent.joinpath(f'{org_dir.name}_result')

    os.makedirs(dest_pic_dir,exist_ok=True)
    os.makedirs(dest_text_dir,exist_ok=True)
    
    for org_file in img_files(org_dir):
        cur_path=Path(org_file)
        
        
        
        dest_pic_path=os.path.join(dest_pic_dir,cur_path.relative_to(org_dir))
        os.makedirs(os.path.dirname(dest_pic_path),exist_ok=True)
        
        
        
        
        # 处理单张图片
        result_image,orc_results=processor.process_image(
            img_path=org_file,
            output_path=dest_pic_path,
            font_path='simhei.ttf'
        )
        dest_text_path=Path(os.path.join(dest_text_dir,cur_path.relative_to(org_dir))).with_suffix('.docx')

        
        boxes, texts, scores=orc_results
        results=[[_box,[_text,_scores]]  for _box,_text,_scores in  zip(boxes,texts,scores)]
        
        #缓存数据
        json.dump(results,open(dest_text_path.with_suffix(".json"),'w',encoding='utf-8'),ensure_ascii=False,indent=4)
        ocr_results_to_word(ocr_results=results,output_path=str(dest_text_path),img_width=result_image.width,img_height=result_image.height)

if __name__ == '__main__':
    org_dir=r"F:\worm_practice\taobao\五味食养\广告法"

    main(org_dir)
    
    # json_path=r"F:\worm_practice\taobao\五味食养\广告法_result\2caab56e-9ed4-4a0e-bdbc-86ec936d356b.json"
    
    # results= json.load(open(json_path,"r",encoding="utf-8"))
    # ocr_results_to_word(ocr_results=results,output_path=Path(json_path).with_suffix(".docx"),img_width=960,img_height=5412)
    