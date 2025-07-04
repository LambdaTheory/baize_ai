#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试历史记录删除修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def test_history_delete_fix():
    """测试历史记录删除修复"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 历史记录删除修复测试 ===")
    print()
    print("🔧 修复内容：")
    print("- 在删除历史记录时检查当前显示的图片是否被删除")
    print("- 如果当前显示的图片被删除，自动清空主界面")
    print("- 添加了详细的删除日志")
    print()
    print("🧪 测试步骤：")
    print("1. 拖拽几张图片到应用中，建立历史记录")
    print("2. 从历史记录中点击选择一张图片A")
    print("3. 确认图片A的信息显示在主界面")
    print("4. 选中图片A的记录，点击'删除选中'按钮")
    print("5. 确认删除")
    print("6. 观察主界面是否自动清空")
    print()
    print("📊 关键日志：")
    print("[删除记录] - 删除操作相关日志")
    print("- 会显示删除的文件路径")
    print("- 会显示是否清空了主界面")
    print()
    print("✅ 预期效果：")
    print("- 删除记录后，如果当前显示的图片被删除")
    print("- 主界面应该自动清空，显示拖拽提示")
    print("- 提示词、标签等信息都应该清空")
    print()
    print("🎯 额外测试：")
    print("- 也可以测试'清空全部'按钮")
    print("- 清空全部后主界面也应该自动清空")
    print()
    print("开始测试...")
    
    app.exec_()

if __name__ == "__main__":
    test_history_delete_fix()
