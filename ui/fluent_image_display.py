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
                
                # 生成方式判断 (现在通过卡片展示，不需要设置旧的文本控件)
                # generation_method = self.detect_generation_method(image_info)
                # self.parent.generation_method_text.setText(generation_method)
                
                # 生成参数
                self.clear_params_layout()
                self.create_params_layout(image_info)
            else:
                # 清空AI信息
                self.parent.positive_prompt_text.setPlainText("")
                self.parent.negative_prompt_text.setPlainText("")
                # self.parent.generation_method_text.setText("-")  # 现在通过卡片展示
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
        
        # 显示模型信息
        self.create_model_display(image_info)
        
        # 显示生成方式
        self.create_generation_method_display(image_info)
        
        # 显示LoRA信息
        self.create_lora_display(image_info)
        
        # 定义生成参数映射 (移除模型相关信息，将sampler加回来)
        param_mapping = {
            'sampler_name': '采样器',
            'steps': '采样步数',
            'cfg_scale': 'CFG Scale',
            'seed': '随机种子',
            'size': '尺寸',
            'denoising_strength': '去噪强度',
            'clip_skip': 'Clip Skip',
            'ensd': 'ENSD'
        }
        
        # 生成参数标题
        if any(image_info.get(key, '') for key in param_mapping.keys()):
            # 添加分隔线
            separator = QWidget()
            separator.setFixedHeight(1)
            separator.setStyleSheet("background-color: rgba(229, 231, 235, 0.6);")
            self.parent.params_layout.addWidget(separator)
            
            params_title_widget = QWidget()
            params_title_layout = QHBoxLayout()
            params_title_layout.setContentsMargins(0, 8, 0, 4)
            params_title_layout.setSpacing(8)
            
            params_title = BodyLabel("📊 生成参数:")
            params_title.setStyleSheet("""
                color: #6B7280;
                font-size: 12px;
                font-weight: 600;
            """)
            
            params_title_layout.addWidget(params_title)
            params_title_layout.addStretch()
            params_title_widget.setLayout(params_title_layout)
            
            self.parent.params_layout.addWidget(params_title_widget)
        
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
        
        # 如果有其他参数，显示"更多参数"部分
        excluded_keys = list(param_mapping.keys()) + [
            'prompt', 'negative_prompt', 'workflow', 'lora_info', 'generation_source',
            'model_name', 'model_hash'
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
    
    def create_model_display(self, image_info):
        """创建模型信息展示"""
        from qfluentwidgets import BodyLabel
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
        
        model_name = image_info.get('model_name', '')
        model_hash = image_info.get('model_hash', '')
        
        if not model_name and not model_hash:
            return
        
        # 模型标题区域
        model_title_widget = QWidget()
        model_title_layout = QHBoxLayout()
        model_title_layout.setContentsMargins(0, 8, 0, 4)
        model_title_layout.setSpacing(8)
        
        model_title = BodyLabel("🤖 使用模型:")
        model_title.setStyleSheet("""
            color: #6B7280;
            font-size: 12px;
            font-weight: 600;
        """)
        
        model_title_layout.addWidget(model_title)
        model_title_layout.addStretch()
        model_title_widget.setLayout(model_title_layout)
        
        self.parent.params_layout.addWidget(model_title_widget)
        
        # 模型信息卡片
        model_card = QFrame()
        model_card.setFrameStyle(QFrame.NoFrame)
        model_card.setStyleSheet("""
            QFrame {
                background-color: rgba(254, 249, 195, 0.6);
                border: 1px solid rgba(251, 191, 36, 0.4);
                border-radius: 8px;
                padding: 0px;
            }
            QFrame:hover {
                background-color: rgba(254, 243, 199, 0.8);
                border-color: rgba(251, 191, 36, 0.6);
            }
        """)
        
        model_layout = QVBoxLayout()
        model_layout.setContentsMargins(12, 10, 12, 10)
        model_layout.setSpacing(6)
        
        if model_name:
            # 模型名称
            name_label = BodyLabel(model_name)
            name_label.setStyleSheet("""
                color: #1F2937;
                font-size: 13px;
                font-weight: 600;
            """)
            name_label.setWordWrap(True)
            model_layout.addWidget(name_label)
        
        if model_hash:
            # 模型哈希
            hash_container = QWidget()
            hash_layout = QHBoxLayout()
            hash_layout.setContentsMargins(0, 0, 0, 0)
            hash_layout.setSpacing(6)
            
            hash_prefix = BodyLabel("哈希:")
            hash_prefix.setStyleSheet("""
                color: #6B7280;
                font-size: 11px;
                font-weight: 500;
            """)
            
            hash_value = BodyLabel(model_hash)
            hash_value.setStyleSheet("""
                color: #374151;
                font-size: 11px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                background-color: rgba(243, 244, 246, 0.8);
                border: 1px solid rgba(209, 213, 219, 0.6);
                padding: 2px 6px;
                border-radius: 4px;
            """)
            
            hash_layout.addWidget(hash_prefix)
            hash_layout.addWidget(hash_value, 1)
            hash_container.setLayout(hash_layout)
            model_layout.addWidget(hash_container)
        
        model_card.setLayout(model_layout)
        self.parent.params_layout.addWidget(model_card)
        
        # 添加间距
        spacer = QWidget()
        spacer.setFixedHeight(8)
        self.parent.params_layout.addWidget(spacer)
    
    def create_generation_method_display(self, image_info):
        """创建生成方式展示"""
        from qfluentwidgets import BodyLabel
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
        
        generation_method = self.detect_generation_method(image_info)
        if generation_method == "-":
            return
        
        # 生成方式标题区域
        method_title_widget = QWidget()
        method_title_layout = QHBoxLayout()
        method_title_layout.setContentsMargins(0, 0, 0, 4)
        method_title_layout.setSpacing(8)
        
        method_title = BodyLabel("⚙️ 生成方式:")
        method_title.setStyleSheet("""
            color: #6B7280;
            font-size: 12px;
            font-weight: 600;
        """)
        
        method_title_layout.addWidget(method_title)
        method_title_layout.addStretch()
        method_title_widget.setLayout(method_title_layout)
        
        self.parent.params_layout.addWidget(method_title_widget)
        
        # 生成方式卡片
        method_card = QFrame()
        method_card.setFrameStyle(QFrame.NoFrame)
        
        # 根据不同的生成方式设置不同的颜色
        if generation_method == "ComfyUI":
            card_style = """
                QFrame {
                    background-color: rgba(236, 254, 255, 0.6);
                    border: 1px solid rgba(6, 182, 212, 0.4);
                    border-radius: 8px;
                    padding: 0px;
                }
                QFrame:hover {
                    background-color: rgba(207, 250, 254, 0.8);
                    border-color: rgba(6, 182, 212, 0.6);
                }
            """
        else:  # SD WebUI
            card_style = """
                QFrame {
                    background-color: rgba(239, 246, 255, 0.6);
                    border: 1px solid rgba(59, 130, 246, 0.4);
                    border-radius: 8px;
                    padding: 0px;
                }
                QFrame:hover {
                    background-color: rgba(219, 234, 254, 0.8);
                    border-color: rgba(59, 130, 246, 0.6);
                }
            """
        
        method_card.setStyleSheet(card_style)
        
        method_layout = QHBoxLayout()
        method_layout.setContentsMargins(12, 8, 12, 8)
        method_layout.setSpacing(8)
        
        # 生成方式图标和名称
        if generation_method == "ComfyUI":
            icon_text = "🔗"
        else:
            icon_text = "🖼️"
        
        icon_label = BodyLabel(icon_text)
        icon_label.setStyleSheet("""
            font-size: 16px;
        """)
        
        method_label = BodyLabel(generation_method)
        method_label.setStyleSheet("""
            color: #1F2937;
            font-size: 13px;
            font-weight: 600;
        """)
        
        method_layout.addWidget(icon_label)
        method_layout.addWidget(method_label, 1)
        method_card.setLayout(method_layout)
        
        self.parent.params_layout.addWidget(method_card)
        
        # 添加间距
        spacer = QWidget()
        spacer.setFixedHeight(8)
        self.parent.params_layout.addWidget(spacer)
    
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