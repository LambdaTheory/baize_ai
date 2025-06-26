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
        
        # 创建布局管理器
        self.parent.extraction_layout = FluentExtractionLayout(self.parent)
        
        # 创建界面
        self.parent.extraction_interface = self.parent.extraction_layout.create_extraction_interface()
        
        # 获取各个组件的引用
        components = self.parent.extraction_layout.get_components()
        
        # 设置组件引用到主窗口
        self.parent.image_label = components['image_label']
        self.parent.file_name_edit = components['file_name_edit']
        self.parent.file_path_label = components['file_path_label']
        self.parent.file_size_label = components['file_size_label']
        self.parent.image_size_label = components['image_size_label']
        self.parent.positive_prompt_text = components['positive_prompt_text']
        self.parent.negative_prompt_text = components['negative_prompt_text']
        self.parent.generation_method_text = components['generation_method_text']
        self.parent.params_layout = components['params_layout']
        self.parent.user_tags_edit = components['user_tags_edit']
        self.parent.user_notes_edit = components['user_notes_edit']
        self.parent.history_widget = components['history_widget']
        self.parent.image_info_widget = components['image_info_widget']
        self.parent.license_status_bar = components['license_status_bar']
        
        # 获取按钮引用
        self.parent.positive_translate_btn = components['positive_translate_btn']
        self.parent.negative_translate_btn = components['negative_translate_btn']
        self.parent.save_prompts_btn = components['save_prompts_btn']
        self.parent.reset_prompts_btn = components['reset_prompts_btn']
        
        # 加载历史记录
        self.parent.history_widget.load_history()
    
    def create_gallery_interface(self):
        """创建图片画廊界面"""
        from .fluent_gallery_components import FluentGalleryWidget
        
        self.parent.gallery_interface = FluentGalleryWidget(self.parent)
        
        # 连接信号
        self.parent.gallery_interface.record_selected.connect(
            self.parent.event_handlers.handle_gallery_record_selected
        )
    
    def create_prompt_editor_interface(self):
        """创建提示词编辑界面"""
        from .fluent_prompt_editor_widget import FluentPromptEditorWidget
        
        self.parent.prompt_editor_interface = FluentPromptEditorWidget(self.parent)
    
    def create_prompt_reverser_interface(self):
        """创建提示词反推界面"""
        from .fluent_prompt_reverser_widget import FluentPromptReverserWidget
        
        self.parent.prompt_reverser_interface = FluentPromptReverserWidget(self.parent)
    
    def create_settings_interface(self):
        """创建设置界面"""
        from .fluent_settings_widget import FluentSettingsWidget
        
        self.parent.settings_interface = FluentSettingsWidget(self.parent)
    
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
        
        trial_features = [
            "✓ 基础图片信息提取",
            "✓ 提示词查看和编辑",
            "✓ 历史记录查看",
            "✓ 单个文件导出",
            "✗ 批量处理功能",
            "✗ AI智能标签",
            "✗ 高级导出功能"
        ]
        
        for feature in trial_features:
            feature_label = BodyLabel(feature)
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
        
        full_features = [
            "✓ 全部基础功能",
            "✓ 批量处理功能",
            "✓ AI智能标签",
            "✓ 高级导出功能",
            "✓ ComfyUI集成",
            "✓ 云端同步",
            "✓ 优先技术支持"
        ]
        
        for feature in full_features:
            feature_label = BodyLabel(feature)
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