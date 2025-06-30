#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 单个提示词编辑面板
包含输入框、预览和标签显示
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QScrollArea, QFrame, QPushButton, QLabel, 
                            QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from qfluentwidgets import (FlowLayout, PlainTextEdit, InfoBar, InfoBarPosition)

from .fluent_styles import FluentColors, FluentSpacing
from .fluent_prompt_components import PromptTag
from core.translator import get_translator


class TranslationWorker(QThread):
    """翻译工作线程"""
    finished = pyqtSignal(list, dict)  # 英文提示词列表, 英文→中文映射
    error = pyqtSignal(str)
    
    def __init__(self, text):
        super().__init__()
        self.text = text
        
    def run(self):
        try:
            print(f"[翻译线程] 开始翻译: {self.text}")
            translator = get_translator()
            english_prompts, translation_map = translator.smart_translate(self.text)
            
            print(f"[翻译线程] 翻译完成: {len(english_prompts)} 个提示词")
            self.finished.emit(english_prompts, translation_map)
            
        except Exception as e:
            print(f"[翻译线程] 翻译失败: {e}")
            self.error.emit(str(e))


class PromptEditorPanel(QWidget):
    """单个提示词编辑面板"""
    
    def __init__(self, title="提示词编辑", parent=None):
        super().__init__(parent)
        self.title = title
        self.english_prompts = []
        self.translation_map = {}  # 英文→中文映射
        self.prompt_tags = []
        
        # 定时器
        self.input_timer = QTimer()
        self.input_timer.setSingleShot(True)
        self.input_timer.timeout.connect(self.start_translation)
        
        self.translation_worker = None
        self.mapping_worker = None
        self.parent_widget = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        
        # 左侧区域
        left_container = self.create_left_area()
        
        # 右侧标签区域
        right_container = self.create_tags_area()
        
        # 设置比例 (3:2)
        main_layout.addWidget(left_container, 3)
        main_layout.addWidget(right_container, 2)
        
        self.setLayout(main_layout)
        
    def create_left_area(self):
        """创建左侧输入和预览区域"""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 输入区域
        input_frame = self.create_input_area()
        
        # 预览区域
        preview_frame = self.create_preview_area()
        
        layout.addWidget(input_frame)
        layout.addWidget(preview_frame, 1)
        container.setLayout(layout)
        
        return container
        
    def create_input_area(self):
        """创建输入区域"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题和复制按钮
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("提示词输入:")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(28, 28)
        self.copy_btn.setToolTip("复制英文提示词")
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 6px;
                background-color: {FluentColors.get_color('bg_secondary')};
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {FluentColors.get_color('bg_tertiary')};
                border-color: {FluentColors.get_color('accent')};
            }}
            QPushButton:pressed {{
                background-color: {FluentColors.get_color('accent')};
                color: white;
            }}
        """)
        self.copy_btn.clicked.connect(self.copy_prompts)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.copy_btn)
        
        # 输入框
        self.input_edit = PlainTextEdit()
        self.input_edit.setPlaceholderText("请输入中文或英文提示词，用逗号分隔...")
        self.input_edit.setFixedHeight(100)
        self.input_edit.setPlainText("masterpiece, best quality, ultra detailed")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.input_edit)
        frame.setLayout(layout)
        
        return frame
        
    def create_preview_area(self):
        """创建预览区域"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("英文预览:")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        # 预览框
        self.preview_edit = PlainTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setPlaceholderText("这里将显示英文提示词...")
        self.preview_edit.setStyleSheet(f"""
            PlainTextEdit {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 6px;
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_secondary')};
                padding: 8px;
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.preview_edit, 1)
        frame.setLayout(layout)
        
        return frame
        
    def create_tags_area(self):
        """创建标签区域"""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("提示词标签:")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 6px;
                background-color: {FluentColors.get_color('bg_primary')};
            }}
            QScrollBar:vertical {{
                background-color: {FluentColors.get_color('bg_secondary')};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {FluentColors.get_color('accent')};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {FluentColors.get_color('text_secondary')};
            }}
        """)
        
        # 标签容器
        self.tags_widget = QWidget()
        self.tags_layout = FlowLayout(self.tags_widget)
        self.tags_layout.setContentsMargins(12, 12, 12, 12)
        self.tags_layout.setHorizontalSpacing(6)
        self.tags_layout.setVerticalSpacing(6)
        
        self.tags_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        scroll_area.setWidget(self.tags_widget)
        
        layout.addWidget(title_label)
        layout.addWidget(scroll_area, 1)
        container.setLayout(layout)
        
        return container
        
    def setup_connections(self):
        """设置信号连接"""
        self.input_edit.textChanged.connect(self.on_input_changed)
        self.input_edit.focusOutEvent = self.on_focus_out
        
    def on_input_changed(self):
        """输入改变时的处理"""
        # 停止之前的定时器
        self.input_timer.stop()
        
        # 获取当前输入
        current_text = self.input_edit.toPlainText().strip()
        
        if not current_text:
            # 输入为空，清空所有内容
            self.english_prompts = []
            self.translation_map = {}
            self.update_display()
            return
        
        # 2.5秒后开始翻译
        self.input_timer.start(2500)
        
    def on_focus_out(self, event):
        """输入框失去焦点时立即翻译"""
        PlainTextEdit.focusOutEvent(self.input_edit, event)
        
        current_text = self.input_edit.toPlainText().strip()
        if current_text and self.input_timer.isActive():
            self.input_timer.stop()
            self.start_translation()
            
    def start_translation(self):
        """开始翻译"""
        current_text = self.input_edit.toPlainText().strip()
        if not current_text:
            return
        
        # 显示翻译状态
        self.preview_edit.setPlainText("正在翻译...")
        
        # 停止之前的翻译线程
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.quit()
            self.translation_worker.wait()
        
        # 创建新的翻译线程
        self.translation_worker = TranslationWorker(current_text)
        self.translation_worker.finished.connect(self.on_translation_finished)
        self.translation_worker.error.connect(self.on_translation_error)
        self.translation_worker.start()
        
    def on_translation_finished(self, english_prompts, translation_map):
        """翻译完成"""
        self.english_prompts = english_prompts
        
        # 合并翻译映射，保留已有的映射关系
        if self.translation_map:
            # 保留现有映射，添加新的映射
            for english, chinese in translation_map.items():
                self.translation_map[english] = chinese
        else:
            self.translation_map = translation_map
        
        print(f"[面板] 翻译完成: {len(english_prompts)} 个英文提示词")
        print(f"[面板] 总映射关系: {len(self.translation_map)} 个")
        
        self.update_display()
        
        # 触发保存
        if self.parent_widget and hasattr(self.parent_widget, 'save_history_data'):
            self.parent_widget.save_history_data()
            
    def on_translation_error(self, error_msg):
        """翻译错误"""
        print(f"[面板] 翻译错误: {error_msg}")
        self.preview_edit.setPlainText(f"翻译失败: {error_msg}")
        
    def update_display(self):
        """更新显示"""
        self.update_preview()
        self.update_tags()
        
    def update_preview(self):
        """更新预览框"""
        if self.english_prompts:
            preview_text = ", ".join(self.english_prompts)
            self.preview_edit.setPlainText(preview_text)
        else:
            self.preview_edit.setPlainText("")
            
    def update_tags(self):
        """更新标签显示"""
        # 清空现有标签
        for tag in self.prompt_tags:
            self.tags_layout.removeWidget(tag)
            tag.setParent(None)
            tag.deleteLater()
        self.prompt_tags.clear()
        
        # 创建新标签
        for english in self.english_prompts:
            chinese = self.translation_map.get(english, "")
            
            # 确保中文翻译有效且与英文不同
            if chinese and chinese.strip() and chinese.strip() != english.strip():
                tag = PromptTag(english, chinese)
            else:
                tag = PromptTag(english, "")  # 没有有效中文翻译时只显示英文
                
            tag.deleted.connect(self.on_tag_deleted)
            
            self.tags_layout.addWidget(tag)
            self.prompt_tags.append(tag)
            
    def on_tag_deleted(self, english_text, chinese_text):
        """处理标签删除"""
        if english_text in self.english_prompts:
            self.english_prompts.remove(english_text)
            
        if english_text in self.translation_map:
            del self.translation_map[english_text]
            
        self.update_display()
        
    def copy_prompts(self):
        """复制英文提示词"""
        if self.english_prompts:
            text = ", ".join(self.english_prompts)
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            InfoBar.success(
                title="复制成功", content="英文提示词已复制到剪贴板",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=1500, parent=self
            )
        else:
            InfoBar.warning(
                title="提示", content="没有可复制的提示词",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=1500, parent=self
            )
            
    def set_prompts(self, english_prompts=None, chinese_prompts=None, translation_map=None):
        """设置提示词（用于加载历史数据）"""
        if english_prompts:
            self.english_prompts = english_prompts[:]
            # 更新输入框
            input_text = ", ".join(english_prompts)
            self.input_edit.setPlainText(input_text)
            
            # 如果提供了翻译映射，直接使用
            if translation_map:
                self.translation_map = translation_map.copy()
                print(f"[面板] 加载翻译映射: {len(self.translation_map)} 个")
            else:
                # 否则需要获取中文翻译
                print(f"[面板] 未提供翻译映射，将异步获取")
                self.update_translation_map_for_english_prompts()
            
        self.update_display()
    
    def update_translation_map_for_english_prompts(self):
        """为英文提示词更新翻译映射"""
        if not self.english_prompts:
            return
            
        # 启动翻译来获取中文映射，但不改变英文提示词
        input_text = ", ".join(self.english_prompts)
        
        # 创建专门的翻译线程来获取中文翻译
        if hasattr(self, 'mapping_worker') and self.mapping_worker and self.mapping_worker.isRunning():
            self.mapping_worker.quit()
            self.mapping_worker.wait()
        
        self.mapping_worker = TranslationWorker(input_text)
        self.mapping_worker.finished.connect(self.on_mapping_translation_finished)
        self.mapping_worker.error.connect(lambda error: print(f"获取翻译映射失败: {error}"))
        self.mapping_worker.start()
    
    def on_mapping_translation_finished(self, english_prompts, translation_map):
        """翻译映射获取完成（仅更新映射，不更新提示词）"""
        # 合并翻译映射，保留已有的映射关系
        if self.translation_map:
            # 保留现有映射，添加新的映射
            for english, chinese in translation_map.items():
                if english not in self.translation_map:  # 避免覆盖已有的映射
                    self.translation_map[english] = chinese
        else:
            self.translation_map = translation_map
        
        print(f"[面板] 翻译映射更新完成，总映射关系: {len(self.translation_map)} 个")
        
        # 只更新标签显示，不更新其他部分
        self.update_tags()
        
    def get_prompts(self):
        """获取当前提示词"""
        return {
            'english': self.english_prompts[:],
            'translation_map': self.translation_map.copy()  # 保存翻译映射
        } 