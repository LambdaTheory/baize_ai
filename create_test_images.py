#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import os

def create_test_images():
    """创建测试图片"""
    # 创建测试目录
    os.makedirs('test_images', exist_ok=True)
    
    # 创建一个简单的测试图片 (小图片，不需要缩放)
    img1 = Image.new('RGB', (100, 100), color='red')
    img1.save('test_images/small_test.png')
    print("已创建小图片: test_images/small_test.png")
    
    # 创建一个大图片 (需要缩放)
    img2 = Image.new('RGB', (800, 600), color='blue')
    img2.save('test_images/large_test.png')
    print("已创建大图片: test_images/large_test.png")
    
    return ['test_images/small_test.png', 'test_images/large_test.png']

if __name__ == "__main__":
    create_test_images() 