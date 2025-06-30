#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 提示词基础组件
包含标签组件和手风琴组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSizePolicy, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from qfluentwidgets import CardWidget
from .fluent_styles import FluentColors


class PromptTag(QWidget):
    """一个统一的、可切换状态的提示词标签"""
    toggled = pyqtSignal(str, bool)  # 信号：(英文文本, 是否选中)
    deleted = pyqtSignal(str, str)

    def __init__(self, english_text: str, chinese_text: str = "", parent=None):
        super().__init__(parent)
        self.english_text = english_text
        self.chinese_text = chinese_text
        self.is_selected = True  # 默认是选中状态
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setAutoFillBackground(True)  # 强制父组件绘制背景，确保样式生效
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 英文部分
        self.english_label = QLabel(self.english_text)
        self.english_label.setWordWrap(True)
        self.english_label.setAlignment(Qt.AlignCenter)
        self.english_label.setObjectName("english_label") # 设置对象名以供样式表选择

        # 中文部分
        self.chinese_label = QLabel(self.chinese_text)
        self.chinese_label.setWordWrap(True)
        self.chinese_label.setAlignment(Qt.AlignCenter)
        self.chinese_label.setObjectName("chinese_label") # 设置对象名

        layout.addWidget(self.english_label)
        if self.chinese_text and self.chinese_text.strip() and self.chinese_text.strip() != self.english_text.strip():
            layout.addWidget(self.chinese_label)
        else:
            self.chinese_label.hide()
        
        self.setLayout(layout)
        self.setObjectName("prompt_tag") # 为父组件也设置对象名
        self._update_style()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def mousePressEvent(self, event):
        """处理点击事件"""
        if event.button() == Qt.LeftButton:
            self.toggle_selection()
        elif event.button() == Qt.RightButton:
            self.show_delete_menu(event.pos())
        super().mousePressEvent(event)
    
    def toggle_selection(self):
        """切换选中状态"""
        self.is_selected = not self.is_selected
        self._update_style()
        self.toggled.emit(self.english_text, self.is_selected)

    def show_delete_menu(self, pos):
        """显示右键删除菜单"""
        menu = QMenu(self)
        delete_action = menu.addAction("删除该标签")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == delete_action:
            self.deleted.emit(self.english_text, self.chinese_text)

    def _update_style(self):
        """根据状态更新样式，使用统一的样式表"""
        if self.is_selected:
            # 选中状态: 强制使用黑色背景，确保高对比度
            # 使用 'QWidget#prompt_tag' 和 'QLabel#...' 来提高选择器特异性，避免被全局样式覆盖
            self.setStyleSheet("""
                QWidget#prompt_tag {
                    background-color: black; /* 直接使用黑色背景 */
                    border: 1px solid #333;
                    border-radius: 6px;
                }
                QLabel#english_label {
                    color: white;
                    background-color: black; /* 透明，透出父级的黑色 */
                    padding: 6px 10px;
                    border-top-left-radius: 5px;
                    border-bottom-left-radius: 5px;
                }
                QLabel#chinese_label {
                    background-color: #009688; /* 青色 */
                    color: white;
                    padding: 6px 10px;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
            """)
        else:
            # 未选中状态: 浅色背景，深色文字，确保清晰
            self.setStyleSheet("""
                QWidget#prompt_tag {
                    background-color: #ECEFF1;
                    border: 1px solid #CFD8DC;
                    border-radius: 6px;
                }
                QLabel#english_label {
                    color: #37474F;
                    background-color:  #ECEFF1;
                    border-top-left-radius: 5px;
                    border-bottom-left-radius: 5px;image.png
                    padding: 6px 10px;
                }
                QLabel#chinese_label {
                    background-color: #B2DFDB;
                    color: #37474F;
                    padding: 6px 10px;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
            """)


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