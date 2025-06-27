#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design Loading覆盖层组件
提供美观的加载界面效果
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from .fluent_styles import FluentColors, FluentSpacing


class LoadingOverlay(QWidget):
    """加载覆盖层组件 - 简洁美观设计"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadingOverlay")
        self.init_ui()
        self.setup_animation()
        self.hide()  # 初始隐藏
        
    def init_ui(self):
        """初始化UI - 简洁美观设计"""
        # 设置半透明白色背景，确保可见性
        self.setStyleSheet(f"""
            QWidget#LoadingOverlay {{
                background-color: rgba(255, 255, 255, 0.92);
                border: none;
            }}
        """)
        
        # 主布局 - 完全居中
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(FluentSpacing.LG)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 创建中心卡片容器
        card_container = QWidget()
        card_container.setFixedSize(360, 240)  # 固定合适的尺寸
        card_container.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-radius: 16px;
                border: 1px solid {FluentColors.get_color('border_primary')};
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        # 卡片内部布局
        card_layout = QVBoxLayout(card_container)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(FluentSpacing.LG)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        # 创建旋转loading图标
        loading_container = QWidget()
        loading_container.setFixedHeight(80)
        loading_layout = QVBoxLayout(loading_container)
        loading_layout.setAlignment(Qt.AlignCenter)
        loading_layout.setContentsMargins(0, 0, 0, 0)
        
        # 使用动态emoji图标作为loading效果
        self.loading_icon = QLabel("🔄")
        self.loading_icon.setAlignment(Qt.AlignCenter)
        self.loading_icon.setFixedSize(60, 60)
        self.loading_icon.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                background: transparent;
                border: none;
                color: {FluentColors.get_color('primary')};
            }}
        """)
        
        loading_layout.addWidget(self.loading_icon)
        
        # 主标题
        self.loading_label = QLabel("正在渲染布局")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setWordWrap(False)  # 禁止换行，确保单行显示
        self.loading_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_primary')};
                font-size: 18px;
                font-weight: 600;
                background: transparent;
                padding: 4px 8px;
                text-align: center;
            }}
        """)
        
        # 子标题
        self.subtitle_label = QLabel("请稍候，正在优化卡片布局...")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)  # 允许换行
        self.subtitle_label.setFixedHeight(40)  # 固定高度，最多两行
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_secondary')};
                font-size: 14px;
                font-weight: 400;
                background: transparent;
                padding: 4px 8px;
                text-align: center;
                line-height: 1.4;
            }}
        """)
        
        # 添加组件到卡片布局
        card_layout.addWidget(loading_container)
        card_layout.addWidget(self.loading_label)
        card_layout.addWidget(self.subtitle_label)
        
        # 添加卡片到主布局
        layout.addStretch(1)
        layout.addWidget(card_container)
        layout.addStretch(1)
        
        self.setLayout(layout)
        
    def setup_animation(self):
        """设置动画效果"""
        # 淡入淡出动画
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 使用QTimer创建loading图标切换动画
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_icon)
        self.loading_timer.setInterval(500)  # 每500ms切换一次
        
        # loading图标序列
        self.loading_icons = ["⏳", "⌛", "🔄", "⚡"]
        self.current_icon_index = 0
        
    def update_loading_icon(self):
        """更新loading图标"""
        self.current_icon_index = (self.current_icon_index + 1) % len(self.loading_icons)
        self.loading_icon.setText(self.loading_icons[self.current_icon_index])
        
    def show_loading(self, message="正在渲染布局", subtitle=""):
        """显示加载界面
        
        Args:
            message (str): 主要加载消息
            subtitle (str): 子标题消息，如果为空则自动匹配
        """
        # 确保文字不会被截断
        if len(message) > 20:
            message = message[:17] + "..."
        self.loading_label.setText(message)
        
        # 智能子标题匹配，确保长度合适
        if not subtitle:
            subtitle_map = {
                "布局": "正在优化卡片布局，提升浏览体验",
                "调整": "正在调整界面尺寸，请稍候",
                "加载": "正在从数据库获取图片信息",
                "记录": "正在加载图片记录数据",
                "筛选": "正在过滤符合条件的记录",
                "选项": "正在分析数据并更新筛选选项",
                "更新": "正在更新界面数据",
                "渲染": "正在渲染界面元素",
                "处理": "正在处理数据",
                "初始化": "正在初始化组件"
            }
            
            for key, sub in subtitle_map.items():
                if key in message:
                    subtitle = sub
                    break
            else:
                subtitle = "请稍候，操作进行中"
        
        # 确保子标题长度合适
        if len(subtitle) > 35:
            subtitle = subtitle[:32] + "..."
            
        self.subtitle_label.setText(subtitle)
        self.show()
        self.raise_()
        
        # 启动loading图标动画
        self.current_icon_index = 0
        self.loading_icon.setText(self.loading_icons[0])
        self.loading_timer.start()
        
        # 平滑淡入
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
    def hide_loading(self):
        """隐藏加载界面"""
        # 停止loading图标动画
        self.loading_timer.stop()
        
        # 淡出动画
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def set_loading_message(self, message, subtitle=""):
        """更新加载消息（不重新显示界面）
        
        Args:
            message (str): 新的主要消息
            subtitle (str): 新的子标题消息
        """
        if len(message) > 20:
            message = message[:17] + "..."
        self.loading_label.setText(message)
        
        if subtitle:
            if len(subtitle) > 35:
                subtitle = subtitle[:32] + "..."
            self.subtitle_label.setText(subtitle)
        
    def resizeEvent(self, event):
        """调整大小时保持覆盖整个父组件"""
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect()) 