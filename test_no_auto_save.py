#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试去掉自动保存功能后的效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def test_no_auto_save():
    """测试去掉自动保存功能"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 去掉自动保存功能测试 ===")
    print("修改内容：")
    print("✅ 去掉了用户输入变化触发的自动保存")
    print("✅ 去掉了5秒定时器自动保存")
    print("✅ 简化了删除图片的逻辑")
    print("✅ 保留了AI自动打标后的自动保存")
    print("✅ 保留了手动保存按钮功能")
    print()
    print("测试步骤：")
    print("1. 拖拽一张图片到应用中")
    print("2. 图片加载后会自动保存一次（首次加载）")
    print("3. 在标签框中输入内容 - 应该不会触发自动保存")
    print("4. 等待10秒 - 应该不会有自动保存")
    print("5. 按Delete键删除图片 - 应该立即清空，不会恢复")
    print("6. 再次拖拽图片，使用AI自动打标功能")
    print("7. AI打标完成后应该自动保存")
    print("8. 手动点击保存按钮应该正常工作")
    print()
    print("预期效果：")
    print("- 删除图片后不会自动恢复")
    print("- 用户输入不会触发自动保存")
    print("- 只有AI打标和手动保存会保存数据")
    print("- 界面操作更加可控")
    
    app.exec_()

if __name__ == "__main__":
    test_no_auto_save()
