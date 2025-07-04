#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除图片功能修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def test_delete_functionality():
    """测试删除功能"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 删除图片功能测试 ===")
    print("1. 拖拽一张图片到应用中")
    print("2. 等待图片信息加载完成")
    print("3. 按Delete键或Backspace键删除图片")
    print("4. 确认删除后，检查以下内容：")
    print("   - 图片显示区域应该清空并显示拖拽提示")
    print("   - 提示词区域应该清空")
    print("   - 标签输入框应该清空")
    print("   - 文件信息应该清空")
    print("   - 不应该出现自动还原的情况")
    print("5. 再次拖拽图片，确认功能正常")
    
    app.exec_()

if __name__ == "__main__":
    test_delete_functionality()
