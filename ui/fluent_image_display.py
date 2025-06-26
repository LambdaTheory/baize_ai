#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片显示和信息处理组件
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from qfluentwidgets import BodyLabel, InfoBar, InfoBarPosition
from .fluent_styles import FluentColors


class FluentImageDisplay(QObject):
    """图片显示和信息处理组件"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def display_image_info(self, file_path, image_info=None):
        """显示图片信息到新布局"""
        import os
        from PyQt5.QtGui import QPixmap
        from qfluentwidgets import BodyLabel
        
        try:
            # 显示图片预览
            if os.path.exists(file_path):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 缩放图片以适应显示区域
                    scaled_pixmap = pixmap.scaled(
                        self.parent.image_label.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.parent.image_label.setPixmap(scaled_pixmap)
                else:
                    self.parent.image_label.setText("无法加载图片")
            else:
                self.parent.image_label.setText("图片文件不存在")
            
            # 显示基础信息
            filename = os.path.basename(file_path)
            self.parent.file_name_edit.setText(filename)
            self.parent.file_path_label.setText(file_path)
            
            # 文件大小
            try:
                file_size = os.path.getsize(file_path)
                size_text = self.format_file_size(file_size)
                self.parent.file_size_label.setText(size_text)
            except:
                self.parent.file_size_label.setText("-")
            
            # 图片尺寸
            if not pixmap.isNull():
                dimensions = f"{pixmap.width()} x {pixmap.height()}"
                self.parent.image_size_label.setText(dimensions)
            else:
                self.parent.image_size_label.setText("-")
            
            # 显示AI信息
            if image_info and isinstance(image_info, dict):
                # 正向提示词
                prompt = image_info.get('prompt', '')
                self.parent.positive_prompt_text.setPlainText(prompt)
                
                # 反向提示词
                negative_prompt = image_info.get('negative_prompt', '')
                self.parent.negative_prompt_text.setPlainText(negative_prompt)
                
                # 保存原始提示词数据（用于重置功能）
                self.parent.original_prompts['positive'] = prompt
                self.parent.original_prompts['negative'] = negative_prompt
                
                # 生成方式判断
                generation_method = self.detect_generation_method(image_info)
                self.parent.generation_method_text.setText(generation_method)
                
                # 生成参数
                self.clear_params_layout()
                self.create_params_layout(image_info)
            else:
                # 清空AI信息
                self.parent.positive_prompt_text.setPlainText("")
                self.parent.negative_prompt_text.setPlainText("")
                self.parent.generation_method_text.setText("-")
                self.clear_params_layout()
                
                # 清空原始提示词数据
                self.parent.original_prompts['positive'] = ''
                self.parent.original_prompts['negative'] = ''
                
        except Exception as e:
            print(f"显示图片信息时出错: {e}")
            self.parent.image_label.setText(f"显示错误: {str(e)}")
    
    def format_file_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def detect_generation_method(self, image_info):
        """检测图片的生成方式"""
        if not isinstance(image_info, dict):
            return "-"
        
        # 检查ComfyUI特有标识
        if 'workflow' in image_info or 'comfyui' in str(image_info).lower():
            return "ComfyUI"
        
        # 检查SD WebUI特有参数
        webui_indicators = ['sampler_name', 'cfg_scale', 'steps', 'seed']
        if any(key in image_info for key in webui_indicators):
            return "SD WebUI"
        
        # 检查其他标识符
        software = image_info.get('software', '').lower()
        if 'comfy' in software:
            return "ComfyUI"
        elif 'automatic1111' in software or 'webui' in software:
            return "SD WebUI"
        
        # 如果有prompt但无明确标识，默认为SD WebUI
        if image_info.get('prompt'):
            return "SD WebUI"
        
        return "-"
    
    def clear_params_layout(self):
        """清空参数布局"""
        while self.parent.params_layout.count():
            child = self.parent.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def create_params_layout(self, image_info):
        """创建参数布局"""
        from qfluentwidgets import BodyLabel
        from PyQt5.QtWidgets import QWidget, QVBoxLayout
        
        # 确保image_info是字典类型
        if not isinstance(image_info, dict):
            return
        
        # 定义参数映射
        param_mapping = {
            'steps': '采样步数',
            'sampler_name': '采样器',
            'cfg_scale': 'CFG Scale',
            'seed': '随机种子',
            'size': '尺寸',
            'model_name': '模型',
            'model_hash': '模型哈希',
            'denoising_strength': '去噪强度',
            'clip_skip': 'Clip Skip',
            'ensd': 'ENSD'
        }
        
        # 显示主要参数
        for key, label in param_mapping.items():
            value = image_info.get(key, '')
            if value:
                param_widget = QWidget()
                param_layout = QVBoxLayout()
                param_layout.setSpacing(2)
                param_layout.setContentsMargins(0, 4, 0, 4)
                
                # 参数标签
                param_label = BodyLabel(f"{label}:")
                param_label.setStyleSheet("""
                    color: #6B7280;
                    font-size: 12px;
                    font-weight: 500;
                    margin-bottom: 2px;
                """)
                
                # 参数值
                param_value = BodyLabel(str(value))
                param_value.setStyleSheet("""
                    color: #1F2937;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: rgba(248, 250, 252, 0.8);
                    border: 1px solid rgba(229, 231, 235, 0.6);
                    padding: 6px 10px;
                    border-radius: 6px;
                    margin-top: 2px;
                """)
                param_value.setWordWrap(True)
                
                param_layout.addWidget(param_label)
                param_layout.addWidget(param_value)
                param_widget.setLayout(param_layout)
                
                self.parent.params_layout.addWidget(param_widget)
        
        # 显示LoRA信息
        self.create_lora_display(image_info)
        
        # 如果有其他参数，显示"更多参数"部分
        excluded_keys = list(param_mapping.keys()) + [
            'prompt', 'negative_prompt', 'workflow', 'lora_info', 'generation_source'
        ]
        other_params = {}
        for key, value in image_info.items():
            if key not in excluded_keys:
                if value and str(value).strip():
                    other_params[key] = value
        
        if other_params:
            # 添加分隔线
            separator = QWidget()
            separator.setFixedHeight(1)
            separator.setStyleSheet("background-color: rgba(229, 231, 235, 0.6);")
            self.parent.params_layout.addWidget(separator)
            
            # 其他参数标题
            other_title = BodyLabel("其他参数:")
            other_title.setStyleSheet("""
                color: #6B7280;
                font-size: 12px;
                font-weight: 600;
                margin: 8px 0 4px 0;
            """)
            self.parent.params_layout.addWidget(other_title)
            
            # 显示其他参数（限制显示数量）
            count = 0
            for key, value in other_params.items():
                if count >= 5:  # 最多显示5个其他参数
                    break
                
                param_widget = QWidget()
                param_layout = QVBoxLayout()
                param_layout.setSpacing(2)
                param_layout.setContentsMargins(0, 2, 0, 2)
                
                # 参数标签
                param_label = BodyLabel(f"{key}:")
                param_label.setStyleSheet("""
                    color: #6B7280;
                    font-size: 11px;
                    font-weight: 500;
                """)
                
                # 参数值（截断长文本）
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                
                param_value = BodyLabel(value_str)
                param_value.setStyleSheet("""
                    color: #1F2937;
                    font-size: 11px;
                    background-color: rgba(248, 250, 252, 0.8);
                    border: 1px solid rgba(229, 231, 235, 0.5);
                    padding: 3px 8px;
                    border-radius: 4px;
                """)
                param_value.setWordWrap(True)
                
                param_layout.addWidget(param_label)
                param_layout.addWidget(param_value)
                param_widget.setLayout(param_layout)
                
                self.parent.params_layout.addWidget(param_widget)
                count += 1 
    
    def create_lora_display(self, image_info):
        """创建LoRA信息展示"""
        from qfluentwidgets import BodyLabel
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
        
        lora_info = image_info.get('lora_info', {})
        if not lora_info:
            return
        
        # 解析LoRA数据
        lora_list = []
        if isinstance(lora_info, dict):
            if 'loras' in lora_info and isinstance(lora_info['loras'], list):
                lora_list = lora_info['loras']
            elif 'loras' not in lora_info:
                for name, weight in lora_info.items():
                    lora_list.append({"name": name, "weight": weight})
        elif isinstance(lora_info, list):
            lora_list = lora_info
        
        if not lora_list:
            return
        
        # 添加分隔线
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(229, 231, 235, 0.6);")
        self.parent.params_layout.addWidget(separator)
        
        # LoRA标题区域
        lora_title_widget = QWidget()
        lora_title_layout = QHBoxLayout()
        lora_title_layout.setContentsMargins(0, 8, 0, 4)
        lora_title_layout.setSpacing(8)
        
        lora_title = BodyLabel("🎨 LoRA模型:")
        lora_title.setStyleSheet("""
            color: #6B7280;
            font-size: 12px;
            font-weight: 600;
        """)
        
        lora_count = BodyLabel(f"({len(lora_list)}个)")
        lora_count.setStyleSheet("""
            color: #9CA3AF;
            font-size: 11px;
            font-weight: 400;
        """)
        
        lora_title_layout.addWidget(lora_title)
        lora_title_layout.addWidget(lora_count)
        lora_title_layout.addStretch()
        lora_title_widget.setLayout(lora_title_layout)
        
        self.parent.params_layout.addWidget(lora_title_widget)
        
        # LoRA列表容器
        lora_container = QWidget()
        lora_container_layout = QVBoxLayout()
        lora_container_layout.setContentsMargins(0, 0, 0, 8)
        lora_container_layout.setSpacing(6)
        
        for i, lora in enumerate(lora_list):
            if isinstance(lora, dict):
                name = lora.get('name', 'Unknown')
                weight = lora.get('weight', 'N/A')
                
                # 创建单个LoRA卡片
                lora_card = QFrame()
                lora_card.setFrameStyle(QFrame.NoFrame)
                lora_card.setStyleSheet("""
                    QFrame {
                        background-color: rgba(248, 250, 252, 0.6);
                        border: 1px solid rgba(229, 231, 235, 0.4);
                        border-radius: 8px;
                        padding: 0px;
                    }
                    QFrame:hover {
                        background-color: rgba(240, 245, 251, 0.8);
                        border-color: rgba(99, 102, 241, 0.3);
                    }
                """)
                
                lora_layout = QHBoxLayout()
                lora_layout.setContentsMargins(10, 8, 10, 8)
                lora_layout.setSpacing(8)
                
                # LoRA名称
                name_label = BodyLabel(name)
                name_label.setStyleSheet("""
                    color: #1F2937;
                    font-size: 12px;
                    font-weight: 500;
                """)
                name_label.setWordWrap(True)
                
                # 权重标签
                weight_label = BodyLabel(f"权重: {weight}")
                weight_label.setStyleSheet("""
                    color: #6B7280;
                    font-size: 11px;
                    font-weight: 400;
                    background-color: rgba(239, 246, 255, 0.8);
                    border: 1px solid rgba(147, 197, 253, 0.3);
                    padding: 2px 6px;
                    border-radius: 4px;
                """)
                weight_label.setFixedHeight(20)
                
                # 序号标签
                index_label = BodyLabel(f"{i+1}")
                index_label.setStyleSheet("""
                    color: #6B7280;
                    font-size: 10px;
                    font-weight: 600;
                    background-color: rgba(229, 231, 235, 0.6);
                    border-radius: 8px;
                    min-width: 16px;
                    max-width: 16px;
                    min-height: 16px;
                    max-height: 16px;
                    text-align: center;
                """)
                index_label.setAlignment(Qt.AlignCenter)
                
                lora_layout.addWidget(index_label)
                lora_layout.addWidget(name_label, 1)
                lora_layout.addWidget(weight_label)
                
                lora_card.setLayout(lora_layout)
                lora_container_layout.addWidget(lora_card)
        
        lora_container.setLayout(lora_container_layout)
        self.parent.params_layout.addWidget(lora_container)