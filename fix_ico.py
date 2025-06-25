#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复ICO文件生成问题
"""

import os
from PIL import Image
from pathlib import Path

def main():
    print("🔖 修复ICO文件...")
    
    # 找一个现有的logo文件
    logo_files = [
        "assets/baize_logo.png",
        "assets/baize_icon.png", 
        "assets/app_icon.png",
        "assets/baize_logo_modern.png",
    ]
    
    source = None
    for f in logo_files:
        if os.path.exists(f):
            source = f
            break
    
    if not source:
        print("❌ 找不到源文件")
        return
    
    print(f"📁 使用源文件: {source}")
    
    try:
        # 打开图片
        img = Image.open(source)
        print(f"📐 原始尺寸: {img.size}")
        
        # 转换为RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建一个简单的32x32图标
        icon_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
        
        # 保存为ICO
        ico_path = "assets/icons/baize_app_icon.ico"
        icon_32.save(ico_path, format='ICO')
        
        # 检查文件大小
        size = os.path.getsize(ico_path)
        print(f"✅ ICO已保存: {ico_path}")
        print(f"📏 文件大小: {size} 字节")
        
        if size > 1000:
            print("✨ ICO文件生成成功！")
        else:
            print("⚠️ 文件可能还是太小")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 