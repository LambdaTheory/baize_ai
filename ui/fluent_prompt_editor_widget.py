#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 提示词修改组件
"""

import sys
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QScrollArea, QFrame, QPushButton, QLabel, QGridLayout, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSignal as Signal
from PyQt5.QtGui import QFont, QPalette

from qfluentwidgets import (CardWidget, FlowLayout, PushButton, StrongBodyLabel,
                           TextEdit, PlainTextEdit, MessageBox, PrimaryPushButton, InfoBar, InfoBarPosition,
                           LineEdit, ScrollArea)

from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing
from core.translator import BaiduTranslator
from core.data_manager import DataManager
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve


class TranslationThread(QThread):
    """翻译线程"""
    translation_finished = Signal(list)
    translation_error = Signal(str)
    
    def __init__(self, prompts, from_lang='en', to_lang='zh'):
        super().__init__()
        self.prompts = prompts
        self.from_lang = from_lang
        self.to_lang = to_lang
        
    def run(self):
        try:
            translator = BaiduTranslator()
            translated_prompts = translator.translate_prompts(self.prompts, self.from_lang, self.to_lang)
            self.translation_finished.emit(translated_prompts)
        except Exception as e:
            self.translation_error.emit(str(e))


class PromptTag(CardWidget):
    """提示词标签组件"""
    deleted = pyqtSignal(str, str)  # 删除信号，传递英文和中文
    
    def __init__(self, english_text, chinese_text=None, parent=None):
        super().__init__(parent)
        self.english_text = english_text
        self.chinese_text = chinese_text or ""
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # 显示文本
        if self.english_text and self.chinese_text:
            display_text = f"{self.english_text}({self.chinese_text})"
        elif self.english_text:
            display_text = self.english_text
        elif self.chinese_text:
            display_text = self.chinese_text
        else:
            display_text = "空标签"
            
        self.text_label = QLabel(display_text)
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_primary')};
                font-size: 14px;
                font-weight: 500;
                border: none;
                background: transparent;
            }}
        """)
        
        # 删除按钮
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 10px;
                background-color: {FluentColors.get_color('error')};
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(220, 38, 38, 0.8);
            }}
            QPushButton:pressed {{
                background-color: rgba(220, 38, 38, 0.9);
            }}
        """)
        self.delete_btn.clicked.connect(self.on_delete)
        
        layout.addWidget(self.text_label)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)
        
        # 设置标签样式
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 6px;
            }}
            CardWidget:hover {{
                border-color: {FluentColors.get_color('accent')};
                background-color: {FluentColors.get_color('bg_tertiary')};
            }}
        """)
        
    def on_delete(self):
        """删除标签"""
        self.deleted.emit(self.english_text, self.chinese_text)


