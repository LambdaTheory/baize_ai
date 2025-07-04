#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建DMG背景图片的脚本
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_dmg_background():
    """创建DMG安装界面的背景图片"""
    
    # 设置画布尺寸 (标准DMG窗口大小)
    width, height = 640, 400
    
    # 创建渐变背景
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 创建从白色到浅灰色的渐变
    for y in range(height):
        # 计算渐变色
        ratio = y / height
        gray_value = int(255 - (ratio * 30))  # 从255到225的渐变
        color = (gray_value, gray_value, gray_value)
        draw.line([(0, y), (width, y)], fill=color)
    
    # 添加标题区域的深色背景
    title_height = 80
    draw.rectangle([(0, 0), (width, title_height)], fill=(45, 45, 45))
    
    # 尝试加载字体
    try:
        # macOS系统字体
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 28)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
        instruction_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
    except:
        # 备用字体
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        instruction_font = ImageFont.load_default()
    
    # 添加标题文字
    title_text = "白泽AI"
    subtitle_text = "AI图片信息提取工具"
    
    # 计算文字位置（居中）
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    
    # 绘制标题
    draw.text((title_x, 15), title_text, fill='white', font=title_font)
    draw.text((subtitle_x, 50), subtitle_text, fill=(200, 200, 200), font=subtitle_font)
    
    # 添加安装说明
    instructions = [
        "安装方法：",
        "1. 将左侧的应用图标拖拽到右侧的 Applications 文件夹",
        "2. 在 Launchpad 或 Applications 文件夹中找到白泽AI",
        "3. 双击启动应用"
    ]
    
    y_offset = height - 120
    for i, instruction in enumerate(instructions):
        if i == 0:
            # 标题使用粗体
            draw.text((30, y_offset), instruction, fill=(60, 60, 60), font=subtitle_font)
        else:
            draw.text((30, y_offset), instruction, fill=(100, 100, 100), font=instruction_font)
        y_offset += 20
    
    # 添加装饰性元素
    # 绘制一个微妙的边框
    draw.rectangle([(0, 0), (width-1, height-1)], outline=(180, 180, 180), width=1)
    
    # 在中间添加一个箭头指示
    arrow_y = height // 2 - 20
    arrow_points = [
        (width//2 - 30, arrow_y),
        (width//2 - 10, arrow_y - 10),
        (width//2 - 10, arrow_y - 5),
        (width//2 + 30, arrow_y - 5),
        (width//2 + 30, arrow_y + 5),
        (width//2 - 10, arrow_y + 5),
        (width//2 - 10, arrow_y + 10)
    ]
    draw.polygon(arrow_points, fill=(100, 150, 255), outline=(80, 130, 235))
    
    # 保存图片
    background_path = "assets/dmg_background.png"
    img.save(background_path, 'PNG', quality=95)
    print(f"DMG背景图片已创建: {background_path}")
    
    return background_path

if __name__ == "__main__":
    create_dmg_background()
