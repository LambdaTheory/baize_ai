#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息提取界面布局
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from qfluentwidgets import (CardWidget, SubtitleLabel, BodyLabel, LineEdit, TextEdit,
                           SmoothScrollArea, TransparentPushButton, PushButton)

from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing


class FluentExtractionLayout:
    """信息提取界面布局管理器"""
    
    def __init__(self, parent):
        self.parent = parent
        
    def create_extraction_interface(self):
        """创建信息提取界面 - 三列布局"""
        interface = QWidget()
        interface.setAcceptDrops(True)  # 使整个界面支持拖拽
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                     FluentSpacing.MD, FluentSpacing.MD)
        main_layout.setSpacing(FluentSpacing.SM)
        
        # 许可证状态栏
        self.create_license_status_bar(main_layout)
        
        # 主要内容布局 - 三列
        layout = QHBoxLayout()
        layout.setSpacing(FluentSpacing.LG)
        
        # 第一列 - 图片预览和基础信息
        self.create_first_column(layout)
        
        # 第二列 - AI信息
        self.create_second_column(layout)
        
        # 第三列 - 标签备注和历史记录
        self.create_third_column(layout)
        
        # 将主要内容布局添加到主布局
        main_layout.addLayout(layout)
        
        interface.setLayout(main_layout)
        
        # 设置对象名称
        interface.setObjectName("extraction")
        
        return interface
    
    def create_license_status_bar(self, parent_layout):
        """创建许可证状态栏"""
        self.parent.license_status_card = CardWidget()
        self.parent.license_status_card.setFixedHeight(60)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.SM, 
                                       FluentSpacing.MD, FluentSpacing.SM)
        
        # 状态图标和文本
        self.parent.license_status_icon = BodyLabel("🔓")
        self.parent.license_status_icon.setStyleSheet("font-size: 16px;")
        
        self.parent.license_status_text = BodyLabel("检查许可证状态中...")
        self.parent.license_status_text.setStyleSheet("font-weight: 500;")
        
        # 快速激活按钮
        from qfluentwidgets import PrimaryPushButton
        self.parent.quick_activate_btn = PrimaryPushButton("立即激活")
        self.parent.quick_activate_btn.setFixedSize(80, 32)
        
        # 布局
        status_layout.addWidget(self.parent.license_status_icon)
        status_layout.addWidget(self.parent.license_status_text)
        status_layout.addStretch()
        status_layout.addWidget(self.parent.quick_activate_btn)
        
        self.parent.license_status_card.setLayout(status_layout)
        parent_layout.addWidget(self.parent.license_status_card)
        
    def create_first_column(self, parent_layout):
        """创建第一列：图片预览区域(100%高度)"""
        first_column = QWidget()
        column_layout = QVBoxLayout()
        column_layout.setSpacing(0)  # 移除间距以实现100%高度
        column_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        first_column.setLayout(column_layout)
        
        # 图片预览卡片 (100%)
        self.parent.image_preview_card = CardWidget()
        self.parent.image_preview_card.setBorderRadius(16)
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                        FluentSpacing.LG, FluentSpacing.LG)
        
        # 图片标签 - 占用所有可用空间
        self.parent.image_label = QLabel()
        self.parent.image_label.setAlignment(Qt.AlignCenter)
        self.parent.image_label.setMinimumHeight(500)  # 增加最小高度
        self.parent.image_label.setScaledContents(False)
        self.parent.image_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {FluentColors.get_color('border_primary')};
                border-radius: 12px;
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_tertiary')};
                font-size: 16px;
            }}
        """)
        self.parent.image_label.setText("🖼️ 将图片拖拽到此处\n💻 支持从SD WebUI、ComfyUI等浏览器拖拽")
        
        # 图片标签占用全部空间
        preview_layout.addWidget(self.parent.image_label, 1)
        self.parent.image_preview_card.setLayout(preview_layout)
        
        # 创建隐藏的控件来保持与其他代码的兼容性
        # 这些控件不会显示在界面上，但需要保留以避免其他代码报错
        self.parent.file_name_edit = LineEdit()
        self.parent.file_name_edit.hide()
        self.parent.file_path_label = BodyLabel("-")
        self.parent.file_path_label.hide()
        self.parent.file_size_label = BodyLabel("-")
        self.parent.file_size_label.hide()
        self.parent.image_size_label = BodyLabel("-")
        self.parent.image_size_label.hide()
        
        # 图片预览卡片占用100%高度
        column_layout.addWidget(self.parent.image_preview_card, 1)
        
        parent_layout.addWidget(first_column, 3)  # 第一列占3份
    
    def create_second_column(self, parent_layout):
        """创建第二列：AI信息(100%)"""
        second_column = QWidget()
        column_layout = QVBoxLayout()
        column_layout.setSpacing(FluentSpacing.MD)
        second_column.setLayout(column_layout)
        
        # AI信息卡片 (100%)
        self.parent.ai_info_card = CardWidget()
        self.parent.ai_info_card.setBorderRadius(16)
        ai_layout = QVBoxLayout()
        ai_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                   FluentSpacing.LG, FluentSpacing.LG)
        
        # 标题
        ai_title = SubtitleLabel("🤖 AI生成信息")
        ai_title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 8px;
        """)
        
        # AI信息滚动区域
        ai_scroll = SmoothScrollArea()
        ai_scroll.setWidgetResizable(True)
        ai_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.parent.ai_content = QWidget()
        self.parent.ai_content_layout = QVBoxLayout()
        self.parent.ai_content_layout.setSpacing(FluentSpacing.SM)
        
        # 正向提示词区域
        positive_prompt_layout = QHBoxLayout()
        self.parent.positive_prompt_label = BodyLabel("正向提示词:")
        self.parent.positive_prompt_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        # 正向提示词跳转翻译按钮
        self.parent.positive_translate_btn = TransparentPushButton("跳转翻译")
        self.parent.positive_translate_btn.setFixedHeight(24)
        self.parent.positive_translate_btn.setFixedWidth(80)
        self.parent.positive_translate_btn.setStyleSheet(f"""
            TransparentPushButton {{
                color: {FluentColors.get_color('accent')};
                border: 1px solid {FluentColors.get_color('accent')};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            TransparentPushButton:hover {{
                background-color: {FluentColors.get_color('accent')};
                color: white;
            }}
        """)
        
        positive_prompt_layout.addWidget(self.parent.positive_prompt_label)
        positive_prompt_layout.addStretch()
        positive_prompt_layout.addWidget(self.parent.positive_translate_btn)
        
        self.parent.positive_prompt_text = TextEdit()
        self.parent.positive_prompt_text.setMaximumHeight(120)  # 从80增加到120
        self.parent.positive_prompt_text.setPlaceholderText("正向提示词...")
        
        # 反向提示词区域
        negative_prompt_layout = QHBoxLayout()
        self.parent.negative_prompt_label = BodyLabel("反向提示词:")
        self.parent.negative_prompt_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        # 反向提示词跳转翻译按钮
        self.parent.negative_translate_btn = TransparentPushButton("跳转翻译")
        self.parent.negative_translate_btn.setFixedHeight(24)
        self.parent.negative_translate_btn.setFixedWidth(80)
        self.parent.negative_translate_btn.setStyleSheet(f"""
            TransparentPushButton {{
                color: {FluentColors.get_color('accent')};
                border: 1px solid {FluentColors.get_color('accent')};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            TransparentPushButton:hover {{
                background-color: {FluentColors.get_color('accent')};
                color: white;
            }}
        """)
        
        negative_prompt_layout.addWidget(self.parent.negative_prompt_label)
        negative_prompt_layout.addStretch()
        negative_prompt_layout.addWidget(self.parent.negative_translate_btn)
        
        self.parent.negative_prompt_text = TextEdit()
        self.parent.negative_prompt_text.setMaximumHeight(100)  # 从60增加到100
        self.parent.negative_prompt_text.setPlaceholderText("反向提示词...")
        
        # 提示词操作按钮区域
        prompt_buttons_layout = QHBoxLayout()
        self.parent.save_prompts_btn = PushButton("💾 保存")
        self.parent.save_prompts_btn.setFixedHeight(32)
        self.parent.save_prompts_btn.setFixedWidth(80)
        self.parent.save_prompts_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('primary')};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }}
            PushButton:hover {{
                background-color: rgba(0, 120, 215, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(0, 120, 215, 0.9);
            }}
        """)
        
        self.parent.reset_prompts_btn = PushButton("🔄 重置")
        self.parent.reset_prompts_btn.setFixedHeight(32)
        self.parent.reset_prompts_btn.setFixedWidth(80)
        self.parent.reset_prompts_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('bg_tertiary')};
                color: {FluentColors.get_color('text_primary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }}
            PushButton:hover {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border-color: {FluentColors.get_color('accent')};
            }}
        """)
        
        prompt_buttons_layout.addWidget(self.parent.save_prompts_btn)
        prompt_buttons_layout.addWidget(self.parent.reset_prompts_btn)
        prompt_buttons_layout.addStretch()
        
        # 生成方式
        self.parent.generation_method_label = BodyLabel("生成方式:")
        self.parent.generation_method_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.parent.generation_method_text = BodyLabel("-")
        self.parent.generation_method_text.setStyleSheet("""
            color: #1F2937;
            background-color: rgba(248, 250, 252, 0.8);
            border: 1px solid rgba(229, 231, 235, 0.6);
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
        """)
        
        # 生成参数
        self.parent.params_label = BodyLabel("生成参数:")
        self.parent.params_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.parent.params_widget = QWidget()
        self.parent.params_layout = QVBoxLayout()
        self.parent.params_widget.setLayout(self.parent.params_layout)
        
        self.parent.ai_content_layout.addLayout(positive_prompt_layout)
        self.parent.ai_content_layout.addWidget(self.parent.positive_prompt_text)
        self.parent.ai_content_layout.addLayout(negative_prompt_layout)
        self.parent.ai_content_layout.addWidget(self.parent.negative_prompt_text)
        self.parent.ai_content_layout.addLayout(prompt_buttons_layout)
        self.parent.ai_content_layout.addWidget(self.parent.generation_method_label)
        self.parent.ai_content_layout.addWidget(self.parent.generation_method_text)
        self.parent.ai_content_layout.addWidget(self.parent.params_label)
        self.parent.ai_content_layout.addWidget(self.parent.params_widget)
        self.parent.ai_content_layout.addStretch()
        
        self.parent.ai_content.setLayout(self.parent.ai_content_layout)
        ai_scroll.setWidget(self.parent.ai_content)
        
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(ai_scroll)
        self.parent.ai_info_card.setLayout(ai_layout)
        
        # AI信息卡片占满整个列
        column_layout.addWidget(self.parent.ai_info_card, 1)
        
        parent_layout.addWidget(second_column, 3)  # 第二列占3份
    
    def create_third_column(self, parent_layout):
        """创建第三列：标签备注(40%) + 历史记录(60%)"""
        third_column = QWidget()
        column_layout = QVBoxLayout()
        column_layout.setSpacing(FluentSpacing.MD)
        third_column.setLayout(column_layout)
        
        # 标签备注卡片 (40%)
        self.parent.tags_notes_card = CardWidget()
        self.parent.tags_notes_card.setBorderRadius(16)
        tags_layout = QVBoxLayout()
        tags_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        
        # 标题
        tags_title = SubtitleLabel("🏷️ 标签与备注")
        tags_title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 8px;
        """)
        
        # 标签备注滚动区域
        tags_scroll = SmoothScrollArea()
        tags_scroll.setWidgetResizable(True)
        tags_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        tags_content = QWidget()
        tags_content_layout = QVBoxLayout()
        tags_content_layout.setSpacing(FluentSpacing.SM)
        
        # 用户标签
        user_tags_label = BodyLabel("用户标签:")
        user_tags_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.parent.user_tags_edit = TextEdit()
        self.parent.user_tags_edit.setMaximumHeight(60)
        self.parent.user_tags_edit.setPlaceholderText("输入标签，用逗号分隔...")
        
        # 用户备注
        user_notes_label = BodyLabel("用户备注:")
        user_notes_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.parent.user_notes_edit = TextEdit()
        self.parent.user_notes_edit.setPlaceholderText("输入备注信息...")
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        self.parent.save_btn = PushButton("保存记录")
        self.parent.save_btn.setFixedHeight(32)
        self.parent.copy_btn = PushButton("复制信息")
        self.parent.copy_btn.setFixedHeight(32)
        self.parent.export_btn = PushButton("HTML分享")
        self.parent.export_btn.setFixedHeight(32)
        
        button_layout.addWidget(self.parent.save_btn)
        button_layout.addWidget(self.parent.copy_btn)
        button_layout.addWidget(self.parent.export_btn)
        button_layout.addStretch()
        
        tags_content_layout.addWidget(user_tags_label)
        tags_content_layout.addWidget(self.parent.user_tags_edit)
        tags_content_layout.addWidget(user_notes_label)
        tags_content_layout.addWidget(self.parent.user_notes_edit)
        tags_content_layout.addLayout(button_layout)
        tags_content_layout.addStretch()
        
        tags_content.setLayout(tags_content_layout)
        tags_scroll.setWidget(tags_content)
        
        tags_layout.addWidget(tags_title)
        tags_layout.addWidget(tags_scroll)
        self.parent.tags_notes_card.setLayout(tags_layout)
        
        # 历史记录卡片 (70%)
        self.parent.history_card = CardWidget()
        self.parent.history_card.setBorderRadius(16)
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(FluentSpacing.SM, FluentSpacing.SM, 
                                        FluentSpacing.SM, FluentSpacing.SM)
        
        # 历史记录组件（直接添加，不需要额外标题）
        from .fluent_history_widget import FluentHistoryWidget
        self.parent.history_widget = FluentHistoryWidget(self.parent.data_manager)
        
        # 加载历史记录
        self.parent.history_widget.load_history()
        
        history_layout.addWidget(self.parent.history_widget, 1)  # 添加拉伸因子，让历史记录组件占用全部空间
        self.parent.history_card.setLayout(history_layout)
        
        # 按30%和70%的比例添加到列布局
        column_layout.addWidget(self.parent.tags_notes_card, 3)    # 30%
        column_layout.addWidget(self.parent.history_card, 7)       # 70%
        
        parent_layout.addWidget(third_column, 2)  # 第三列占2份 