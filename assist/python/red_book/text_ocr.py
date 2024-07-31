####ocr文本检测
from paddleocr import PaddleOCR 
img_path=r"F:\教程\C++\双生子\cad.png"
ocr=PaddleOCR(lang='ch')
result=ocr.ocr(img_path)


#画出识别图片
from PIL import Image, ImageDraw, ImageFont
def draw_ocr(image, boxes, txts, scores, font_path):
    draw = ImageDraw.Draw(image)
    
    # 加载字体
    font = ImageFont.truetype(font_path, size=25)  # 字体大小可以根据需要调整
    
    for i, box in enumerate(boxes):
        left_bot, right_bot, right_top, left_top = box
        x0=min(left_bot[0],right_bot[0],right_top[0],left_top[0])
        y0=min(left_bot[1],right_bot[1],right_top[1],left_top[1])
        x1=max(left_bot[0],right_bot[0],right_top[0],left_top[0])
        y1=max(left_bot[1],right_bot[1],right_top[1],left_top[1])
        
        left_bot=[x0,y0]
        right_bot=[x1,y0]
        right_top=[x1,y1]
        left_top=[x0,y1]
        
        
        # 画出边界框
        # for x1, y1, x2, y2 in [(left_bot, right_bot, right_top, right_bot), (right_top, right_bot, right_top, left_top),
        #                 (right_top, left_top, left_bot, left_top), (left_bot, left_top, left_bot, right_bot)]:
        #     draw.line([(x1, y1), (x2, y2)], fill='black', width=2)
        border=[x0,y0,x1,y1]
        draw.rectangle(border, outline='red', width=2)
        
        # 添加文本
        text = f"{txts[i]} ({scores[i]:.2f})"  # 格式化文本，显示得分
        text_size = draw.textbbox((0,0),text, font=font)
        text_height=text_size[3]-text_size[1]
        text_width=text_size[2]-text_size[0]
        # text_size= font.getsize(text)
        
        
        # 计算文本位置，使其紧贴在边界框上方
        
        y2=y0-text_height- 5
        
        # 如果文本会超出图像边界，则调整位置
        if y2 < 0:
            y2 = y1 + 5
        
        text_rect=[x0, y2, x0 + text_width, y2 + text_height]
        # 画出文本背景
        draw.rectangle(text_rect, fill='black')
        
        # 在背景上写文本
        draw.text(text_rect, text, font=font, fill='white')
    
    return image

result=result[0]
image=Image.open(img_path).convert("RGB" )
boxes =[line[0]for line in result]
txts=[line[1][0]for line in result]
scores =[line[1][1]for line in result]
im_show=draw_ocr(image,boxes,txts,scores,font_path='C:\\Windows\\Fonts\\simhei.ttf') ###米
# im_show=Image.fromarray(im_show)
im_show.save("result 3.png")


# 识别多张图片，将结果保存至excel中
from paddleocr import PaddleOCR
import os
import pandas as pd
img_path =os.path.dirname(img_path)
ocr =PaddleOCR(lang='ch')
paths =os.listdir(img_path)
imgs,txts =[],[ ]
for p in paths:
    if p.split(".")[1] not in ['png','jpg','jpeg']:
        continue
    result=ocr.ocr("%s/%s"%(img_path,p))
    txt =[line[1][0]for line in result[0]]
    txt ="\n".join(txt)
    imgs .append(p)
    txts.append(txt)
d=pd.DataFrame({'imgs':imgs,'txts':txts})
d.to_excel("img_txt.xlsx",index = None )


