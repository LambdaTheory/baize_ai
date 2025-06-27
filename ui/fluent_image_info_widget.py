#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 图片信息展示组件
使用PyQt-Fluent-Widgets组件库
"""

import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QSizePolicy, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from qfluentwidgets import (CardWidget, BodyLabel, SubtitleLabel, TitleLabel,
                           LineEdit, TextEdit, PushButton, GroupHeaderCardWidget,
                           SmoothScrollArea, FlowLayout, TransparentPushButton, 
                           InfoBar, InfoBarPosition)
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing, FluentTypography


class FluentImageInfoWidget(SmoothScrollArea):
    """Fluent Design 图片信息展示组件"""
    
    # 添加信号
    edit_prompt_requested = pyqtSignal(str, str)  # 传递提示词内容和图片名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file_path = ""  # 存储当前文件路径
        self.current_image_info = {}  # 存储当前图片信息
        self.init_ui()
        self.setup_preset_tags()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI"""
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(FluentSpacing.LG)
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        
        # 1. 图片预览卡片
        self.create_image_preview_card(main_layout)
        
        # 2. 基本信息卡片
        self.create_basic_info_card(main_layout)
        
        # 3. AI生成信息卡片
        self.create_ai_info_card(main_layout)
        
        # 4. 用户信息卡片
        self.create_user_info_card(main_layout)
        
        # 5. 操作按钮卡片
        self.create_action_buttons_card(main_layout)
        
        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)
        
    def create_image_preview_card(self, parent_layout):
        """创建图片预览卡片"""
        card = CardWidget()
        card.setBorderRadius(16)
        card.setMinimumHeight(280)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                FluentSpacing.LG, FluentSpacing.LG)
        
        # 标题
        title = SubtitleLabel("📸 图片预览")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        
        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setMaximumHeight(220)
        self.image_label.setScaledContents(False)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {FluentColors.get_color('border_primary')};
                border-radius: 12px;
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_tertiary')};
                font-size: 16px;
            }}
        """)
        self.image_label.setText("等待图片加载...")
        
        layout.addWidget(title)
        layout.addWidget(self.image_label)
        card.setLayout(layout)
        parent_layout.addWidget(card)
        
    def create_basic_info_card(self, parent_layout):
        """创建基本信息卡片"""
        card = CardWidget()
        card.setBorderRadius(16)
        
        # 创建标题
        title = SubtitleLabel("📋 基本信息")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(FluentSpacing.MD)
        content_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.MD, 
                                        FluentSpacing.LG, FluentSpacing.LG)
        
        # 网格布局
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(FluentSpacing.LG)
        grid_layout.setVerticalSpacing(FluentSpacing.MD)
        
        # 文件名（可编辑）
        file_name_label = BodyLabel("文件名")
        file_name_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.file_name_edit = LineEdit()
        self.file_name_edit.setPlaceholderText("可编辑文件名...")
        self.file_name_edit.setFixedHeight(36)
        
        grid_layout.addWidget(file_name_label, 0, 0)
        grid_layout.addWidget(self.file_name_edit, 0, 1)
        
        # 文件路径
        path_label = BodyLabel("文件路径")
        path_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.file_path_label = BodyLabel("-")
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            background-color: {FluentColors.get_color('bg_secondary')};
            padding: 8px 12px;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
        """)
        
        grid_layout.addWidget(path_label, 1, 0)
        grid_layout.addWidget(self.file_path_label, 1, 1)
        
        # 文件大小和图片尺寸
        size_label = BodyLabel("文件大小")
        size_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.file_size_label = BodyLabel("-")
        self.file_size_label.setStyleSheet(f"color: {FluentColors.get_color('text_primary')};")
        
        dimension_label = BodyLabel("图片尺寸")
        dimension_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        self.image_size_label = BodyLabel("-")
        self.image_size_label.setStyleSheet(f"color: {FluentColors.get_color('text_primary')};")
        
        grid_layout.addWidget(size_label, 2, 0)
        grid_layout.addWidget(self.file_size_label, 2, 1)
        grid_layout.addWidget(dimension_label, 3, 0)
        grid_layout.addWidget(self.image_size_label, 3, 1)
        
        # 设置列拉伸
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)
        
        content_layout.addLayout(grid_layout)
        
        # 设置卡片布局
        card.setLayout(content_layout)
        parent_layout.addWidget(card)
        
    def create_ai_info_card(self, parent_layout):
        """创建AI生成信息卡片"""
        card = CardWidget()
        card.setBorderRadius(16)
        
        # 创建标题容器
        title_layout = QHBoxLayout()
        title = SubtitleLabel("🤖 AI生成信息")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        
        # 工作流类型标签
        self.workflow_type_label = BodyLabel("")
        self.workflow_type_label.setStyleSheet(f"""
            color: white;
            background-color: {FluentColors.get_color('accent')};
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        """)
        self.workflow_type_label.hide()  # 默认隐藏
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.workflow_type_label)
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(FluentSpacing.MD)
        content_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                        FluentSpacing.LG, FluentSpacing.LG)
        
        # 添加标题布局
        content_layout.addLayout(title_layout)
        
        # Prompt区域
        prompt_header = QHBoxLayout()
        prompt_label = BodyLabel("正向提示词 (Prompt)")
        prompt_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        
        # 编辑按钮
        self.edit_prompt_btn = PushButton("✏️ 编辑")
        self.edit_prompt_btn.setFixedSize(80, 28)
        self.edit_prompt_btn.setToolTip("将提示词导入到提示词编辑器")
        self.edit_prompt_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('accent')};
                color: white;
                border: none;
                padding: 4px 8px;
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
        
        # 添加到header布局
        prompt_header.addWidget(prompt_label)
        prompt_header.addStretch()
        prompt_header.addWidget(self.edit_prompt_btn)
        
        self.prompt_text = TextEdit()
        self.prompt_text.setMinimumHeight(120)
        self.prompt_text.setMaximumHeight(150)
        self.prompt_text.setReadOnly(True)
        self.prompt_text.setPlaceholderText("暂无正向提示词...")
        
        # Negative Prompt区域
        neg_prompt_label = BodyLabel("反向提示词 (Negative Prompt)")
        neg_prompt_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        
        self.neg_prompt_text = TextEdit()
        self.neg_prompt_text.setMinimumHeight(100)
        self.neg_prompt_text.setMaximumHeight(120)
        self.neg_prompt_text.setReadOnly(True)
        self.neg_prompt_text.setPlaceholderText("暂无反向提示词...")
        
        # 参数区域 - 使用可变布局
        self.params_card = CardWidget()
        self.params_card.setBorderRadius(12)
        self.params_card.setStyleSheet(f"""
            background-color: {FluentColors.get_color('bg_secondary')};
            border: 1px solid {FluentColors.get_color('border_secondary')};
        """)
        
        # 创建参数区域的容器
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                           FluentSpacing.MD, FluentSpacing.MD)
        self.params_container.setLayout(self.params_layout)
        self.params_card.setLayout(QVBoxLayout())
        self.params_card.layout().addWidget(self.params_container)
        
        # Lora信息
        lora_label = BodyLabel("Lora 信息")
        lora_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        
        self.lora_text = TextEdit()
        self.lora_text.setMinimumHeight(100)
        self.lora_text.setMaximumHeight(130)
        self.lora_text.setReadOnly(True)
        self.lora_text.setPlaceholderText("暂无Lora信息...")
        
        # AI功能按钮区域
        ai_buttons_layout = QHBoxLayout()
        ai_buttons_layout.setSpacing(FluentSpacing.MD)
        
        # 分享HTML按钮
        self.share_html_btn = PushButton("📤 分享HTML")
        self.share_html_btn.setFixedHeight(36)
        self.share_html_btn.setMinimumWidth(120)
        self.share_html_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('primary')};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }}
            PushButton:hover {{
                background-color: rgba(16, 137, 211, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(16, 137, 211, 0.6);
            }}
        """)
        
        # 导出工作流按钮
        self.export_workflow_btn = PushButton("📋 导出工作流")
        self.export_workflow_btn.setFixedHeight(36)
        self.export_workflow_btn.setMinimumWidth(140)
        self.export_workflow_btn.setStyleSheet(f"""
            PushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }}
            PushButton:hover {{
                background-color: rgba(16, 185, 129, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(16, 185, 129, 0.6);
            }}
        """)
        
        ai_buttons_layout.addWidget(self.share_html_btn)
        ai_buttons_layout.addWidget(self.export_workflow_btn)
        ai_buttons_layout.addStretch()
        
        # 添加到布局
        content_layout.addLayout(prompt_header)
        content_layout.addWidget(self.prompt_text)
        content_layout.addWidget(neg_prompt_label)
        content_layout.addWidget(self.neg_prompt_text)
        content_layout.addWidget(BodyLabel("生成参数"))
        content_layout.addWidget(self.params_card)
        content_layout.addWidget(lora_label)
        content_layout.addWidget(self.lora_text)
        content_layout.addLayout(ai_buttons_layout)
        
        # 设置卡片布局
        card.setLayout(content_layout)
        parent_layout.addWidget(card)
        
    def create_standard_params_layout(self):
        """创建标准参数布局（SD WebUI / 标准ComfyUI）"""
        # 安全地清空现有布局
        self.safe_clear_layout()
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(FluentSpacing.LG)
        grid_layout.setVerticalSpacing(FluentSpacing.SM)
        
        # 创建参数输入框
        self.create_param_field(grid_layout, "模型", 0, 0)
        self.model_edit = LineEdit()
        self.model_edit.setReadOnly(True)
        self.model_edit.setFixedHeight(32)
        grid_layout.addWidget(self.model_edit, 0, 1)
        
        self.create_param_field(grid_layout, "采样器", 0, 2)
        self.sampler_edit = LineEdit()
        self.sampler_edit.setReadOnly(True)
        self.sampler_edit.setFixedHeight(32)
        grid_layout.addWidget(self.sampler_edit, 0, 3)
        
        self.create_param_field(grid_layout, "Steps", 1, 0)
        self.steps_edit = LineEdit()
        self.steps_edit.setReadOnly(True)
        self.steps_edit.setFixedHeight(32)
        self.steps_edit.setMaximumWidth(100)
        grid_layout.addWidget(self.steps_edit, 1, 1)
        
        self.create_param_field(grid_layout, "CFG Scale", 1, 2)
        self.cfg_edit = LineEdit()
        self.cfg_edit.setReadOnly(True)
        self.cfg_edit.setFixedHeight(32)
        self.cfg_edit.setMaximumWidth(100)
        grid_layout.addWidget(self.cfg_edit, 1, 3)
        
        self.create_param_field(grid_layout, "Seed", 2, 0)
        self.seed_edit = LineEdit()
        self.seed_edit.setReadOnly(True)
        self.seed_edit.setFixedHeight(32)
        grid_layout.addWidget(self.seed_edit, 2, 1, 1, 3)  # 跨列
        
        # 设置列拉伸
        grid_layout.setColumnStretch(1, 2)
        grid_layout.setColumnStretch(3, 1)
        
        self.params_layout.addLayout(grid_layout)
        
    def create_flux_params_layout(self):
        """创建Flux参数布局"""
        # 安全地清空现有布局
        self.safe_clear_layout()
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(FluentSpacing.LG)
        grid_layout.setVerticalSpacing(FluentSpacing.SM)
        
        # UNET模型
        self.create_param_field(grid_layout, "UNET 模型", 0, 0)
        self.unet_edit = LineEdit()
        self.unet_edit.setReadOnly(True)
        self.unet_edit.setFixedHeight(32)
        grid_layout.addWidget(self.unet_edit, 0, 1, 1, 3)  # 跨列
        
        # CLIP模型
        self.create_param_field(grid_layout, "CLIP 模型", 1, 0)
        self.clip_edit = LineEdit()
        self.clip_edit.setReadOnly(True)
        self.clip_edit.setFixedHeight(32)
        grid_layout.addWidget(self.clip_edit, 1, 1, 1, 3)  # 跨列
        
        # VAE模型
        self.create_param_field(grid_layout, "VAE 模型", 2, 0)
        self.vae_edit = LineEdit()
        self.vae_edit.setReadOnly(True)
        self.vae_edit.setFixedHeight(32)
        grid_layout.addWidget(self.vae_edit, 2, 1, 1, 3)  # 跨列
        
        # 采样参数
        self.create_param_field(grid_layout, "采样器", 3, 0)
        self.sampler_edit = LineEdit()
        self.sampler_edit.setReadOnly(True)
        self.sampler_edit.setFixedHeight(32)
        grid_layout.addWidget(self.sampler_edit, 3, 1)
        
        self.create_param_field(grid_layout, "Steps", 3, 2)
        self.steps_edit = LineEdit()
        self.steps_edit.setReadOnly(True)
        self.steps_edit.setFixedHeight(32)
        self.steps_edit.setMaximumWidth(100)
        grid_layout.addWidget(self.steps_edit, 3, 3)
        
        # Guidance (替代CFG Scale)
        self.create_param_field(grid_layout, "Guidance", 4, 0)
        self.guidance_edit = LineEdit()
        self.guidance_edit.setReadOnly(True)
        self.guidance_edit.setFixedHeight(32)
        self.guidance_edit.setMaximumWidth(100)
        grid_layout.addWidget(self.guidance_edit, 4, 1)
        
        # Seed
        self.create_param_field(grid_layout, "Seed", 4, 2)
        self.seed_edit = LineEdit()
        self.seed_edit.setReadOnly(True)
        self.seed_edit.setFixedHeight(32)
        grid_layout.addWidget(self.seed_edit, 4, 3)
        
        # 设置列拉伸
        grid_layout.setColumnStretch(1, 2)
        grid_layout.setColumnStretch(3, 1)
        
        self.params_layout.addLayout(grid_layout)
        
    def clear_params_layout(self):
        """清空参数布局"""
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
                
    def clear_layout(self, layout):
        """递归清空布局"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
        
    def create_param_field(self, layout, text, row, col):
        """创建参数字段标签"""
        label = BodyLabel(text)
        label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_tertiary')};
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(label, row, col)
        
    def create_user_info_card(self, parent_layout):
        """创建用户信息卡片"""
        card = CardWidget()
        card.setBorderRadius(16)
        
        # 创建标题
        title = SubtitleLabel("🏷️ 标签与备注")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(FluentSpacing.MD)
        content_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                        FluentSpacing.LG, FluentSpacing.LG)
        
        # 添加标题
        content_layout.addWidget(title)
        
        # 标签输入区域的标题和按钮
        tags_header_layout = QHBoxLayout()
        tags_label = BodyLabel("标签")
        tags_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        
        # AI自动打标签按钮
        self.auto_tag_btn = PushButton("🤖 AI自动打标签")
        self.auto_tag_btn.setFixedHeight(32)
        self.auto_tag_btn.setMinimumWidth(140)
        self.auto_tag_btn.setStyleSheet(f"""
            PushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
            }}
            PushButton:hover {{
                background-color: rgba(16, 185, 129, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(16, 185, 129, 0.6);
            }}
        """)
        
        tags_header_layout.addWidget(tags_label)
        tags_header_layout.addStretch()
        tags_header_layout.addWidget(self.auto_tag_btn)
        
        self.tags_edit = LineEdit()
        self.tags_edit.setPlaceholderText("输入标签，用逗号分隔，如: 美女,时装,写真")
        self.tags_edit.setFixedHeight(40)
        
        # 预设标签区域
        preset_label = BodyLabel("快速标签")
        preset_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        
        # 预设标签流式布局
        self.preset_tags_widget = QWidget()
        self.preset_tags_layout = FlowLayout()
        self.preset_tags_layout.setSpacing(6)  # 与提示词标签保持一致的间距
        self.preset_tags_layout.setContentsMargins(6, 6, 6, 6)  # 调整内边距
        self.preset_tags_widget.setLayout(self.preset_tags_layout)
        
        # 备注区域
        notes_label = BodyLabel("备注")
        notes_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        
        self.notes_text = TextEdit()
        self.notes_text.setMinimumHeight(80)
        self.notes_text.setMaximumHeight(120)
        self.notes_text.setPlaceholderText("在此添加备注...")
        
        # 添加到布局
        content_layout.addLayout(tags_header_layout)
        content_layout.addWidget(self.tags_edit)
        content_layout.addWidget(preset_label)
        content_layout.addWidget(self.preset_tags_widget)
        content_layout.addWidget(notes_label)
        content_layout.addWidget(self.notes_text)
        
        # 设置卡片布局
        card.setLayout(content_layout)
        parent_layout.addWidget(card)
        
    def create_action_buttons_card(self, parent_layout):
        """创建操作按钮卡片"""
        card = CardWidget()
        card.setBorderRadius(16)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.MD, 
                                FluentSpacing.LG, FluentSpacing.MD)
        layout.setSpacing(FluentSpacing.MD)
        
        # 保存按钮
        self.save_btn = PushButton("💾 保存记录 (Ctrl+S)")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setMinimumWidth(160)
        self.save_btn.setToolTip("保存当前记录信息\n快捷键: Ctrl+S")
        
        # 复制按钮
        self.copy_info_btn = PushButton("📋 复制信息")
        self.copy_info_btn.setFixedHeight(40)
        self.copy_info_btn.setMinimumWidth(120)
        self.copy_info_btn.setToolTip("复制当前图片的详细信息")
        
        layout.addWidget(self.save_btn)
        layout.addWidget(self.copy_info_btn)
        layout.addStretch()
        
        card.setLayout(layout)
        parent_layout.addWidget(card)
        
    def setup_preset_tags(self):
        """设置预设标签"""
        preset_tags = [
            "人物", "风景", "动物", "建筑", "美食",
            "艺术", "科技", "时尚", "自然", "城市",
            "夜景", "日出", "日落", "海洋", "山峰"
        ]
        
        for tag in preset_tags:
            tag_btn = TransparentPushButton(tag)
            tag_btn.setFixedHeight(32)  # 与提示词标签保持一致的高度
            tag_btn.setMinimumWidth(60)  # 参考设计图片调整最小宽度
            tag_btn.setMaximumWidth(200)  # 调整最大宽度
            tag_btn.setStyleSheet(f"""
                TransparentPushButton {{
                    border: 1px solid {FluentColors.get_color('border_primary')};
                    border-radius: 16px;
                    padding: 6px 12px;
                    background-color: {FluentColors.get_color('bg_secondary')};
                    color: {FluentColors.get_color('text_primary')};
                    font-size: 13px;
                    font-weight: 500;
                }}
                TransparentPushButton:hover {{
                    background-color: {FluentColors.get_color('primary')};
                    color: white;
                    transform: translateY(-1px);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
                    transition: all 0.2s ease;
                }}
                TransparentPushButton:pressed {{
                    transform: translateY(0px);
                }}
            """)
            tag_btn.clicked.connect(lambda checked, t=tag: self.add_preset_tag(t))
            self.preset_tags_layout.addWidget(tag_btn)
            
    def add_preset_tag(self, tag):
        """添加预设标签"""
        current_tags = self.tags_edit.text().strip()
        if current_tags:
            if tag not in current_tags:
                self.tags_edit.setText(f"{current_tags}, {tag}")
        else:
            self.tags_edit.setText(tag)
            
    def clear_info(self):
        """清空信息"""
        self.image_label.setText("等待图片加载...")
        self.image_label.setPixmap(QPixmap())
        
        self.file_path_label.setText("-")
        self.file_name_edit.clear()
        self.file_size_label.setText("-")
        self.image_size_label.setText("-")
        
        self.prompt_text.clear()
        self.neg_prompt_text.clear()
        self.lora_text.clear()
        
        # 安全地清空参数输入框
        try:
            self.clear_param_fields()
        except (RuntimeError, AttributeError):
            # 如果组件已被删除，忽略错误
            pass
        
        self.tags_edit.clear()
        self.notes_text.clear()
        
        # 隐藏工作流类型标签
        self.workflow_type_label.hide()
        
        # 隐藏导出工作流按钮
        self.export_workflow_btn.setVisible(False)
        
    def clear_param_fields(self):
        """清空参数字段"""
        # 清空可能存在的各种参数字段
        param_fields = [
            'model_edit', 'sampler_edit', 'steps_edit', 'cfg_edit', 'seed_edit',
            'unet_edit', 'clip_edit', 'vae_edit', 'guidance_edit'
        ]
        
        for field_name in param_fields:
            if hasattr(self, field_name):
                field = getattr(self, field_name)
                # 检查组件是否仍然有效
                try:
                    if hasattr(field, 'clear') and not field.isWidgetType() or field.parent() is not None:
                        field.clear()
                except (RuntimeError, AttributeError):
                    # 组件已被删除或无效，忽略错误
                    pass
                    
    def safe_clear_layout(self):
        """安全地清空参数布局"""
        # 在清空布局前，先移除对旧组件的引用
        param_fields = [
            'model_edit', 'sampler_edit', 'steps_edit', 'cfg_edit', 'seed_edit',
            'unet_edit', 'clip_edit', 'vae_edit', 'guidance_edit'
        ]
        
        for field_name in param_fields:
            if hasattr(self, field_name):
                delattr(self, field_name)
        
        # 然后清空布局
        self.clear_params_layout()

    def on_edit_prompt_clicked(self):
        """处理编辑提示词按钮点击"""
        prompt_text = self.prompt_text.toPlainText().strip()
        if not prompt_text:
            InfoBar.warning(
                title="提示",
                content="当前没有可编辑的提示词",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        
        # 获取图片文件名（不含扩展名）作为场景名称
        if self.current_file_path:
            file_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        else:
            file_name = "导入的提示词"
        
        # 发射信号，传递提示词内容和场景名称
        self.edit_prompt_requested.emit(prompt_text, file_name)
        
        InfoBar.success(
            title="提示词已导入",
            content=f"已将提示词导入到提示词编辑器的新场景：{file_name}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    def display_image_info(self, file_path, image_info=None):
        """显示图片信息"""
        try:
            # 更新当前文件路径和图片信息
            self.current_file_path = file_path
            self.current_image_info = image_info if image_info else {}
            print(f"FluentImageInfoWidget.display_image_info 被调用: {file_path}")
            print(f"组件当前可见性: {self.isVisible()}")
            
            # 强制显示组件
            self.setVisible(True)
            self.show()
            
            # 先清空现有信息
            self.clear_info()
            
            # 更新导出工作流按钮状态
            self.update_export_workflow_button()
            
            # 显示图片
            if os.path.exists(file_path):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 缩放图片以适应显示区域
                    scaled_pixmap = pixmap.scaled(
                        400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setStyleSheet(f"""
                        QLabel {{
                            border: 2px solid {FluentColors.get_color('border_primary')};
                            border-radius: 12px;
                            background-color: {FluentColors.get_color('bg_primary')};
                        }}
                    """)
                else:
                    self.image_label.setText("🖼️\n图片加载失败")
            else:
                self.image_label.setText("❌\n文件不存在")
                
            # 基本信息
            self.file_path_label.setText(file_path)
            self.file_name_edit.setText(os.path.basename(file_path))
            
            # 文件大小
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                size_str = self.format_file_size(size)
                self.file_size_label.setText(size_str)
                
                # 图片尺寸
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.image_size_label.setText(f"{pixmap.width()} × {pixmap.height()}")
                    
            # AI生成信息
            if image_info:
                # 显示工作流类型和生成来源
                generation_source = image_info.get('generation_source', 'Unknown')
                workflow_type = image_info.get('workflow_type', '')
                
                # 设置工作流类型标签
                if generation_source == 'ComfyUI' and workflow_type:
                    self.workflow_type_label.setText(f"ComfyUI - {workflow_type}")
                    self.workflow_type_label.show()
                    
                    # 根据工作流类型选择参数布局
                    if workflow_type.lower() == 'flux':
                        self.setup_flux_layout(image_info)
                    elif workflow_type.lower() in ['sdxl', 'standard', 'sd15']:
                        self.setup_standard_layout(image_info)
                    else:
                        self.setup_standard_layout(image_info)
                elif generation_source == 'Stable Diffusion WebUI':
                    self.workflow_type_label.setText("SD WebUI")
                    self.workflow_type_label.setStyleSheet(f"""
                        color: white;
                        background-color: #28a745;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 500;
                    """)
                    self.workflow_type_label.show()
                    self.setup_standard_layout(image_info)
                else:
                    self.workflow_type_label.hide()
                    self.setup_standard_layout(image_info)
                
                # 设置提示词
                self.prompt_text.setText(image_info.get('prompt', ''))
                self.neg_prompt_text.setText(image_info.get('negative_prompt', ''))
                
                # Lora信息格式化
                lora_info = image_info.get('lora_info', {})
                if lora_info:
                    formatted_lora = self._format_lora_info(lora_info)
                    self.lora_text.setText(formatted_lora)
            else:
                # 没有AI信息时隐藏工作流标签并使用标准布局
                self.workflow_type_label.hide()
                self.setup_standard_layout({})
                    
            # 强制刷新界面
            self.update()
            self.repaint()
            if self.widget():
                self.widget().update()
                self.widget().repaint()
                
            # 强制显示父组件
            parent = self.parent()
            while parent:
                parent.setVisible(True)
                parent.show()
                parent = parent.parent()
            
            print(f"界面刷新完成，组件可见: {self.isVisible()}")
            print(f"组件几何: {self.geometry()}")
            print(f"组件大小: {self.size()}")
            
            # 显示成功提示
            InfoBar.success(
                title="图片加载完成",
                content=f"已加载: {os.path.basename(file_path)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"加载图片信息时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            import traceback
            traceback.print_exc()
    
    def setup_flux_layout(self, image_info):
        """设置Flux工作流布局"""
        self.create_flux_params_layout()
        
        # 填充Flux特有的字段
        if hasattr(self, 'unet_edit'):
            self.unet_edit.setText(image_info.get('unet_model', ''))
        if hasattr(self, 'clip_edit'):
            self.clip_edit.setText(image_info.get('clip_model', ''))
        if hasattr(self, 'vae_edit'):
            self.vae_edit.setText(image_info.get('vae_model', ''))
        if hasattr(self, 'guidance_edit'):
            guidance = image_info.get('guidance', image_info.get('cfg_scale', ''))
            self.guidance_edit.setText(str(guidance) if guidance else '')
        
        # 通用字段
        if hasattr(self, 'sampler_edit'):
            self.sampler_edit.setText(image_info.get('sampler', ''))
        if hasattr(self, 'steps_edit'):
            self.steps_edit.setText(str(image_info.get('steps', '')))
        if hasattr(self, 'seed_edit'):
            self.seed_edit.setText(str(image_info.get('seed', '')))
    
    def setup_standard_layout(self, image_info):
        """设置标准工作流布局"""
        self.create_standard_params_layout()
        
        # 填充标准字段
        if hasattr(self, 'model_edit'):
            self.model_edit.setText(image_info.get('model', ''))
        if hasattr(self, 'sampler_edit'):
            self.sampler_edit.setText(image_info.get('sampler', ''))
        if hasattr(self, 'steps_edit'):
            self.steps_edit.setText(str(image_info.get('steps', '')))
        if hasattr(self, 'cfg_edit'):
            self.cfg_edit.setText(str(image_info.get('cfg_scale', '')))
        if hasattr(self, 'seed_edit'):
            self.seed_edit.setText(str(image_info.get('seed', '')))
    
    def format_file_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def _format_lora_info(self, lora_info):
        """格式化Lora信息"""
        if not lora_info:
            return ""
            
        formatted_parts = []
        
        if isinstance(lora_info, dict):
            if 'loras' in lora_info and lora_info['loras']:
                for i, lora in enumerate(lora_info['loras'], 1):
                    name = lora.get('name', '未知')
                    weight = lora.get('weight', 'N/A')
                    formatted_parts.append(f"{i}. {name} (权重: {weight})")
            elif 'raw_lora_text' in lora_info:
                formatted_parts.append(lora_info['raw_lora_text'])
        elif isinstance(lora_info, str):
            formatted_parts.append(lora_info)
            
        return '\n'.join(formatted_parts) if formatted_parts else "暂无Lora信息"
    
    def update_export_workflow_button(self):
        """更新导出工作流按钮状态"""
        try:
            # 安全检查当前图片信息
            if not hasattr(self, 'current_image_info') or not self.current_image_info:
                self.export_workflow_btn.setVisible(False)
                self.export_workflow_btn.setEnabled(False)
                return
            
            # 检查是否为ComfyUI图片且包含workflow数据
            generation_source = self.current_image_info.get('generation_source', '')
            workflow_data = self.current_image_info.get('workflow_data', '')
            
            # 确保类型检查正确
            is_comfyui = str(generation_source) == 'ComfyUI'
            
            # 检查workflow_data是否有效（支持字符串和字典类型）
            has_workflow = False
            if workflow_data:
                if isinstance(workflow_data, str):
                    # 字符串类型：检查是否非空且不只是空白字符
                    has_workflow = bool(workflow_data.strip())
                elif isinstance(workflow_data, dict):
                    # 字典类型：检查是否非空字典
                    has_workflow = bool(workflow_data)
                else:
                    # 其他类型：检查是否非空
                    has_workflow = bool(workflow_data)
            
            is_comfyui_with_workflow = is_comfyui and has_workflow
            
            # 确保传递的是布尔值
            self.export_workflow_btn.setVisible(bool(is_comfyui_with_workflow))
            self.export_workflow_btn.setEnabled(bool(is_comfyui_with_workflow))
            
            if is_comfyui_with_workflow:
                print("显示导出工作流按钮 - ComfyUI图片包含workflow数据")
            else:
                print(f"隐藏导出工作流按钮 - 非ComfyUI图片或无workflow数据 (source: {generation_source}, has_workflow: {has_workflow})")
                
        except Exception as e:
            print(f"更新导出工作流按钮状态时出错: {e}")
            import traceback
            traceback.print_exc()
            # 出错时隐藏按钮
            self.export_workflow_btn.setVisible(False)
            self.export_workflow_btn.setEnabled(False)
    
    def export_workflow(self):
        """导出ComfyUI工作流为JSON文件"""
        try:
            # 检查是否有workflow数据
            workflow_data = self.current_image_info.get('workflow_data')
            if not workflow_data:
                InfoBar.warning(
                    title="导出失败",
                    content="当前图片不包含ComfyUI工作流数据",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # 解析workflow数据（支持字符串和字典类型）
            try:
                if isinstance(workflow_data, str):
                    # 字符串类型：尝试解析JSON
                    workflow_json = json.loads(workflow_data)
                elif isinstance(workflow_data, dict):
                    # 字典类型：直接使用
                    workflow_json = workflow_data
                else:
                    # 其他类型：尝试转换
                    workflow_json = dict(workflow_data)
                    
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                InfoBar.error(
                    title="数据解析失败",
                    content=f"工作流数据格式错误: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # 生成默认文件名
            if self.current_file_path:
                base_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
                default_filename = f"{base_name}_workflow.json"
            else:
                default_filename = "comfyui_workflow.json"
            
            # 打开文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出ComfyUI工作流",
                default_filename,
                "JSON文件 (*.json);;所有文件 (*.*)"
            )
            
            if file_path:
                # 保存workflow数据到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(workflow_json, f, indent=2, ensure_ascii=False)
                
                InfoBar.success(
                    title="导出成功",
                    content=f"工作流已保存到: {os.path.basename(file_path)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
                print(f"ComfyUI工作流已导出到: {file_path}")
                print(f"工作流包含 {len(workflow_json)} 个节点")
            
        except Exception as e:
            InfoBar.error(
                title="导出失败",
                content=f"导出工作流时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            import traceback
            traceback.print_exc()
    
    def connect_signals(self):
        """连接信号槽"""
        # 连接编辑按钮（AI生成信息区域）
        self.edit_prompt_btn.clicked.connect(self.on_edit_prompt_clicked)
        
        # 连接AI功能按钮（AI生成信息区域）
        self.share_html_btn.clicked.connect(self.on_share_html_clicked)
        self.export_workflow_btn.clicked.connect(self.export_workflow)
        
        # 连接AI自动打标签按钮（用户信息区域）
        self.auto_tag_btn.clicked.connect(self.on_auto_tag_clicked)
        
        # 初始时隐藏导出工作流按钮
        self.export_workflow_btn.setVisible(False)
        
    def on_share_html_clicked(self):
        """处理分享HTML按钮点击"""
        # 这里需要实现分享HTML功能，或者发出信号给主窗口处理
        print("分享HTML按钮被点击")
        
    def on_auto_tag_clicked(self):
        """处理AI自动打标签按钮点击"""
        # 这里需要实现AI自动打标签功能，或者发出信号给主窗口处理
        print("AI自动打标签按钮被点击") 