class AccordionCard(CardWidget):
    """自定义手风琴卡片组件"""
    
    def __init__(self, title="标题", parent=None):
        super().__init__(parent)
        self._title = title
        self._expanded = False
        self._content_widget = None
        self._animation = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        self.header = QWidget()
        self.header.setFixedHeight(50)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 8, 16, 8)
        
        # 展开/折叠图标
        self.expand_icon = QPushButton("▶")
        self.expand_icon.setFixedSize(24, 24)
        self.expand_icon.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                color: {FluentColors.get_color('text_primary')};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border-radius: 4px;
            }}
        """)
        
        # 标题文本
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_primary')};
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        
        header_layout.addWidget(self.expand_icon)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.header.setLayout(header_layout)
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border-radius: 8px;
            }}
            QWidget:hover {{
                background-color: {FluentColors.get_color('bg_tertiary')};
            }}
        """)
        
        # 内容容器
        self.content_container = QWidget()
        self.content_container.setFixedHeight(0)
        self.content_container.setVisible(False)
        
        layout.addWidget(self.header)
        layout.addWidget(self.content_container)
        
        self.setLayout(layout)
        
        # 绑定点击事件
        self.header.mousePressEvent = self.toggle_expanded
        self.expand_icon.clicked.connect(self.toggle_expanded)
        
        # 设置卡片样式
        self.setBorderRadius(12)
        self.setStyleSheet(f"""
            AccordionCard {{
                background-color: {FluentColors.get_color('bg_primary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
            }}
        """)
        
    def setContent(self, widget):
        """设置内容组件"""
        if self._content_widget:
            self._content_widget.setParent(None)
            
        self._content_widget = widget
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(widget)
        self.content_container.setLayout(layout)
        
    def setTitle(self, title):
        """设置标题"""
        self._title = title
        self.title_label.setText(title)
        
    def title(self):
        """获取标题"""
        return self._title
        
    def setExpanded(self, expanded):
        """设置展开状态"""
        if expanded == self._expanded:
            return
            
        self._expanded = expanded
        
        if self._expanded:
            self.expand_icon.setText("▼")
            target_height = self._content_widget.sizeHint().height() + 16 if self._content_widget else 200
            self.content_container.setVisible(True)
        else:
            self.expand_icon.setText("▶")
            target_height = 0
            
        # 创建动画
        self._animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.setStartValue(self.content_container.height())
        self._animation.setEndValue(target_height)
        
        if not self._expanded:
            self._animation.finished.connect(lambda: self.content_container.setVisible(False))
            
        self._animation.start()
        
    def isExpanded(self):
        """获取展开状态"""
        return self._expanded
        
    def toggle_expanded(self, event=None):
        """切换展开状态"""
        self.setExpanded(not self._expanded)


