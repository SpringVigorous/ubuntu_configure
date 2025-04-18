from PIL import Image, ImageFilter, ImageChops

def advanced_blur_background(foreground_path, background_path, output_path, blur_radius=15):
    # 打开图片
    foreground = Image.open(foreground_path).convert("RGBA")
    background = Image.open(background_path).convert("RGBA")
    
    # 调整大小
    background = background.resize(foreground.size)
    
    # 虚化背景
    blurred_bg = background.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 创建蒙版（基于前景的alpha通道）
    mask = foreground.split()[3]  # 获取alpha通道
    
    # 合并图片
    result = Image.composite(foreground, blurred_bg, mask)
    
    # 保存结果
    result.save(output_path)

# 使用示例
advanced_blur_background("foreground.png", "background.jpg", "output_advanced.png")