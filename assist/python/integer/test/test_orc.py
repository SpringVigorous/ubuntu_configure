import pytesseract
from PIL import Image
import numpy


pytesseract.pytesseract.tesseract_cmd = r'D:\Tool\tesseract_ocr\tesseract.exe'
#导入图片文件的地址
image= Image.open(r'F:\3rd_repositories\PandaOCR.Pro\images\快捷语言1.jpg')
#将图片转换为灰度图像
arrayd=image.convert("L")
#设置阀值为200，超过这个阀值，图片像素设置为255，否则让像素为0，表示黑色
#如果发现识别不准确，可以适当的调整这个阀值
thud=180
#将图片转换为NumPy数组
arrd=numpy.array(arrayd)
arrd=numpy.where(arrd >thud,255,0)
image=Image.fromarray(arrd.astype("uint8"))
print(pytesseract.image_to_string(image))