class PromptEditorPanel(QWidget):
    """单个提示词编辑面板"""
    
    def __init__(self, title="提示词编辑", parent=None):
        super().__init__(parent)
        self.title = title
        self.english_prompts = []
        self.chinese_prompts = []
        self.prompt_tags = []
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.sync_prompts)
        self.translation_thread = None
        self.parent_widget = None  # 用于回调保存
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化UI"""
        # 主布局改为水平布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                FluentSpacing.MD, FluentSpacing.MD)
        main_layout.setSpacing(FluentSpacing.MD)
        
        # 左侧区域
        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(FluentSpacing.SM)
        
        # 输入框区域（左侧上方）
        input_frame = QFrame()
        input_layout = QVBoxLayout()
        input_layout.setSpacing(FluentSpacing.MD)
        
        # 英文输入框
        english_container = self.create_input_container(
            "英文提示词:", "📋", "请输入英文提示词，用逗号分隔...",
            "masterpiece, best quality, ultra detailed", 
            self.copy_english_prompts
        )
        self.english_edit = english_container['edit']
        self.english_copy_btn = english_container['copy_btn']
        
        # 中文输入框
        chinese_container = self.create_input_container(
            "中文提示词:", "📋", "请输入中文提示词，用逗号分隔...",
            "杰作, 最高质量, 超详细",
            self.copy_chinese_prompts
        )
        self.chinese_edit = chinese_container['edit']
        self.chinese_copy_btn = chinese_container['copy_btn']
        
        input_layout.addWidget(english_container['widget'])
        input_layout.addWidget(chinese_container['widget'])
        input_frame.setLayout(input_layout)
        
        # 功能按钮区域
        buttons_frame = self.create_buttons_frame()
        
        # 展示文本框（左侧下方）
        display_frame = self.create_display_area()
        
        # 组装左侧布局
        left_layout.addWidget(input_frame)
        left_layout.addWidget(buttons_frame)
        left_layout.addWidget(display_frame, 1)
        left_container.setLayout(left_layout)
        
        # 右侧区域 - 标签区域
        tags_area = self.create_tags_area()
        
        # 设置左右比例 (3:2)
        main_layout.addWidget(left_container, 3)
        main_layout.addWidget(tags_area, 2)
        
        self.setLayout(main_layout)
        
    def create_input_container(self, label_text, copy_icon, placeholder, sample_text, copy_callback):
        """创建输入框容器"""
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(8)
        
        # 标题和复制按钮
        header = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        copy_btn = QPushButton(copy_icon)
        copy_btn.setFixedSize(28, 28)
        copy_btn.setToolTip(f"复制{label_text.replace(':', '')}")
        copy_btn.setStyleSheet(f"""
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
        copy_btn.clicked.connect(copy_callback)
        
        header.addWidget(label)
        header.addStretch()
        header.addWidget(copy_btn)
        
        # 输入框
        edit = PlainTextEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(100)
        edit.setPlainText(sample_text)
        
        container_layout.addLayout(header)
        container_layout.addWidget(edit)
        container.setLayout(container_layout)
        
        return {
            'widget': container,
            'edit': edit,
            'copy_btn': copy_btn
        }
        
    def create_buttons_frame(self):
        """创建按钮框架"""
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(FluentSpacing.SM)
        
        # 清空按钮
        self.clear_btn = PushButton("清空")
        self.clear_btn.setFixedHeight(32)
        self.clear_btn.clicked.connect(self.clear_all_prompts)
        
        # 加载示例按钮
        self.example_btn = PrimaryPushButton("示例")
        self.example_btn.setFixedHeight(32)
        self.example_btn.clicked.connect(self.load_example_prompts)
        
        # 英译中按钮
        self.translate_en_to_zh_btn = PushButton("英→中")
        self.translate_en_to_zh_btn.setFixedHeight(32)
        self.translate_en_to_zh_btn.clicked.connect(self.translate_english_to_chinese)
        self.translate_en_to_zh_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('info')};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
            }}
            PushButton:hover {{
                background-color: rgba(59, 130, 246, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(59, 130, 246, 0.9);
            }}
        """)
        
        # 中译英按钮
        self.translate_zh_to_en_btn = PushButton("中→英")
        self.translate_zh_to_en_btn.setFixedHeight(32)
        self.translate_zh_to_en_btn.clicked.connect(self.translate_chinese_to_english)
        self.translate_zh_to_en_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('success')};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
            }}
            PushButton:hover {{
                background-color: rgba(34, 197, 94, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(34, 197, 94, 0.9);
            }}
        """)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.example_btn)
        buttons_layout.addWidget(self.translate_en_to_zh_btn)
        buttons_layout.addWidget(self.translate_zh_to_en_btn)
        buttons_layout.addStretch()
        
        buttons_frame.setLayout(buttons_layout)
        return buttons_frame
        
    def create_display_area(self):
        """创建展示区域"""
        display_container = QWidget()
        display_layout = QVBoxLayout()
        display_layout.setSpacing(8)
        
        # 展示区域标题
        display_title = QLabel("提示词预览:")
        display_title.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        # 只读的展示文本框
        self.display_text = PlainTextEdit()
        self.display_text.setReadOnly(True)
        self.display_text.setPlaceholderText("这里将显示格式化后的提示词...")
        self.display_text.setStyleSheet(f"""
            PlainTextEdit {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 6px;
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_secondary')};
                padding: 8px;
            }}
        """)
        
        display_layout.addWidget(display_title)
        display_layout.addWidget(self.display_text, 1)
        display_container.setLayout(display_layout)
        
        return display_container
        
    def create_tags_area(self):
        """创建标签区域"""
        tags_container = QWidget()
        tags_layout = QVBoxLayout()
        tags_layout.setSpacing(8)
        
        # 标签标题
        tags_title = QLabel("提示词标签:")
        tags_title.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        # 滚动区域用于显示标签
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(120)  # 设置最小高度
        scroll_area.setMaximumHeight(200)  # 设置最大高度，确保有滚动条
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
        self.tags_layout.setHorizontalSpacing(8)
        self.tags_layout.setVerticalSpacing(8)
        
        scroll_area.setWidget(self.tags_widget)
        
        tags_layout.addWidget(tags_title)
        tags_layout.addWidget(scroll_area, 1)
        tags_container.setLayout(tags_layout)
        
        return tags_container
        
    def setup_connections(self):
        """设置信号连接"""
        self.english_edit.textChanged.connect(self.on_english_text_changed)
        self.chinese_edit.textChanged.connect(self.on_chinese_text_changed)
        
    def on_english_text_changed(self):
        """英文文本改变时的处理"""
        self.update_timer.stop()
        self.update_timer.start(500)
        
    def on_chinese_text_changed(self):
        """中文文本改变时的处理"""
        self.update_timer.stop()
        self.update_timer.start(500)
        
    def sync_prompts(self):
        """同步英文和中文提示词"""
        try:
            english_text = self.english_edit.toPlainText().strip()
            chinese_text = self.chinese_edit.toPlainText().strip()
            
            english_prompts = self.parse_prompts(english_text)
            chinese_prompts = self.parse_prompts(chinese_text)
            
            self.english_prompts = english_prompts
            self.chinese_prompts = chinese_prompts
            
            self.update_tags_display()
            
            # 触发自动保存
            if self.parent_widget and hasattr(self.parent_widget, 'save_history_data'):
                self.parent_widget.save_history_data()
            
        except Exception as e:
            print(f"同步提示词时出错: {e}")
            
    def parse_prompts(self, text):
        """解析提示词文本，按逗号分割"""
        if not text:
            return []
        prompts = [prompt.strip() for prompt in text.split(',') if prompt.strip()]
        return prompts
        
    def update_tags_display(self):
        """更新标签显示"""
        for tag in self.prompt_tags:
            self.tags_layout.removeWidget(tag)
            tag.setParent(None)
            tag.deleteLater()
        self.prompt_tags.clear()
        
        max_count = max(len(self.english_prompts), len(self.chinese_prompts)) if self.english_prompts or self.chinese_prompts else 0
        
        for i in range(max_count):
            english = self.english_prompts[i] if i < len(self.english_prompts) else ""
            chinese = self.chinese_prompts[i] if i < len(self.chinese_prompts) else ""
            
            if english or chinese:
                tag = PromptTag(english, chinese)
                tag.deleted.connect(self.on_tag_deleted)
                self.tags_layout.addWidget(tag)
                self.prompt_tags.append(tag)
        
        # 更新展示文本框内容
        self.update_display_text()
                
    def update_display_text(self):
        """更新展示文本框内容"""
        if hasattr(self, 'display_text'):
            display_lines = []
            
            if self.english_prompts:
                display_lines.append("English Prompts:")
                display_lines.append(", ".join(self.english_prompts))
                display_lines.append("")
            
            if self.chinese_prompts:
                display_lines.append("Chinese Prompts:")
                display_lines.append(", ".join(self.chinese_prompts))
                display_lines.append("")
            
            if self.english_prompts and self.chinese_prompts:
                display_lines.append("Paired Prompts:")
                max_count = max(len(self.english_prompts), len(self.chinese_prompts))
                for i in range(max_count):
                    english = self.english_prompts[i] if i < len(self.english_prompts) else ""
                    chinese = self.chinese_prompts[i] if i < len(self.chinese_prompts) else ""
                    if english and chinese:
                        display_lines.append(f"{i+1}. {english} → {chinese}")
                    elif english:
                        display_lines.append(f"{i+1}. {english} → [无对应中文]")
                    elif chinese:
                        display_lines.append(f"{i+1}. [无对应英文] → {chinese}")
            
            display_text = "\n".join(display_lines) if display_lines else "暂无提示词内容"
            self.display_text.setPlainText(display_text)
        
    def on_tag_deleted(self, english_text, chinese_text):
        """处理标签删除"""
        try:
            if english_text in self.english_prompts:
                index = self.english_prompts.index(english_text)
                self.english_prompts.pop(index)
                
                if index < len(self.chinese_prompts):
                    self.chinese_prompts.pop(index)
                    
            elif chinese_text in self.chinese_prompts:
                index = self.chinese_prompts.index(chinese_text)
                self.chinese_prompts.pop(index)
                
                if index < len(self.english_prompts):
                    self.english_prompts.pop(index)
            
            self.update_input_texts()
            self.update_tags_display()
            
        except Exception as e:
            print(f"删除标签时出错: {e}")
            
    def update_input_texts(self):
        """更新输入框文本"""
        self.english_edit.textChanged.disconnect()
        self.chinese_edit.textChanged.disconnect()
        
        try:
            english_text = ", ".join(self.english_prompts)
            self.english_edit.setPlainText(english_text)
            
            chinese_text = ", ".join(self.chinese_prompts)
            self.chinese_edit.setPlainText(chinese_text)
            
        finally:
            self.english_edit.textChanged.connect(self.on_english_text_changed)
            self.chinese_edit.textChanged.connect(self.on_chinese_text_changed)
            
    def set_prompts(self, english_prompts=None, chinese_prompts=None):
        """设置提示词内容"""
        if english_prompts is not None:
            self.english_prompts = english_prompts[:]
            
        if chinese_prompts is not None:
            self.chinese_prompts = chinese_prompts[:]
            
        self.update_input_texts()
        self.update_tags_display()
        
    def get_prompts(self):
        """获取当前提示词"""
        return {
            'english': self.english_prompts[:],
            'chinese': self.chinese_prompts[:]
        }
        
    def clear_all_prompts(self):
        """清空所有提示词"""
        self.english_prompts.clear()
        self.chinese_prompts.clear()
        self.update_input_texts()
        self.update_tags_display()
        
    def load_example_prompts(self):
        """加载示例提示词"""
        example_english = [
            "masterpiece", "best quality", "ultra detailed",
            "beautiful", "elegant", "soft lighting"
        ]
        
        example_chinese = [
            "杰作", "最高质量", "超详细",
            "美丽", "优雅", "柔和光线"
        ]
        
        self.set_prompts(example_english, example_chinese)
        
    def copy_english_prompts(self):
        """复制英文提示词到剪贴板"""
        text = self.english_edit.toPlainText().strip()
        if not text:
            InfoBar.warning(
                title="提示", content="英文输入框为空",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=1500, parent=self
            )
            return
            
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        InfoBar.success(
            title="复制成功", content="英文提示词已复制到剪贴板",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=1500, parent=self
        )
        
    def copy_chinese_prompts(self):
        """复制中文提示词到剪贴板"""
        text = self.chinese_edit.toPlainText().strip()
        if not text:
            InfoBar.warning(
                title="提示", content="中文输入框为空",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=1500, parent=self
            )
            return
            
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        InfoBar.success(
            title="复制成功", content="中文提示词已复制到剪贴板",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=1500, parent=self
        )
        
    def translate_english_to_chinese(self):
        """翻译英文提示词为中文"""
        if not self.english_prompts:
            InfoBar.warning(
                title="提示", content="请先输入英文提示词",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self
            )
            return
            
        self.translate_en_to_zh_btn.setText("翻译中...")
        self.translate_en_to_zh_btn.setEnabled(False)
        self.translate_zh_to_en_btn.setEnabled(False)
        
        InfoBar.info(
            title="翻译中", content="正在翻译提示词，请稍候...",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=3000, parent=self
        )
        
        if self.translation_thread:
            self.translation_thread.quit()
            self.translation_thread.wait()
            
        self.translation_thread = TranslationThread(self.english_prompts, 'en', 'zh')
        self.translation_thread.translation_finished.connect(self.on_en_to_zh_translation_finished)
        self.translation_thread.translation_error.connect(self.on_en_to_zh_translation_error)
        self.translation_thread.start()
        
    def translate_chinese_to_english(self):
        """翻译中文提示词为英文"""
        if not self.chinese_prompts:
            InfoBar.warning(
                title="提示", content="请先输入中文提示词",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self
            )
            return
            
        self.translate_zh_to_en_btn.setText("翻译中...")
        self.translate_zh_to_en_btn.setEnabled(False)
        self.translate_en_to_zh_btn.setEnabled(False)
        
        InfoBar.info(
            title="翻译中", content="正在翻译提示词，请稍候...",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=3000, parent=self
        )
        
        if self.translation_thread:
            self.translation_thread.quit()
            self.translation_thread.wait()
            
        self.translation_thread = TranslationThread(self.chinese_prompts, 'zh', 'en')
        self.translation_thread.translation_finished.connect(self.on_zh_to_en_translation_finished)
        self.translation_thread.translation_error.connect(self.on_zh_to_en_translation_error)
        self.translation_thread.start()
        
    def on_en_to_zh_translation_finished(self, translated_prompts):
        """英译中完成处理"""
        self.chinese_prompts = translated_prompts
        self.update_input_texts()
        self.update_tags_display()
        
        self.translate_en_to_zh_btn.setText("英→中")
        self.translate_en_to_zh_btn.setEnabled(True)
        self.translate_zh_to_en_btn.setEnabled(True)
        
        InfoBar.success(
            title="英译中完成", content=f"成功翻译了 {len(translated_prompts)} 个提示词",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=2000, parent=self
        )
        
    def on_en_to_zh_translation_error(self, error_message):
        """英译中错误处理"""
        self.translate_en_to_zh_btn.setText("英→中")
        self.translate_en_to_zh_btn.setEnabled(True)
        self.translate_zh_to_en_btn.setEnabled(True)
        
        InfoBar.error(
            title="英译中失败", content=f"翻译出现错误: {error_message}",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=3000, parent=self
        )
        
    def on_zh_to_en_translation_finished(self, translated_prompts):
        """中译英完成处理"""
        self.english_prompts = translated_prompts
        self.update_input_texts()
        self.update_tags_display()
        
        self.translate_zh_to_en_btn.setText("中→英")
        self.translate_zh_to_en_btn.setEnabled(True)
        self.translate_en_to_zh_btn.setEnabled(True)
        
        InfoBar.success(
            title="中译英完成", content=f"成功翻译了 {len(translated_prompts)} 个提示词",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=2000, parent=self
        )
        
    def on_zh_to_en_translation_error(self, error_message):
        """中译英错误处理"""
        self.translate_zh_to_en_btn.setText("中→英")
        self.translate_zh_to_en_btn.setEnabled(True)
        self.translate_en_to_zh_btn.setEnabled(True)
        
        InfoBar.error(
            title="中译英失败", content=f"翻译出现错误: {error_message}",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=3000, parent=self
        )


