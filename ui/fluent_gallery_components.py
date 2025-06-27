#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片画廊相关组件
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from qfluentwidgets import (EditableComboBox, CardWidget, SmoothScrollArea, 
                           FlowLayout, TitleLabel, BodyLabel, PushButton, ComboBox,
                           InfoBar, InfoBarPosition)

from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing


class HighlightEditableComboBox(EditableComboBox):
    """支持高亮匹配文本的可编辑下拉框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_items = []
        self._filter_updating = False  # 添加过滤更新标志位
        # 暂时不连接信号，在外部手动连接
    
    def setup_filter_connection(self):
        """设置过滤连接（由外部调用）"""
        try:
            # 尝试使用lineEdit方法
            if hasattr(self, 'lineEdit') and callable(getattr(self, 'lineEdit')):
                line_edit = self.lineEdit()
                if line_edit and hasattr(line_edit, 'textChanged'):
                    line_edit.textChanged.connect(self.filter_items)
        except Exception as e:
            print(f"设置过滤连接失败: {e}")
    
    def addItems(self, items):
        """添加项目"""
        if self._filter_updating:
            return
        self.original_items = items.copy()
        super().addItems(items)
    
    def filter_items(self, text):
        """根据输入文本过滤项目"""
        if self._filter_updating:
            return
            
        self._filter_updating = True
        try:
            if not text:
                # 如果没有输入，显示所有项目
                self.clear()
                super().addItems(self.original_items)
                return
            
            # 过滤匹配的项目
            filtered_items = []
            text_lower = text.lower()
            
            for item in self.original_items:
                if text_lower in item.lower():
                    filtered_items.append(item)
            
            # 更新下拉框内容
            current_text = text
            self.clear()
            super().addItems(filtered_items)
            
            # 恢复输入的文本
            try:
                if hasattr(self, 'lineEdit') and callable(getattr(self, 'lineEdit')):
                    line_edit = self.lineEdit()
                    if line_edit:
                        line_edit.setText(current_text)
                elif hasattr(self, 'setCurrentText'):
                    self.setCurrentText(current_text)
            except:
                pass
        except Exception as e:
            print(f"过滤项目时出错: {e}")
        finally:
            self._filter_updating = False


class FluentImageCard(CardWidget):
    """Fluent Design 图片卡片组件"""
    clicked = pyqtSignal(dict)
    
    def __init__(self, record_data, parent=None, card_width=240):
        super().__init__(parent)
        self.record_data = record_data
        self.card_width = card_width  # 支持动态宽度
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """初始化卡片UI"""
        # 设置最小大小和固定高度，宽度自适应
        self.setMinimumSize(self.card_width, 360)
        self.setMaximumHeight(360)
        # 设置大小策略为水平扩展，垂直固定
        from PyQt5.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setBorderRadius(20)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                 FluentSpacing.MD, FluentSpacing.MD)
        layout.setSpacing(FluentSpacing.SM)
        
        # 图片预览
        self.image_label = QLabel()
        # 图片宽度根据卡片宽度动态调整
        image_width = self.card_width - 32  # 减去边距
        self.image_label.setMinimumSize(image_width, 170)
        self.image_label.setMaximumSize(16777215, 170)  # 宽度不限制，高度固定
        self.image_label.setAlignment(Qt.AlignCenter)
        # 设置图片预览的大小策略
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                border: none;
                border-radius: 16px;
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_tertiary')};
            }}
        """)
        
        # 加载图片
        file_path = self.record_data.get('file_path', '')
        if os.path.exists(file_path):
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(image_width, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet(f"""
                    QLabel {{
                        border: none;
                        border-radius: 16px;
                        background-color: {FluentColors.get_color('bg_primary')};
                    }}
                """)
            else:
                self.image_label.setText("🖼️\n图片无法加载")
                self.image_label.setStyleSheet(f"""
                    QLabel {{
                        border: 2px dashed {FluentColors.get_color('border_primary')};
                        border-radius: 16px;
                        background-color: {FluentColors.get_color('bg_secondary')};
                        color: {FluentColors.get_color('text_tertiary')};
                        font-size: 14px;
                    }}
                """)
        else:
            self.image_label.setText("❌\n图片不存在")
            self.image_label.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {FluentColors.get_color('error')};
                    border-radius: 16px;
                    background-color: rgba(239, 68, 68, 0.05);
                    color: {FluentColors.get_color('error')};
                    font-size: 14px;
                }}
            """)
        
        # 文件名
        file_name = self.record_data.get('custom_name') or self.record_data.get('file_name', '未知')
        if len(file_name) > 28:
            file_name = file_name[:25] + "..."
        name_label = QLabel(file_name)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                font-size: 16px;
                color: {FluentColors.get_color('text_primary')};
                border: none;
                background: transparent;
                padding: 8px 4px 4px 4px;
            }}
        """)
        name_label.setWordWrap(True)
        
        # 模型信息
        model = self.record_data.get('model', '未知模型')
        if not model or model.strip() == '':
            model = '未知模型'
        if len(model) > 35:
            model = model[:32] + "..."
        model_label = QLabel(f"🎨 {model}")
        model_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {FluentColors.get_color('text_secondary')};
                border: none;
                background: transparent;
                padding: 2px 4px;
            }}
        """)
        
        # 标签信息
        tags = self.record_data.get('tags', '').strip()
        if tags:
            # 限制标签显示长度，避免卡片过高
            if len(tags) > 30:
                tags_display = tags[:27] + "..."
            else:
                tags_display = tags
            tags_label = QLabel(f"🏷️ {tags_display}")
        else:
            tags_label = QLabel("🏷️ 暂无标签")
        
        tags_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {FluentColors.get_color('text_tertiary')};
                border: none;
                background: transparent;
                padding: 2px 4px;
            }}
        """)
        tags_label.setWordWrap(True)
        
        # LoRA信息
        lora_info = self.record_data.get('lora_info', '')
        if lora_info:
            try:
                import json
                lora_display = ""
                if isinstance(lora_info, str) and lora_info.strip():
                    lora_data = json.loads(lora_info)
                    if isinstance(lora_data, dict) and 'loras' in lora_data and lora_data['loras']:
                        # 正确的LoRA数据结构
                        lora_names = []
                        for lora in lora_data['loras']:
                            if isinstance(lora, dict) and 'name' in lora:
                                name = lora.get('name', '未知')
                                weight = lora.get('weight', 1.0)
                                lora_names.append(f"{name}({weight})")
                        
                        if lora_names:
                            # 限制显示的LoRA数量，避免卡片过高
                            if len(lora_names) > 2:
                                lora_display = ", ".join(lora_names[:2]) + f"等{len(lora_names)}个"
                            else:
                                lora_display = ", ".join(lora_names)
                    elif isinstance(lora_data, dict):
                        # 备用格式
                        lora_items = []
                        for name, weight in lora_data.items():
                            if name != 'loras':
                                lora_items.append(f"{name}({weight})")
                                if len(lora_items) >= 2:
                                    break
                        lora_display = ", ".join(lora_items)
                
                if lora_display:
                    # 限制LoRA显示长度
                    if len(lora_display) > 25:
                        lora_display = lora_display[:22] + "..."
                    lora_label = QLabel(f"🎯 {lora_display}")
                else:
                    lora_label = QLabel("🎯 暂无LoRA")
            except Exception as e:
                lora_label = QLabel("🎯 LoRA解析错误")
        else:
            lora_label = QLabel("🎯 暂无LoRA")
        
        lora_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {FluentColors.get_color('text_tertiary')};
                border: none;
                background: transparent;
                padding: 2px 4px;
            }}
        """)
        lora_label.setWordWrap(True)
        
        # 创建时间
        created_at = self.record_data.get('created_at', '')
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('T', ' '))
                time_str = dt.strftime('%m-%d %H:%M')
            except:
                time_str = created_at[:16]
        else:
            time_str = '未知时间'
        
        time_label = QLabel(f"⏰ {time_str}")
        time_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {FluentColors.get_color('text_tertiary')};
                border: none;
                background: transparent;
                padding: 2px 4px;
            }}
        """)
        
        layout.addWidget(self.image_label)
        layout.addWidget(name_label)
        layout.addWidget(model_label)
        layout.addWidget(tags_label)
        layout.addWidget(lora_label)
        layout.addWidget(time_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def setup_animations(self):
        """设置动画效果"""
        # 这里可以添加更复杂的动画效果
        pass
    
    def resizeEvent(self, event):
        """卡片大小改变时更新图片尺寸"""
        super().resizeEvent(event)
        # 动态调整图片预览大小
        if hasattr(self, 'image_label') and self.image_label.pixmap():
            current_width = self.width() - 32  # 减去边距
            if current_width > 0:
                self.update_image_size(current_width)
    
    def update_image_size(self, new_width):
        """更新图片显示尺寸"""
        if not hasattr(self, 'image_label') or not self.image_label.pixmap():
            return
        
        try:
            file_path = self.record_data.get('file_path', '')
            if os.path.exists(file_path):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(new_width, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"更新图片尺寸时出错: {e}")
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border: 2px solid {FluentColors.get_color('primary')};
            }}
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {FluentColors.get_color('bg_primary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
            }}
        """)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(f"""
                CardWidget {{
                    background-color: {FluentColors.get_color('bg_tertiary')};
                    border: 2px solid {FluentColors.get_color('primary')};
                }}
            """)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            # 发出我们自定义的信号，带参数
            self.clicked.emit(self.record_data)
        # 不调用父类的 mouseReleaseEvent，避免发出无参数的 clicked 信号


class FluentGalleryWidget(SmoothScrollArea):
    """Fluent Design 图片画廊组件"""
    record_selected = pyqtSignal(dict)
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.all_records = []
        self.filtered_records = []
        self.current_filter_field = ""
        self.current_filter_value = ""
        self._updating_filters = False  # 添加标志位防止递归
        self.current_card_width = 240  # 当前卡片宽度
        self.init_ui()
        self.load_records()
        
    def init_ui(self):
        """初始化UI"""
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.LG)
        
        # 标题和操作区域
        header_card = CardWidget()
        header_card.setBorderRadius(16)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.MD, 
                                       FluentSpacing.LG, FluentSpacing.MD)
        
        # 第一行：标题和刷新按钮
        title_row = QHBoxLayout()
        
        # 标题
        title_label = TitleLabel("🖼️ 图片记录画廊")
        title_label.setStyleSheet(f"color: {FluentColors.get_color('text_primary')};")
        
        # 刷新按钮
        self.refresh_btn = PushButton("刷新")
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.clicked.connect(self.load_records)
        
        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(self.refresh_btn)
        
        # 第二行：筛选器
        filter_row = QHBoxLayout()
        filter_row.setSpacing(FluentSpacing.MD)
        
        # 筛选字段标签
        filter_label = BodyLabel("筛选:")
        filter_label.setStyleSheet(f"color: {FluentColors.get_color('text_primary')};")
        
        # 第一个下拉框：筛选字段
        self.field_combo = ComboBox()
        self.field_combo.addItems(["全部", "模型", "LoRA", "标签"])
        self.field_combo.setFixedWidth(120)
        self.field_combo.currentTextChanged.connect(self.on_field_changed)
        
        # 第二个下拉框：筛选值
        self.value_combo = HighlightEditableComboBox()
        self.value_combo.setFixedWidth(200)
        self.value_combo.setPlaceholderText("输入或选择筛选值...")
        self.value_combo.currentTextChanged.connect(self.on_value_changed)
        # 暂时不连接lineEdit的textChanged信号，避免递归
        
        # 清除筛选按钮
        self.clear_filter_btn = PushButton("清除筛选")
        self.clear_filter_btn.setFixedHeight(32)
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.field_combo)
        filter_row.addWidget(self.value_combo)
        filter_row.addWidget(self.clear_filter_btn)
        filter_row.addStretch()
        
        header_layout.addLayout(title_row)
        header_layout.addLayout(filter_row)
        header_card.setLayout(header_layout)
        
        # 图片网格容器
        self.grid_widget = QWidget()
        from PyQt5.QtWidgets import QGridLayout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(FluentSpacing.MD)
        self.grid_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                           FluentSpacing.MD, FluentSpacing.MD)
        # 设置网格布局属性
        self.grid_layout.setVerticalSpacing(FluentSpacing.MD)
        self.grid_layout.setHorizontalSpacing(FluentSpacing.MD)
        self.grid_widget.setLayout(self.grid_layout)
        
        # 存储当前的行列数
        self.current_columns = 4  # 默认4列
        self.current_rows = 0
        
        main_layout.addWidget(header_card)
        main_layout.addWidget(self.grid_widget, 1)  # 让网格容器占用所有可用空间
        
        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)
        
    def resizeEvent(self, event):
        """窗口大小改变事件，动态调整卡片大小"""
        super().resizeEvent(event)
        self.update_card_layout()
    
    def update_card_layout(self):
        """更新卡片布局，实现响应式设计"""
        if not hasattr(self, 'grid_widget') or not self.grid_widget:
            return
            
        # 获取可用宽度
        available_width = self.width() - 60  # 减去边距和滚动条
        
        # 计算最佳列数
        min_card_width = 200  # 最小卡片宽度
        max_card_width = 300  # 最大卡片宽度
        spacing = 16          # 卡片间距
        
        # 计算最佳列数（2-6列）
        best_columns = 4  # 默认4列
        for columns in range(6, 1, -1):  # 从6列到2列
            total_spacing = (columns - 1) * spacing + 32  # 加上左右边距
            card_width = (available_width - total_spacing) / columns
            
            if card_width >= min_card_width:
                best_columns = columns
                # 限制最大宽度
                if card_width > max_card_width:
                    card_width = max_card_width
                break
        
        # 如果列数发生变化，重新布局
        if self.current_columns != best_columns:
            self.current_columns = best_columns
            # 计算新的卡片宽度（平分可用宽度）
            total_spacing = (best_columns - 1) * spacing + 32
            self.current_card_width = (available_width - total_spacing) / best_columns
            # 限制在合理范围内
            self.current_card_width = min(max(self.current_card_width, min_card_width), max_card_width)
            self.current_card_width = int(self.current_card_width)
            
            # 设置列的拉伸因子，实现平分效果
            for col in range(best_columns):
                self.grid_layout.setColumnStretch(col, 1)
            
            # 清除多余列的拉伸因子
            for col in range(best_columns, 6):
                self.grid_layout.setColumnStretch(col, 0)
                
            self.refresh_cards()
    
    def refresh_cards(self):
        """使用新的卡片宽度重新创建所有卡片"""
        if hasattr(self, 'filtered_records') and self.filtered_records:
            self.display_records(self.filtered_records)
        
    def load_records(self):
        """加载记录"""
        try:
            self.all_records = self.data_manager.get_all_records()
            self.filtered_records = self.all_records.copy()
            
            # 重置筛选器
            self.current_filter_field = "全部"
            self.current_filter_value = ""
            if hasattr(self, 'field_combo'):
                self.field_combo.setCurrentIndex(0)
                self.value_combo.clear()
            
            self.display_records(self.filtered_records)
            
            print(f"加载完成: 共加载 {len(self.all_records)} 条记录")
        except Exception as e:
            print(f"加载失败: {str(e)}")
    
    def display_records(self, records):
        """显示记录"""
        # 更安全的清理方法
        try:
            # 方法1：直接删除所有子widget
            for i in reversed(range(self.grid_layout.count())):
                child = self.grid_layout.itemAt(i)
                if child:
                    widget = child.widget()
                    if widget:
                        self.grid_layout.removeWidget(widget)
                        widget.setParent(None)
                        widget.deleteLater()
        except Exception as e:
            print(f"清理布局时出错: {e}")
            # 备用清理方法
            try:
                while self.grid_layout.count():
                    item = self.grid_layout.takeAt(0)
                    if item and item.widget():
                        item.widget().deleteLater()
            except:
                pass
        
        # 强制处理事件，确保widget被删除
        QApplication.processEvents()
        
        if not records:
            # 显示空状态
            empty_card = CardWidget()
            empty_card.setBorderRadius(20)
            empty_card.setFixedSize(400, 200)
            
            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignCenter)
            
            icon_label = QLabel("🖼️")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 48px;
                    color: {FluentColors.get_color('text_tertiary')};
                    background: transparent;
                    border: none;
                    padding: 20px;
                }}
            """)
            
            text_label = BodyLabel("暂无图片记录\n\n请先在信息提取页面处理一些图片")
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet(f"""
                BodyLabel {{
                    color: {FluentColors.get_color('text_secondary')};
                    background: transparent;
                    border: none;
                    line-height: 24px;
                }}
            """)
            
            empty_layout.addWidget(icon_label)
            empty_layout.addWidget(text_label)
            empty_card.setLayout(empty_layout)
            
            self.grid_layout.addWidget(empty_card)
            return
        
        # 重置行数
        self.current_rows = 0
        
        # 创建图片卡片并按网格排列
        for i, record in enumerate(records):
            try:
                card = FluentImageCard(record, self, self.current_card_width)
                card.clicked.connect(self.on_card_clicked)
                
                # 计算行列位置
                row = i // self.current_columns
                col = i % self.current_columns
                
                # 添加到网格布局
                self.grid_layout.addWidget(card, row, col)
                
                # 更新行数
                if row >= self.current_rows:
                    self.current_rows = row + 1
                    
            except Exception as e:
                print(f"创建图片卡片时出错: {e}")
        
        # 在最后一行添加拉伸，确保卡片顶部对齐
        if self.current_rows > 0:
            self.grid_layout.setRowStretch(self.current_rows, 1)
        
        # 强制更新布局
        self.grid_widget.update()
        self.update()
    
    def on_card_clicked(self, record_data):
        """卡片点击事件"""
        self.record_selected.emit(record_data)
    
    def on_field_changed(self, field_text):
        """筛选字段改变时的处理"""
        if self._updating_filters:
            return
        
        self._updating_filters = True
        try:
            self.current_filter_field = field_text
            self.update_value_options()
        finally:
            self._updating_filters = False
    
    def on_value_changed(self, value_text):
        """筛选值改变时的处理"""
        if self._updating_filters:
            return
        
        self._updating_filters = True
        try:
            self.current_filter_value = value_text
            self.apply_filters()
        finally:
            self._updating_filters = False
    
    def update_value_options(self):
        """更新筛选值下拉框的选项"""
        # 使用blockSignals临时阻止信号发射
        self.value_combo.blockSignals(True)
        sorted_values = []  # 在外部定义变量
        
        try:
            self.value_combo.clear()
            self.value_combo.original_items = []
            
            if not self.all_records or self.current_filter_field == "全部":
                # 如果是"全部"，清除筛选值并显示所有记录
                self.current_filter_value = ""
                self.filtered_records = self.all_records.copy()
                self.display_records(self.filtered_records)
                return
            
            # 根据筛选字段获取所有可能的值
            values = set()
            
            for record in self.all_records:
                if self.current_filter_field == "模型":
                    model = record.get('model', '').strip()
                    if model:
                        values.add(model)
                elif self.current_filter_field == "LoRA":
                    lora_info = record.get('lora_info', '')
                    if lora_info:
                        # 解析LoRA信息
                        try:
                            import json
                            if isinstance(lora_info, str) and lora_info.strip():
                                lora_data = json.loads(lora_info)
                                if isinstance(lora_data, dict) and 'loras' in lora_data:
                                    # 正确的LoRA数据结构：{"loras": [{"name": "xxx", "weight": 0.8}]}
                                    for lora_item in lora_data['loras']:
                                        if isinstance(lora_item, dict) and 'name' in lora_item:
                                            values.add(lora_item['name'])
                                elif isinstance(lora_data, dict):
                                    # 备用：直接从字典键中查找
                                    for key in lora_data.keys():
                                        if key != 'loras':  # 避免添加'loras'这个键本身
                                            values.add(key)
                                elif isinstance(lora_data, list):
                                    # 备用：如果是列表格式
                                    for lora_item in lora_data:
                                        if isinstance(lora_item, dict) and 'name' in lora_item:
                                            values.add(lora_item['name'])
                        except Exception as e:
                            print(f"解析LoRA信息失败: {e}")
                            # 如果是字符串形式，尝试直接解析
                            if isinstance(lora_info, str):
                                values.add(lora_info)
                elif self.current_filter_field == "标签":
                    tags = record.get('tags', '').strip()
                    if tags:
                        # 分割标签（支持逗号、分号、空格分割）
                        import re
                        tag_list = re.split(r'[,;，；\s]+', tags)
                        for tag in tag_list:
                            tag = tag.strip()
                            if tag:
                                values.add(tag)

            
            # 排序并添加到下拉框
            sorted_values = sorted(list(values))
            self.value_combo.addItems(sorted_values)
            
        finally:
            # 恢复信号发射
            self.value_combo.blockSignals(False)
        
        # 如果有选项，自动选择第一个并触发筛选
        if sorted_values:
            # 设置当前选中的值
            self.current_filter_value = sorted_values[0]
            self.value_combo.setCurrentIndex(0)
            # 手动触发筛选
            print(f"自动选择筛选值: {self.current_filter_value}")
            self.apply_filters()
        else:
            # 如果没有选项，清除筛选值
            self.current_filter_value = ""
            self.filtered_records = self.all_records.copy()
            self.display_records(self.filtered_records)
    
    def apply_filters(self):
        """应用筛选"""
        if not self.all_records:
            return
        
        if self.current_filter_field == "全部" or not self.current_filter_value:
            self.filtered_records = self.all_records.copy()
        else:
            self.filtered_records = []
            filter_value_lower = self.current_filter_value.lower()
            
            for record in self.all_records:
                match = False
                
                if self.current_filter_field == "模型":
                    model = record.get('model', '').lower()
                    match = filter_value_lower in model
                
                elif self.current_filter_field == "LoRA":
                    lora_info = record.get('lora_info', '')
                    if lora_info:
                        try:
                            import json
                            if isinstance(lora_info, str) and lora_info.strip():
                                lora_data = json.loads(lora_info)
                                if isinstance(lora_data, dict) and 'loras' in lora_data:
                                    # 正确的LoRA数据结构：{"loras": [{"name": "xxx", "weight": 0.8}]}
                                    for lora_item in lora_data['loras']:
                                        if isinstance(lora_item, dict) and 'name' in lora_item:
                                            if filter_value_lower in lora_item['name'].lower():
                                                match = True
                                                break
                                elif isinstance(lora_data, dict):
                                    # 备用：直接从字典键中查找
                                    for key in lora_data.keys():
                                        if key != 'loras':  # 避免添加'loras'这个键本身
                                            if filter_value_lower in key.lower():
                                                match = True
                                                break
                                elif isinstance(lora_data, list):
                                    # 备用：如果是列表格式
                                    for lora_item in lora_data:
                                        if isinstance(lora_item, dict) and 'name' in lora_item:
                                            if filter_value_lower in lora_item['name'].lower():
                                                match = True
                                                break
                        except Exception as e:
                            print(f"解析LoRA信息失败: {e}")
                            # 如果是字符串形式，尝试直接解析
                            if isinstance(lora_info, str):
                                match = filter_value_lower in lora_info.lower()
                
                elif self.current_filter_field == "标签":
                    tags = record.get('tags', '').lower()
                    match = filter_value_lower in tags
                

                
                if match:
                    self.filtered_records.append(record)
        
        self.display_records(self.filtered_records)
        
        # 更新状态信息（暂时移除InfoBar以避免主题问题）
        if self.current_filter_field != "全部" and self.current_filter_value:
            print(f"筛选结果: 找到 {len(self.filtered_records)} 条匹配记录")
    
    def clear_filters(self):
        """清除所有筛选"""
        if self._updating_filters:
            return
            
        self._updating_filters = True
        try:
            self.field_combo.setCurrentIndex(0)  # 选择"全部"
            self.value_combo.clear()
            self.current_filter_field = "全部"
            self.current_filter_value = ""
            self.filtered_records = self.all_records.copy()
            self.display_records(self.filtered_records)
        finally:
            self._updating_filters = False 