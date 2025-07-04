#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片显示功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.fluent_main_window import FluentMainWindow
from core.image_reader import ImageInfoReader

def test_image_display():
    """测试图片显示功能"""
    app = QApplication([])
    
    # 创建主窗口
    window = FluentMainWindow()
    window.show()
    
    # 测试图片路径（你需要替换为实际的图片路径）
    test_image_path = "/path/to/your/test/image.png"  # 请替换为实际路径
    
    if os.path.exists(test_image_path):
        print(f"测试图片: {test_image_path}")
        
        # 直接调用处理图片方法
        window.business_logic.process_image(test_image_path)
        
        print("图片处理完成，检查界面显示...")
        
        # 检查界面状态
        print(f"当前文件路径: {window.current_file_path}")
        print(f"正向提示词长度: {len(window.positive_prompt_text.toPlainText())}")
        print(f"负向提示词长度: {len(window.negative_prompt_text.toPlainText())}")
        print(f"图片标签是否有内容: {window.image_label.pixmap() is not None}")
        
    else:
        print(f"测试图片不存在: {test_image_path}")
        print("请修改 test_image_path 变量为实际的图片路径")
    
    # 运行应用
    app.exec_()

if __name__ == "__main__":
    test_image_display()