class FluentPromptEditorWidget(ScrollArea):
    """Fluent Design 提示词修改组件 - 手风琴样式"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editors = []  # 存储所有编辑器面板
        self.editor_count = 0
        self.data_manager = DataManager()  # 数据管理器
        self.auto_save_enabled = True  # 自动保存开关
        self.last_backup_data = None  # 上次备份的数据，用于检测变化
        self.backup_count = 0  # 备份计数器
        
        # 自动备份定时器
        self.auto_backup_timer = QTimer()
        self.auto_backup_timer.timeout.connect(self.auto_backup)
        self.auto_backup_timer.start(10000)  # 每10秒备份一次
        
        self.init_ui()
        self.load_history_data()  # 加载历史数据
        
    def init_ui(self):
        """初始化UI"""
        # 设置滚动区域属性
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.MD)
        
        # 标题和新增按钮
        header_layout = QHBoxLayout()
        
        title_label = StrongBodyLabel("提示词管理器")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        self.add_editor_btn = PrimaryPushButton("+ 新增场景")
        self.add_editor_btn.clicked.connect(self.show_add_editor_dialog)
        self.add_editor_btn.setFixedHeight(36)
        
        # 保存按钮
        self.save_btn = PushButton("💾 保存")
        self.save_btn.clicked.connect(self.manual_save)
        self.save_btn.setFixedHeight(36)
        self.save_btn.setToolTip("手动保存当前提示词数据")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.save_btn)
        header_layout.addWidget(self.add_editor_btn)
        
        main_layout.addLayout(header_layout)
        
        # 手风琴容器
        self.accordion_layout = QVBoxLayout()
        self.accordion_layout.setSpacing(FluentSpacing.SM)
        main_layout.addLayout(self.accordion_layout)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)
        
    def add_editor(self, title="提示词编辑"):
        """添加新的编辑器面板"""
        self.editor_count += 1
        
        # 创建手风琴卡片
        accordion = AccordionCard(title)
        
        # 创建编辑器面板
        editor_panel = PromptEditorPanel(title)
        editor_panel.parent_widget = self  # 设置父组件引用
        
        # 创建内容容器
        content_container = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        
        # 创建头部控制按钮
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 重命名按钮
        rename_btn = QPushButton("🏷️")
        rename_btn.setFixedSize(24, 24)
        rename_btn.setToolTip("重命名场景")
        rename_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 4px;
                background-color: {FluentColors.get_color('bg_secondary')};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {FluentColors.get_color('bg_tertiary')};
            }}
        """)
        rename_btn.clicked.connect(lambda: self.rename_editor(accordion, editor_panel))
        
        # 删除按钮
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setToolTip("删除场景")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 4px;
                background-color: {FluentColors.get_color('bg_secondary')};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {FluentColors.get_color('error')};
                color: white;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_editor(accordion, editor_panel))
        
        header_layout.addStretch()
        header_layout.addWidget(rename_btn)
        header_layout.addWidget(delete_btn)
        header_widget.setLayout(header_layout)
        
        # 组装内容
        content_layout.addWidget(header_widget)
        content_layout.addWidget(editor_panel)
        content_container.setLayout(content_layout)
        
        # 设置手风琴内容
        accordion.setContent(content_container)
        
        # 添加到手风琴布局
        self.accordion_layout.addWidget(accordion)
        
        # 存储编辑器信息
        editor_info = {
            'accordion': accordion,
            'panel': editor_panel,
            'title': title
        }
        self.editors.append(editor_info)
        
        # 默认展开第一个编辑器
        if len(self.editors) == 1:
            accordion.setExpanded(True)
            
        return editor_panel
        
    def show_add_editor_dialog(self):
        """显示添加编辑器对话框"""
        from qfluentwidgets import MessageBox
        from PyQt5.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(
            self, 
            "新增场景", 
            "请输入新场景的名称:",
            text="场景名称"
        )
        
        if ok:
            title = text.strip()
            if title:
                self.add_editor(title)
            else:
                self.add_editor(f"场景 {len(self.editors) + 1}")
            
            # 自动保存
            self.save_history_data()
                
    def rename_editor(self, accordion, editor_panel):
        """重命名编辑器"""
        from PyQt5.QtWidgets import QInputDialog
        
        current_title = accordion.title()
        text, ok = QInputDialog.getText(
            self, 
            "重命名场景", 
            "请输入新的场景名称:",
            text=current_title
        )
        
        if ok:
            new_title = text.strip()
            if new_title:
                accordion.setTitle(new_title)
                editor_panel.title = new_title
                
                # 更新存储的编辑器信息
                for editor_info in self.editors:
                    if editor_info['accordion'] == accordion:
                        editor_info['title'] = new_title
                        break
                
                # 自动保存
                self.save_history_data()
                        
    def delete_editor(self, accordion, editor_panel):
        """删除编辑器"""
        if len(self.editors) <= 1:
            InfoBar.warning(
                title="提示", content="至少需要保留一个编辑器",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self
            )
            return
            
        # 确认删除对话框
        from PyQt5.QtWidgets import QMessageBox
        result = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除场景 \"{accordion.title()}\" 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # 从布局中移除
            self.accordion_layout.removeWidget(accordion)
            accordion.setParent(None)
            accordion.deleteLater()
            
            # 从列表中移除
            self.editors = [editor for editor in self.editors 
                          if editor['accordion'] != accordion]
            
            InfoBar.success(
                title="删除成功", content="场景已删除",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=1500, parent=self
            )
            
            # 自动保存
            self.save_history_data()
            
    def get_all_prompts(self):
        """获取所有编辑器的提示词"""
        all_prompts = {}
        for editor_info in self.editors:
            title = editor_info['title']
            prompts = editor_info['panel'].get_prompts()
            all_prompts[title] = prompts
        return all_prompts
        
    def set_all_prompts(self, prompts_dict):
        """设置所有编辑器的提示词"""
        # 清空现有编辑器
        for editor_info in self.editors[:]:
            accordion = editor_info['accordion']
            self.accordion_layout.removeWidget(accordion)
            accordion.setParent(None)
            accordion.deleteLater()
        self.editors.clear()
        
        # 重新创建编辑器
        for title, prompts in prompts_dict.items():
            editor_panel = self.add_editor(title)
            editor_panel.set_prompts(
                english_prompts=prompts.get('english', []),
                chinese_prompts=prompts.get('chinese', [])
            )
    
    def load_history_data(self):
        """加载历史数据"""
        try:
            data = self.data_manager.load_prompt_data()
            
            if data and 'scenes' in data and len(data['scenes']) > 0:
                # 加载历史数据
                InfoBar.info(
                    title="加载历史数据", 
                    content=f"成功加载 {len(data['scenes'])} 个场景",
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=2000, parent=self
                )
                
                for scene in data['scenes']:
                    title = scene.get('title', '未命名场景')
                    english_prompts = scene.get('english_prompts', [])
                    chinese_prompts = scene.get('chinese_prompts', [])
                    
                    editor_panel = self.add_editor(title)
                    editor_panel.set_prompts(english_prompts, chinese_prompts)
            else:
                # 没有历史数据，创建默认编辑器
                default_data = self.data_manager.get_default_prompt_data()
                for scene in default_data['scenes']:
                    title = scene.get('title', '通用提示词')
                    english_prompts = scene.get('english_prompts', [])
                    chinese_prompts = scene.get('chinese_prompts', [])
                    
                    editor_panel = self.add_editor(title)
                    editor_panel.set_prompts(english_prompts, chinese_prompts)
                    
        except Exception as e:
            print(f"加载历史数据失败: {e}")
            # 出错时创建默认编辑器
            self.add_editor("通用提示词")
    
    def save_history_data(self):
        """保存历史数据"""
        if not self.auto_save_enabled:
            return
            
        try:
            scenes_data = []
            for editor_info in self.editors:
                title = editor_info['title']
                prompts = editor_info['panel'].get_prompts()
                
                scene_data = {
                    'title': title,
                    'english_prompts': prompts.get('english', []),
                    'chinese_prompts': prompts.get('chinese', [])
                }
                scenes_data.append(scene_data)
            
            prompt_data = {
                'scenes': scenes_data
            }
            
            success = self.data_manager.save_prompt_data(prompt_data)
            if success:
                print(f"自动保存成功，共保存 {len(scenes_data)} 个场景")
            else:
                print("自动保存失败")
                
        except Exception as e:
            print(f"保存历史数据失败: {e}")
    
    def manual_save(self):
        """手动保存"""
        self.save_history_data()
        InfoBar.success(
            title="保存成功", 
            content="提示词数据已保存",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=2000, parent=self
        )
    
    def auto_backup(self):
        """自动备份"""
        try:
            # 获取当前数据
            current_data = self.get_current_backup_data()
            
            # 检查数据是否有变化
            if current_data != self.last_backup_data:
                # 数据有变化，执行备份
                self.save_history_data()
                self.last_backup_data = current_data
                self.backup_count += 1
                
                # 每5次备份显示一次提示（即每50秒提示一次）
                if self.backup_count % 5 == 0:
                    InfoBar.info(
                        title="自动备份", 
                        content=f"已自动备份 (第{self.backup_count}次)",
                        orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1500, parent=self
                    )
                else:
                    # 不显示提示，但在控制台记录
                    print(f"自动备份完成 (第{self.backup_count}次)")
            
        except Exception as e:
            print(f"自动备份失败: {e}")
    
    def get_current_backup_data(self):
        """获取当前用于备份比较的数据"""
        try:
            scenes_data = []
            for editor_info in self.editors:
                title = editor_info['title']
                prompts = editor_info['panel'].get_prompts()
                
                scene_data = {
                    'title': title,
                    'english_prompts': prompts.get('english', []),
                    'chinese_prompts': prompts.get('chinese', [])
                }
                scenes_data.append(scene_data)
            
            return str(scenes_data)  # 转为字符串便于比较
        except:
            return None 