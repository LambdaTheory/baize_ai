#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试从历史记录删除图片的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.fluent_main_window import FluentMainWindow

def debug_delete_issue():
    """调试删除问题"""
    app = QApplication([])
    
    window = FluentMainWindow()
    window.show()
    
    print("=== 调试从历史记录删除图片问题 ===")
    print()
    print("🔍 调试步骤：")
    print("1. 拖拽一张图片到应用中")
    print("2. 从历史记录中选择这张图片")
    print("3. 按Delete键删除")
    print("4. 观察控制台输出的详细日志")
    print()
    print("📊 关键日志说明：")
    print("- [删除图片] 删除前/后 - 显示删除前后的状态对比")
    print("- [清空UI] - 显示UI清空的详细过程")
    print("- [删除图片] 延迟验证 - 检查是否有异步重新加载")
    print()
    print("🎯 预期行为：")
    print("- 删除后，当前文件路径应该为 None")
    print("- 图片标签应该显示拖拽提示文本")
    print("- 提示词长度应该为 0")
    print("- 标签输入框应该为空")
    print()
    print("🐛 如果问题仍然存在：")
    print("- 检查延迟验证的日志，看是否有异步重新加载")
    print("- 如果有重新加载，说明某个组件在删除后又触发了加载")
    print("- 需要找到是哪个组件触发的重新加载")
    print()
    print("开始测试...")
    
    app.exec_()

if __name__ == "__main__":
    debug_delete_issue()
