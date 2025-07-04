#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试删除功能 - 详细版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def test_delete_debug():
    """调试删除功能"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 删除功能详细调试 ===")
    print()
    print("🔧 修改内容：")
    print("- 添加了详细的删除日志（带emoji标识）")
    print("- 添加了快捷键设置日志")
    print("- 添加了F12测试快捷键")
    print()
    print("🧪 测试步骤：")
    print("1. 启动应用后，观察快捷键设置日志")
    print("2. 拖拽一张图片到应用")
    print("3. 从历史记录选择这张图片")
    print("4. 按Delete键 - 观察是否有🔥删除日志")
    print("5. 如果Delete键不工作，试试F12键")
    print("6. 如果F12键工作，说明快捷键机制正常，可能是Delete键被其他组件拦截了")
    print()
    print("📊 关键日志标识：")
    print("⌨️ [快捷键] - 快捷键设置相关")
    print("🔥 [删除图片] - 删除方法被调用")
    print("💬 [删除图片] - 确认对话框")
    print("✅ [删除图片] - 用户确认删除")
    print("🧹 [删除信息] - 清空UI相关")
    print("⏰ [删除图片] - 延迟验证")
    print()
    print("🎯 如果看不到🔥日志：")
    print("- 说明Delete键没有触发删除方法")
    print("- 可能是焦点问题或快捷键被拦截")
    print("- 尝试按F12键测试")
    print()
    print("开始测试...")
    
    app.exec_()

if __name__ == "__main__":
    test_delete_debug()
