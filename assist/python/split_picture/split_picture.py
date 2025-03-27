from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
import cv2
from math import ceil
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def get_image_size(image_path):
    # 打开图片
    image = Image.open(image_path)
    return image.size


    

def _split_images(image_path, split_height, reserved_height, overlap_height)->list[Image.Image]:
    # 打开图片
    image = Image.open(image_path)
    width, height = image.size


    
    content_height=split_height-reserved_height*2
    # 计算需要拆分的图片数量
    if height<=content_height or split_height <= overlap_height:
        print("错误：拆分高度必须大于重叠高度。")
        return image
    
    num_splits = ceil((float(height)-2*content_height)/(content_height- 2*overlap_height))+2

    split_images = []
    left = 0
    right = width
    top=0
    bottom = content_height
    for i in range(num_splits):
        # 计算当前裁剪区域的左上角和右下角坐标
        if i>0:
            top=bottom-overlap_height
            bottom=min(top+content_height, height)


        # 裁剪图片
        cropped_image = image.crop((left, top, right, bottom))

        # 创建一个新的图片，上下添加留白，背景为白色

        combined_image = Image.new('RGB', (width, split_height), color=(255, 255, 255))

        # 将裁剪的图片粘贴到新图片中间
        combined_image.paste(cropped_image, (0, overlap_height))

        split_images.append(combined_image)

    return split_images



def split_image(image_path, split_height, reserved_height, overlap_height):
    cur_path=Path(image_path)
    title = cur_path.stem
    lst=[]
    
    
    for i,image in enumerate(_split_images(image_path, split_height, reserved_height, overlap_height)):
        # 生成新的文件名
        new_filename =os.path.join(cur_path.parent, f"{title}_{i + 1}.jpg")
        # 保存裁剪后的图片
        image.save(new_filename)
        print(f"已保存图片: {new_filename}")
        lst.append(new_filename)

    return lst



def images_to_pdf(image_paths, output_pdf_path):
    try:
        pdf = canvas.Canvas(output_pdf_path, pagesize=letter)

        for img_path in image_paths:
            img = Image.open(img_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            pdf_width = letter[0] - 15  # 留出一些边距
            pdf_height = pdf_width / aspect_ratio

            pdf.drawImage(img_path, 10, letter[1] - pdf_height - 10, width=pdf_width, height=pdf_height)
            pdf.showPage()

        pdf.save()
        print(f"已生成 PDF 文件: {output_pdf_path}")
        return True
    except Exception as e:
        print(f"发生错误: {e}")
    

def large_images_to_pdf(image_path,  reserved_height, overlap_height):
    pic_width,_ = get_image_size(image_path)
    std_width,std_height = 210,297

    std_wh_scale=std_width/std_height
    projection_sclale=pic_width/std_width
    
    split_height = ceil(pic_width/std_wh_scale)  # 替换为你指定的高度
    overlap_height = ceil(overlap_height*projection_sclale)  # 替换为你指定的重叠高度
    reserved_height = ceil(reserved_height*projection_sclale)  # 替换为你指定的预留高度
    
    # 拆分图片
    images = split_image(image_path, split_height, reserved_height, overlap_height)

    if images:
        # 生成 PDF 文件
        pdf_path = os.path.splitext(image_path)[0] + ".pdf"
        if not images_to_pdf(images, pdf_path):
            return
    
    for temp_path in images:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return 
    # 删除原始图片
    if os.path.exists(image_path):
        os.remove(image_path)
    
if __name__ == "__main__":
    image_path = r"D:\Document\DownLoad\Saved Pictures\Stable Diffusion模型-新手入门.png"  # 替换为你的图片路径
    overlap_height = 5  # 替换为你指定的重叠高度
    reserved_height = 15  # 替换为你指定的预留高度
    large_images_to_pdf(image_path, reserved_height, overlap_height)

