#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门生成高质量ICO文件的脚本
"""

import os
from PIL import Image
from pathlib import Path


def create_high_quality_ico():
    """生成高质量的ICO文件"""
    
    print("🔖 生成高质量ICO文件...")
    
    # 查找源logo文件
    logo_files = [
        "assets/baize_logo_traditional.png",
        "assets/baize_logo_modern.png", 
        "assets/baize_logo_tech.png",
        "assets/baize_icon.png",
        "assets/baize_logo.png",
    ]
    
    source_logo = None
    for logo_file in logo_files:
        if os.path.exists(logo_file):
            source_logo = logo_file
            print(f"📁 使用源Logo: {logo_file}")
            break
    
    if not source_logo:
        print("❌ 未找到任何logo文件！")
        return False
    
    try:
        # 打开源图片
        with Image.open(source_logo) as img:
            print(f"📐 源图片尺寸: {img.size}")
            
            # 确保是RGBA模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 创建目录
            icons_dir = Path("assets/icons")
            icons_dir.mkdir(exist_ok=True)
            
            # ICO所需的标准尺寸
            ico_sizes = [16, 24, 32, 48, 64, 128, 256]
            ico_images = []
            
            print("📦 准备ICO图像...")
            for size in ico_sizes:
                try:
                    # 高质量缩放
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # 确保是RGBA模式
                    if resized.mode != 'RGBA':
                        resized = resized.convert('RGBA')
                    
                    ico_images.append(resized)
                    print(f"  ✅ 准备 {size}x{size} 图像")
                    
                except Exception as e:
                    print(f"  ❌ 处理 {size}x{size} 失败: {e}")
            
            if not ico_images:
                print("❌ 没有成功准备任何图像")
                return False
            
            # 保存ICO文件
            ico_path = icons_dir / "baize_app_icon.ico"
            print(f"💾 保存ICO文件: {ico_path}")
            
            try:
                # 使用第一个图像作为主图像，其他作为附加图像
                ico_images[0].save(
                    ico_path,
                    format='ICO',
                    sizes=[(img.width, img.height) for img in ico_images],
                )
                
                # 检查文件大小
                file_size = ico_path.stat().st_size
                print(f"✅ ICO文件生成成功！")
                print(f"📏 文件大小: {file_size:,} 字节")
                
                # 如果文件太小，可能有问题
                if file_size < 1000:
                    print("⚠️ 警告：ICO文件太小，可能生成有问题")
                    return False
                
                return True
                
            except Exception as e:
                print(f"❌ 保存ICO文件失败: {e}")
                import traceback
                traceback.print_exc()
                return False
            
    except Exception as e:
        print(f"❌ 处理源图片失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🔖 高质量ICO文件生成器")
    print("=" * 50)
    
    success = create_high_quality_ico()
    
    if success:
        print("\n✨ ICO文件生成完成！")
        print("🔧 可以用于PyInstaller --icon参数")
    else:
        print("\n❌ ICO文件生成失败！") 