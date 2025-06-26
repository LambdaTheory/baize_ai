#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试浏览器拖拽功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def test_browser_drag():
    """测试浏览器拖拽功能"""
    print("🧪 开始测试浏览器拖拽功能...")
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = FluentMainWindow()
    window.show()
    
    print("✅ 应用已启动，请尝试以下操作：")
    print("1. 打开SD WebUI或ComfyUI在浏览器中")
    print("2. 生成一张图片")
    print("3. 将图片从浏览器拖拽到应用中")
    print("4. 检查是否能正确处理图片")
    print("5. 查看控制台输出和应用提示信息")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_browser_drag() 