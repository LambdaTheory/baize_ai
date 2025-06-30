#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试翻译功能的调试脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.fluent_prompt_editor_widget import PromptEditorPanel

def test_translation():
    """测试翻译功能"""
    app = QApplication(sys.argv)
    
    # 创建编辑器面板
    editor = PromptEditorPanel("测试翻译")
    editor.show()
    
    print("=== 开始测试翻译功能 ===")
    
    # 模拟输入中文
    test_text = "杰作, 最高质量, 美丽的女孩, 长发, 微笑"
    print(f"模拟输入中文: {test_text}")
    
    # 设置文本
    editor.english_edit.setPlainText(test_text)
    
    # 手动触发文本改变事件
    editor.on_english_text_changed()
    
    print("已触发文本改变事件，等待翻译...")
    
    # 定时器检查状态
    def check_status():
        print(f"当前状态检查:")
        print(f"  原始输入: '{editor.original_input_text}'")
        print(f"  是否中文: {editor.input_is_chinese}")
        print(f"  翻译文本: '{editor.translated_text}'")
        print(f"  英文提示词: {editor.english_prompts}")
        print(f"  翻译定时器活跃: {editor.translation_timer.isActive()}")
        if hasattr(editor, 'translation_thread') and editor.translation_thread:
            print(f"  翻译线程运行: {editor.translation_thread.isRunning()}")
        print(f"  显示文本: '{editor.display_text.toPlainText()}'")
        print("-" * 50)
    
    # 定期检查状态
    timer = QTimer()
    timer.timeout.connect(check_status)
    timer.start(1000)  # 每秒检查一次
    
    # 5秒后手动触发翻译（如果还没开始）
    def manual_trigger():
        print("5秒后手动触发翻译...")
        if editor.translation_timer.isActive():
            editor.translation_timer.stop()
        editor.auto_translate()
    
    manual_timer = QTimer()
    manual_timer.singleShot(5000, manual_trigger)
    
    # 15秒后退出
    def exit_app():
        print("=== 测试完成，退出应用 ===")
        app.quit()
    
    exit_timer = QTimer()
    exit_timer.singleShot(15000, exit_app)
    
    # 启动应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_translation() 