#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
界面创建组件
"""

from PyQt5.QtCore import QObject
from qfluentwidgets import NavigationItemPosition
from .fluent_styles import FluentIcons


class FluentInterfaceCreator(QObject):
    """界面创建组件"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def create_extraction_interface(self):
        """创建信息提取界面"""
        from .fluent_extraction_layout import FluentExtractionLayout
        from .fluent_drag_components import DragOverlay
        
        # 创建布局管理器
        self.parent.extraction_layout = FluentExtractionLayout(self.parent)
        
        # 创建界面 - FluentExtractionLayout会自动将组件设置到parent上
        self.parent.extraction_interface = self.parent.extraction_layout.create_extraction_interface()
        
        # 创建拖拽蒙层
        self.parent.drag_overlay = DragOverlay(self.parent.extraction_interface)
        
        # 重写拖拽事件
        self.parent.extraction_interface.dragEnterEvent = self.parent.event_handlers.handle_drag_enter_event
        self.parent.extraction_interface.dragLeaveEvent = self.parent.event_handlers.handle_drag_leave_event
        self.parent.extraction_interface.dropEvent = self.parent.event_handlers.handle_drop_event
        
        # 加载历史记录（如果历史组件存在）
        if hasattr(self.parent, 'history_widget') and self.parent.history_widget:
            self.parent.history_widget.load_history()
    
    def create_gallery_interface(self):
        """创建图片画廊界面"""
        from .fluent_gallery_components import FluentGalleryWidget
        
        self.parent.gallery_interface = FluentGalleryWidget(self.parent.data_manager, self.parent)
        self.parent.gallery_interface.setObjectName("gallery")
        
        # 连接信号
        self.parent.gallery_interface.record_selected.connect(
            self.parent.event_handlers.handle_gallery_record_selected
        )
    
    def create_prompt_editor_interface(self):
        """创建提示词编辑界面"""
        from .fluent_prompt_editor_widget import FluentPromptEditorWidget
        
        self.parent.prompt_editor_interface = FluentPromptEditorWidget(self.parent)
        self.parent.prompt_editor_interface.setObjectName("prompt_editor")
    
    def create_prompt_reverser_interface(self):
        """创建提示词反推界面"""
        from .fluent_prompt_reverser_widget import FluentPromptReverserWidget
        
        self.parent.prompt_reverser_interface = FluentPromptReverserWidget(self.parent)
        self.parent.prompt_reverser_interface.setObjectName("prompt_reverser")
    
    def create_settings_interface(self):
        """创建设置界面"""
        from .fluent_settings_widget import FluentSettingsWidget
        
        self.parent.settings_interface = FluentSettingsWidget(self.parent)
        self.parent.settings_interface.setObjectName("settings")
    
    def create_activation_interface(self):
        """创建激活界面"""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout
        from qfluentwidgets import (CardWidget, TitleLabel, BodyLabel, 
                                   PrimaryPushButton, FlowLayout)
        
        # 创建激活界面
        self.parent.activation_interface = QWidget()
        layout = QVBoxLayout(self.parent.activation_interface)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 标题
        title = TitleLabel("软件激活")
        layout.addWidget(title)
        
        # 激活卡片
        activation_card = CardWidget()
        activation_layout = QVBoxLayout(activation_card)
        activation_layout.setContentsMargins(30, 30, 30, 30)
        activation_layout.setSpacing(15)
        
        # 激活说明
        desc_label = BodyLabel("请激活软件以解锁全部功能")
        desc_label.setWordWrap(True)
        activation_layout.addWidget(desc_label)
        
        # 功能对比
        features_layout = FlowLayout()
        
        # 试用期功能
        trial_card = CardWidget()
        trial_layout = QVBoxLayout(trial_card)
        trial_layout.setContentsMargins(20, 20, 20, 20)
        
        trial_title = BodyLabel("试用版功能")
        trial_title.setStyleSheet("font-weight: bold; color: #e67e22;")
        trial_layout.addWidget(trial_title)
        
        trial_features = {
            "✓ 基础图片信息提取": "自动读取并展示PNG图片内包含的基础创作信息。",
            "✓ 提示词查看和编辑": "查看和修改图片的正面及负面提示词。",
            "✓ 历史记录查看": "浏览和管理最近处理过的图片记录。",
            "✓ 单个文件导出": "将当前图片的信息以多种格式（如HTML、Excel）导出。",
            "✗ 批量处理功能": "【付费解锁】一次性处理整个文件夹的图片，自动提取并保存信息。",
            "✗ AI智能标签": "【付费解锁】使用先进的AI模型分析图片内容，自动生成描述性标签。",
            "✗ 高级导出功能": "【付费解锁】批量导出数据到Excel或生成可分享的HTML画廊页面。"
        }
        
        for feature, tooltip in trial_features.items():
            feature_label = BodyLabel(feature)
            feature_label.setToolTip(tooltip)
            if feature.startswith("✗"):
                feature_label.setStyleSheet("color: #95a5a6;")
            trial_layout.addWidget(feature_label)
        
        features_layout.addWidget(trial_card)
        
        # 完整版功能
        full_card = CardWidget()
        full_layout = QVBoxLayout(full_card)
        full_layout.setContentsMargins(20, 20, 20, 20)
        
        full_title = BodyLabel("完整版功能")
        full_title.setStyleSheet("font-weight: bold; color: #27ae60;")
        full_layout.addWidget(full_title)
        
        full_features = {
            "✓ 全部基础功能": "包含所有试用版功能，且无任何使用限制。",
            "✓ 批量处理功能": "支持一次性处理整个文件夹的图片，极大提升效率。",
            "✓ AI智能标签": "借助AI自动为图片生成精准的描述标签，免去手动输入的麻烦。",
            "✓ 高级导出功能": "轻松将大量图片数据整理成Excel表格或一键生成精美的HTML分享页面。",
            "✓ ComfyUI集成": "与ComfyUI无缝集成，支持直接将图片信息和工作流发送至ComfyUI。",
            "✓ 云端同步": "【规划中】未来将支持在多设备间同步您的数据和设置。",
            "✓ 优先技术支持": "享受专属客服通道，您的问题将得到优先处理。"
        }
        
        for feature, tooltip in full_features.items():
            feature_label = BodyLabel(feature)
            feature_label.setToolTip(tooltip)
            feature_label.setStyleSheet("color: #27ae60;")
            full_layout.addWidget(feature_label)
        
        features_layout.addWidget(full_card)
        activation_layout.addLayout(features_layout)
        
        # 激活按钮
        self.parent.activate_btn = PrimaryPushButton("立即激活")
        self.parent.activate_btn.clicked.connect(self.parent.license_component.show_activation_dialog)
        activation_layout.addWidget(self.parent.activate_btn)
        
        layout.addWidget(activation_card)
        layout.addStretch()
        
        # 设置对象名称
        self.parent.activation_interface.setObjectName("activation")
    
    def setup_navigation(self):
        """设置导航界面"""
        # 信息提取页面
        self.parent.addSubInterface(
            interface=self.parent.extraction_interface,
            icon=FluentIcons.get_icon('extract'),
            text='信息提取',
            position=NavigationItemPosition.TOP
        )
        
        # 图片画廊页面
        self.parent.addSubInterface(
            interface=self.parent.gallery_interface,
            icon=FluentIcons.get_icon('gallery'),
            text='图片画廊',
            position=NavigationItemPosition.TOP
        )
        
        # 提示词修改页面
        self.parent.addSubInterface(
            interface=self.parent.prompt_editor_interface,
            icon=FluentIcons.get_icon('edit'),
            text='提示词修改',
            position=NavigationItemPosition.TOP
        )
        
        # 提示词反推页面
        self.parent.addSubInterface(
            interface=self.parent.prompt_reverser_interface,
            icon=FluentIcons.get_icon('magic'),
            text='提示词反推',
            position=NavigationItemPosition.TOP
        )
        
        # 设置页面
        self.parent.addSubInterface(
            interface=self.parent.settings_interface,
            icon=FluentIcons.get_icon('settings'),
            text='设置',
            position=NavigationItemPosition.BOTTOM
        )
        
        # 激活页面（始终显示，方便用户激活）
        self.parent.addSubInterface(
            interface=self.parent.activation_interface,
            icon=FluentIcons.get_icon('key'),
            text='软件激活',
            position=NavigationItemPosition.BOTTOM
        ) 