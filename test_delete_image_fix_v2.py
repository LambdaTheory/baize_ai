#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除图片功能修复 - 第二版
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.fluent_main_window import FluentMainWindow

def test_delete_functionality():
    """测试删除功能"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 删除图片功能测试 - 第二版 ===")
    print("修复内容：")
    print("1. 添加删除状态标志，防止删除时自动恢复")
    print("2. 删除时临时断开历史记录信号")
    print("3. 自动保存和用户输入变化时检查删除状态")
    print("4. 清空信息时不刷新历史记录")
    print()
    print("测试步骤：")
    print("1. 拖拽一张图片到应用中")
    print("2. 等待图片信息加载完成")
    print("3. 在标签框中输入一些内容（测试自动保存）")
    print("4. 等待5秒让自动保存触发")
    print("5. 按Delete键或Backspace键删除图片")
    print("6. 确认删除后，检查以下内容：")
    print("   - 图片显示区域应该清空并显示拖拽提示")
    print("   - 提示词区域应该清空")
    print("   - 标签输入框应该清空")
    print("   - 文件信息应该清空")
    print("   - 不应该出现自动还原的情况")
    print("   - 控制台应该显示删除相关的调试信息")
    print("7. 等待10秒，确认没有自动恢复")
    print("8. 再次拖拽图片，确认功能正常")
    print()
    print("调试信息说明：")
    print("- [删除图片] 开头的信息表示删除流程")
    print("- [自动保存] 开头的信息表示自动保存流程")
    print("- [清空信息] 开头的信息表示清空流程")
    print("- [历史记录] 开头的信息表示历史记录相关操作")
    
    # 添加一个定时器来监控状态
    def check_status():
        if hasattr(window, 'current_file_path'):
            print(f"[状态监控] 当前文件路径: {window.current_file_path}")
            print(f"[状态监控] 自动保存启用: {window.auto_save_enabled}")
            print(f"[状态监控] 删除标志: {getattr(window, '_deleting_image', False)}")
        
    timer = QTimer()
    timer.timeout.connect(check_status)
    timer.start(10000)  # 每10秒检查一次状态
    
    app.exec_()

if __name__ == "__main__":
    test_delete_functionality()
