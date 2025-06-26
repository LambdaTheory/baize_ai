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
        
        # 显示顺序：生成方式 → 模型 → LoRA → 生成参数
        # 0. 显示生成方式
        self.create_generation_method_display(image_info)
        
        # 1. 显示模型信息
        self.create_model_display(image_info)
        
        # 2. 显示LoRA信息
        self.create_lora_display(image_info)
        
        # 3. 显示生成参数
        self.create_generation_params_display(image_info)
        
        # 定义生成参数映射（移除模型相关，加入sampler）
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
        
        # 注意：主要的显示逻辑已经移到上面的专门方法中
        # 不再显示其他参数区域 
    
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
        
        method_title = BodyLabel("🚀 生成方式:")
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
        
        # 根据不同生成方式设置不同颜色
        if generation_method == "ComfyUI":
            card_style = """
                QFrame {
                    background-color: rgba(243, 232, 255, 0.6);
                    border: 1px solid rgba(147, 51, 234, 0.2);
                    border-radius: 8px;
                    padding: 0px;
                }
                QFrame:hover {
                    background-color: rgba(243, 232, 255, 0.8);
                    border-color: rgba(147, 51, 234, 0.3);
                }
            """
            icon = "🎨"
        elif generation_method == "SD WebUI":
            card_style = """
                QFrame {
                    background-color: rgba(254, 242, 242, 0.6);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 8px;
                    padding: 0px;
                }
                QFrame:hover {
                    background-color: rgba(254, 242, 242, 0.8);
                    border-color: rgba(239, 68, 68, 0.3);
                }
            """
            icon = "🖼️"
        else:
            card_style = """
                QFrame {
                    background-color: rgba(240, 253, 250, 0.6);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    border-radius: 8px;
                    padding: 0px;
                }
                QFrame:hover {
                    background-color: rgba(240, 253, 250, 0.8);
                    border-color: rgba(16, 185, 129, 0.3);
                }
            """
            icon = "🔧"
        
        method_card.setStyleSheet(card_style)
        
        method_layout = QHBoxLayout()
        method_layout.setContentsMargins(12, 8, 12, 8)
        method_layout.setSpacing(10)
        
        # 图标
        method_icon = BodyLabel(icon)
        method_icon.setStyleSheet("font-size: 16px;")
        
        # 生成方式名称
        method_label = BodyLabel(generation_method)
        method_label.setStyleSheet("""
            color: #1F2937;
            font-size: 14px;
            font-weight: 600;
        """)
        
        method_layout.addWidget(method_icon)
        method_layout.addWidget(method_label, 1)
        
        method_card.setLayout(method_layout)
        self.parent.params_layout.addWidget(method_card)
        
        # 添加间距
        spacer = QWidget()
        spacer.setFixedHeight(8)
        self.parent.params_layout.addWidget(spacer)
    
    def create_model_display(self, image_info):
        """创建模型信息展示"""
        from qfluentwidgets import BodyLabel
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
        
        # 检查多种可能的模型字段
        model_name = (image_info.get('model_name', '') or 
                     image_info.get('model', '') or
                     image_info.get('checkpoint', '') or
                     image_info.get('unet_model', '') or
                     image_info.get('ckpt_name', ''))
        model_hash = (image_info.get('model_hash', '') or
                     image_info.get('checkpoint_hash', ''))
        
        if not model_name and not model_hash:
            return
        
        # 模型标题区域
        model_title_widget = QWidget()
        model_title_layout = QHBoxLayout()
        model_title_layout.setContentsMargins(0, 0, 0, 4)
        model_title_layout.setSpacing(8)
        
        model_title = BodyLabel("🤖 模型:")
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
                background-color: rgba(252, 231, 243, 0.6);
                border: 1px solid rgba(236, 72, 153, 0.2);
                border-radius: 8px;
                padding: 0px;
            }
            QFrame:hover {
                background-color: rgba(252, 231, 243, 0.8);
                border-color: rgba(236, 72, 153, 0.3);
            }
        """)
        
        model_layout = QVBoxLayout()
        model_layout.setContentsMargins(12, 10, 12, 10)
        model_layout.setSpacing(6)
        
        # 模型名称
        if model_name:
            name_layout = QHBoxLayout()
            name_layout.setSpacing(8)
            
            name_icon = BodyLabel("📋")
            name_icon.setStyleSheet("font-size: 14px;")
            
            name_label = BodyLabel(model_name)
            name_label.setStyleSheet("""
                color: #1F2937;
                font-size: 13px;
                font-weight: 600;
            """)
            name_label.setWordWrap(True)
            
            name_layout.addWidget(name_icon)
            name_layout.addWidget(name_label, 1)
            model_layout.addLayout(name_layout)
        
        # 模型哈希
        if model_hash:
            hash_layout = QHBoxLayout()
            hash_layout.setSpacing(8)
            
            hash_icon = BodyLabel("🔑")
            hash_icon.setStyleSheet("font-size: 12px;")
            
            hash_label = BodyLabel(f"哈希: {model_hash[:16]}..." if len(model_hash) > 16 else f"哈希: {model_hash}")
            hash_label.setStyleSheet("""
                color: #6B7280;
                font-size: 11px;
                font-weight: 400;
                background-color: rgba(243, 244, 246, 0.8);
                border: 1px solid rgba(209, 213, 219, 0.5);
                padding: 2px 6px;
                border-radius: 4px;
            """)
            
            hash_layout.addWidget(hash_icon)
            hash_layout.addWidget(hash_label, 1)
            model_layout.addLayout(hash_layout)
        
        model_card.setLayout(model_layout)
        self.parent.params_layout.addWidget(model_card)
        
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
        
        # 添加间距
        spacer = QWidget()
        spacer.setFixedHeight(8)
        self.parent.params_layout.addWidget(spacer)
    
    def create_generation_params_display(self, image_info):
        """创建生成参数展示"""
        from qfluentwidgets import BodyLabel
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
        
        # 生成参数映射（按优先级排序）
        param_mapping = [
            (['sampler', 'sampler_name'], '采样器'),
            (['scheduler'], '调度器'),
            (['steps'], '采样步数'),
            (['cfg_scale'], 'CFG Scale'),
            (['seed'], '随机种子'),
            (['size'], '尺寸'),
            (['denoising_strength'], '去噪强度'),
            (['clip_skip'], 'Clip Skip'),
            (['ensd'], 'ENSD')
        ]
        
        # 检查是否有参数需要显示
        has_params = False
        for keys, _ in param_mapping:
            if any(image_info.get(key, '') for key in keys):
                has_params = True
                break
        
        if not has_params:
            return
        
        # 参数标题区域
        params_title_widget = QWidget()
        params_title_layout = QHBoxLayout()
        params_title_layout.setContentsMargins(0, 0, 0, 4)
        params_title_layout.setSpacing(8)
        
        params_title = BodyLabel("⚙️ 生成参数:")
        params_title.setStyleSheet("""
            color: #6B7280;
            font-size: 12px;
            font-weight: 600;
        """)
        
        params_title_layout.addWidget(params_title)
        params_title_layout.addStretch()
        params_title_widget.setLayout(params_title_layout)
        
        self.parent.params_layout.addWidget(params_title_widget)
        
        # 参数容器
        params_container = QWidget()
        params_container_layout = QVBoxLayout()
        params_container_layout.setContentsMargins(0, 0, 0, 8)
        params_container_layout.setSpacing(4)
        
        for keys, label in param_mapping:
            # 找到第一个有值的字段
            value = None
            for key in keys:
                value = image_info.get(key, '')
                if value:
                    break
            
            if value:
                # 创建参数卡片
                param_card = QFrame()
                param_card.setFrameStyle(QFrame.NoFrame)
                param_card.setStyleSheet("""
                    QFrame {
                        background-color: rgba(236, 253, 245, 0.6);
                        border: 1px solid rgba(34, 197, 94, 0.2);
                        border-radius: 6px;
                        padding: 0px;
                    }
                    QFrame:hover {
                        background-color: rgba(236, 253, 245, 0.8);
                        border-color: rgba(34, 197, 94, 0.3);
                    }
                """)
                
                param_layout = QHBoxLayout()
                param_layout.setContentsMargins(10, 6, 10, 6)
                param_layout.setSpacing(8)
                
                # 参数标签
                param_label = BodyLabel(f"{label}:")
                param_label.setStyleSheet("""
                    color: #6B7280;
                    font-size: 11px;
                    font-weight: 600;
                    min-width: 60px;
                """)
                
                # 参数值
                param_value = BodyLabel(str(value))
                param_value.setStyleSheet("""
                    color: #1F2937;
                    font-size: 12px;
                    font-weight: 500;
                """)
                param_value.setWordWrap(True)
                
                param_layout.addWidget(param_label)
                param_layout.addWidget(param_value, 1)
                
                param_card.setLayout(param_layout)
                params_container_layout.addWidget(param_card)
        
        params_container.setLayout(params_container_layout)
        self.parent.params_layout.addWidget(params_container)