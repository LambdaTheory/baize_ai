#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 提示词基础组件
包含标签组件和手风琴组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from qfluentwidgets import CardWidget
from .fluent_styles import FluentColors


class PromptTag(CardWidget):
    """提示词标签组件 - 始终显示"英文(中文)"格式"""
    deleted = pyqtSignal(str, str)  # 删除信号，传递英文和中文
    
    def __init__(self, english_text, chinese_text="", parent=None):
        super().__init__(parent)
        self.english_text = english_text
        self.chinese_text = chinese_text
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # 显示文本 - 固定格式：英文(中文)
        if self.chinese_text and self.chinese_text.strip() and self.chinese_text.strip() != self.english_text.strip():
            display_text = f"{self.english_text}({self.chinese_text})"
        else:
            display_text = self.english_text
            
        self.text_label = QLabel(display_text)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_primary')};
                font-size: 13px;
                font-weight: 500;
                border: none;
                background: transparent;
                padding: 0px;
            }}
        """)
        
        # 删除按钮
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(18, 18)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 9px;
                background-color: {FluentColors.get_color('error')};
                color: white;
                font-size: 11px;
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
        
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.delete_btn, 0)
        
        self.setLayout(layout)
        
        # 设置标签样式
        self.setMinimumHeight(32)
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 16px;
                min-height: 32px;
                max-width: 400px;
                font-size: 13px;
                font-weight: 500;
            }}
            CardWidget:hover {{
                border-color: {FluentColors.get_color('accent')};
                background-color: {FluentColors.get_color('bg_tertiary')};
            }}
        """)
        
    def on_delete(self):
        """删除标签"""
        self.deleted.emit(self.english_text, self.chinese_text)
        
    def update_text(self, english_text, chinese_text=""):
        """更新标签文本"""
        self.english_text = english_text
        self.chinese_text = chinese_text
        
        if chinese_text and chinese_text.strip() and chinese_text.strip() != english_text.strip():
            display_text = f"{english_text}({chinese_text})"
        else:
            display_text = english_text
            
        self.text_label.setText(display_text)


class AccordionCard(CardWidget):
    """手风琴卡片组件"""
    
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