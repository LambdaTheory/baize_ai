#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试从历史记录删除图片的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def test_delete_from_history():
    """测试从历史记录删除图片"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 从历史记录删除图片测试 ===")
    print("问题描述：")
    print("1. 从历史记录选择图片A")
    print("2. 图片A的信息显示在界面上")
    print("3. 按Delete键删除图片A")
    print("4. 确认删除")
    print("5. 问题：界面仍然显示图片A的信息，没有清空")
    print()
    print("测试步骤：")
    print("1. 先拖拽几张图片到应用中，让历史记录有数据")
    print("2. 从历史记录中点击选择一张图片")
    print("3. 确认图片信息显示在界面上")
    print("4. 按Delete键删除当前图片")
    print("5. 确认删除")
    print("6. 检查界面是否完全清空")
    print()
    print("预期效果：")
    print("- 删除后图片显示区域应该显示拖拽提示")
    print("- 提示词区域应该清空")
    print("- 标签输入框应该清空")
    print("- 所有参数信息应该清空")
    print()
    print("调试信息：")
    print("- 注意观察控制台的[清空UI]相关日志")
    print("- 如果清空失败，会显示具体的错误信息")
    
    app.exec_()

if __name__ == "__main__":
    test_delete_from_history()
