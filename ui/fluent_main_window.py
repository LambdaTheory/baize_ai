#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 主窗口
使用PyQt-Fluent-Widgets组件库
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QApplication, QGridLayout, QLabel,
                            QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QThread, QObject
from PyQt5.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent, QPainter, QBrush, QColor, QPen, QFont, QLinearGradient

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, FluentWindow,
                           SplashScreen, InfoBar, InfoBarPosition, MessageBox,
                           NavigationWidget, qrouter, CardWidget, SmoothScrollArea,
                           FlowLayout, PivotItem, Pivot, setTheme, Theme, isDarkTheme,
                           ComboBox, EditableComboBox, BodyLabel, TitleLabel, PrimaryPushButton)

from core.image_reader import ImageInfoReader
from core.data_manager import DataManager
from core.html_exporter import HTMLExporter
from core.batch_processor import BatchProcessor
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing
from .fluent_drop_area import FluentDropArea
from .fluent_image_info_widget import FluentImageInfoWidget
from .fluent_history_widget import FluentHistoryWidget
from .fluent_prompt_editor_widget import FluentPromptEditorWidget
from .fluent_prompt_reverser_widget import FluentPromptReverserWidget
from .fluent_settings_widget import FluentSettingsWidget
from .fluent_activation_dialog import FluentActivationDialog
from core.license_manager import LicenseManager


class DragOverlay(QWidget):
    """拖拽蒙层组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
    def paintEvent(self, event):
        """绘制蒙层"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 创建灰色渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 60))         # 深灰色
        gradient.setColorAt(0.5, QColor(64, 64, 64, 80))    # 中灰色
        gradient.setColorAt(1, QColor(0, 0, 0, 60))         # 深灰色
        
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # 绘制圆角边框
        border_rect = self.rect().adjusted(20, 20, -20, -20)
        pen = QPen(QColor(200, 200, 200, 180), 3, Qt.DashLine)
        pen.setDashPattern([8, 4])  # 自定义虚线样式
        painter.setPen(pen)
        painter.drawRoundedRect(border_rect, 20, 20)
        
        # 绘制内部装饰边框
        inner_rect = border_rect.adjusted(10, 10, -10, -10)
        inner_pen = QPen(QColor(255, 255, 255, 80), 1, Qt.SolidLine)
        painter.setPen(inner_pen)
        painter.drawRoundedRect(inner_rect, 12, 12)
        
        # 计算中心点
        center_x = self.rect().center().x()
        center_y = self.rect().center().y()
        
        # 绘制图标
        icon_size = 64
        icon_x = center_x - icon_size // 2
        icon_y = center_y - 80  # 图标位置上移
        
        # 绘制文件图标背景
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.setBrush(QBrush(QColor(128, 128, 128, 120)))
        painter.drawEllipse(icon_x, icon_y, icon_size, icon_size)
        
        # 图标内部的"+"符号
        painter.setPen(QPen(QColor(255, 255, 255), 5, Qt.SolidLine))
        plus_center_x = icon_x + icon_size // 2
        plus_center_y = icon_y + icon_size // 2
        # 水平线
        painter.drawLine(plus_center_x - 16, plus_center_y, plus_center_x + 16, plus_center_y)
        # 垂直线
        painter.drawLine(plus_center_x, plus_center_y - 16, plus_center_x, plus_center_y + 16)
        
        # 主标题
        painter.setPen(QPen(QColor(255, 255, 255)))
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Bold)
        title_font.setFamily("Microsoft YaHei")
        painter.setFont(title_font)
        
        # 主标题位置：图标下方20px
        title_y = icon_y + icon_size + 20
        title_rect = self.rect()
        title_rect.setTop(title_y)
        title_rect.setBottom(title_y + 40)
        painter.drawText(title_rect, Qt.AlignCenter, "拖放图片到此处")
        
        # 副标题
        painter.setPen(QPen(QColor(220, 220, 220, 200)))
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_font.setWeight(QFont.Normal)
        subtitle_font.setFamily("Microsoft YaHei")
        painter.setFont(subtitle_font)
        
        # 副标题位置：主标题下方15px
        subtitle_y = title_y + 50
        subtitle_rect = self.rect()
        subtitle_rect.setTop(subtitle_y)
        subtitle_rect.setBottom(subtitle_y + 30)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "支持 PNG、JPG、JPEG 格式或文件夹")
        
        # 底部装饰点
        dot_pen = QPen(QColor(200, 200, 200, 150))
        painter.setPen(dot_pen)
        painter.setBrush(QBrush(QColor(200, 200, 200, 150)))
        
        # 装饰点位置：副标题下方40px
        dots_y = subtitle_y + 60
        
        for i in range(5):
            dot_x = center_x - 40 + i * 20
            painter.drawEllipse(dot_x - 2, dots_y - 2, 4, 4)


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


class AITagWorker(QObject):
    """AI标签异步工作类"""
    finished = pyqtSignal(bool, dict)  # 完成信号(成功, 结果数据)
    
    def __init__(self, ai_tagger, image_path, existing_tags):
        super().__init__()
        self.ai_tagger = ai_tagger
        self.image_path = image_path
        self.existing_tags = existing_tags
    
    def run(self):
        """执行AI标签分析"""
        try:
            print(f"[异步工作线程] 开始处理图片: {self.image_path}")
            success, result = self.ai_tagger.auto_tag_image(
                image_path=self.image_path,
                existing_tags=self.existing_tags,
                similarity_threshold=0.8
            )
            print(f"[异步工作线程] 处理完成，成功: {success}")
            self.finished.emit(success, result)
        except Exception as e:
            print(f"[异步工作线程] 处理异常: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, {"error": str(e)})


class FluentImageCard(CardWidget):
    """Fluent Design 图片卡片组件"""
    clicked = pyqtSignal(dict)
    
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.record_data = record_data
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """初始化卡片UI"""
        self.setFixedSize(260, 340)
        self.setBorderRadius(20)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                 FluentSpacing.MD, FluentSpacing.MD)
        layout.setSpacing(FluentSpacing.SM)
        
        # 图片预览
        self.image_label = QLabel()
        self.image_label.setFixedSize(228, 190)
        self.image_label.setAlignment(Qt.AlignCenter)
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
                scaled_pixmap = pixmap.scaled(228, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        layout.addWidget(time_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def setup_animations(self):
        """设置动画效果"""
        # 这里可以添加更复杂的动画效果
        pass
    
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
        from qfluentwidgets import TitleLabel, PushButton
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
        self.field_combo.addItems(["全部", "模型", "LoRA", "标签", "备注"])
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
        self.grid_layout = FlowLayout()
        self.grid_layout.setSpacing(FluentSpacing.LG)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_widget.setLayout(self.grid_layout)
        
        main_layout.addWidget(header_card)
        main_layout.addWidget(self.grid_widget)
        main_layout.addStretch()
        
        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)
        
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
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
        if not records:
            # 显示空状态
            empty_card = CardWidget()
            empty_card.setBorderRadius(20)
            empty_card.setFixedSize(400, 200)
            
            empty_layout = QVBoxLayout()
            empty_layout.setAlignment(Qt.AlignCenter)
            
            from qfluentwidgets import BodyLabel
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
        
        # 创建图片卡片
        for record in records:
            try:
                card = FluentImageCard(record)
                card.clicked.connect(self.on_card_clicked)
                self.grid_layout.addWidget(card)
            except Exception as e:
                print(f"创建图片卡片时出错: {e}")
        
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
                elif self.current_filter_field == "备注":
                    notes = record.get('notes', '').strip()
                    if notes:
                        values.add(notes)
            
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
                
                elif self.current_filter_field == "备注":
                    notes = record.get('notes', '').lower()
                    match = filter_value_lower in notes
                
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


class FluentMainWindow(FluentWindow):
    """Fluent Design 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.image_reader = ImageInfoReader()
        self.data_manager = DataManager()
        self.html_exporter = HTMLExporter()
        self.current_file_path = None
        
        # 许可证管理器
        self.license_manager = LicenseManager()
        self.license_status = {"is_valid": False, "message": "", "data": {}}
        
        # 初始化AI图像打标签器
        try:
            from core.ai_image_tagger import AIImageTagger
            self.ai_tagger = AIImageTagger()
            print("AI图像打标签器初始化成功")
        except Exception as e:
            print(f"AI图像打标签器初始化失败: {e}")
            self.ai_tagger = None
        
        # 初始化AI工作线程相关变量
        self.ai_worker_thread = None
        self.ai_worker = None
        
        # 初始化自动保存定时器
        from PyQt5.QtCore import QTimer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_current_record)
        self.auto_save_timer.setSingleShot(False)  # 重复触发
        self.auto_save_enabled = False  # 默认关闭自动保存
        
        # 初始化主题
        FluentTheme.init_theme()
        
        self.init_ui()
        self.setup_connections()
        self.setup_shortcuts()
        
    def set_window_icon(self):
        """设置窗口图标"""
        # 优先级顺序查找图标文件
        icon_paths = [
            "assets/app_icon.png",                 # 主应用图标
            "assets/icons/baize_icon_128x128.png", # 128x128 图标
            "assets/icons/baize_icon_64x64.png",   # 64x64 图标
            "assets/icons/baize_icon_48x48.png",   # 48x48 图标
            "assets/icons/baize_icon_32x32.png",   # 32x32 图标
            "assets/baize_logo_traditional.png",   # 备用大logo
            "assets/baize_logo_modern.png",        # 备用大logo
        ]
        
        icon_set = False
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        print(f"✅ 设置窗口图标: {icon_path}")
                        icon_set = True
                        break
                except Exception as e:
                    print(f"⚠️ 加载图标失败 {icon_path}: {e}")
                    continue
        
        if not icon_set:
            print("⚠️ 未找到图标文件，使用默认图标")

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("白泽")
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.resize(1500, 1000)
        
        # 先创建各个页面
        self.create_extraction_interface()
        self.create_gallery_interface()
        self.create_prompt_editor_interface()
        self.create_prompt_reverser_interface()
        self.create_settings_interface()
        
        # 再设置导航界面
        self.setup_navigation()
        
        # 显示默认页面
        self.stackedWidget.setCurrentWidget(self.extraction_interface)
        
    def setup_navigation(self):
        """设置导航界面"""
        # 信息提取页面
        self.addSubInterface(
            interface=self.extraction_interface,
            icon=FluentIcons.get_icon('extract'),
            text='信息提取',
            position=NavigationItemPosition.TOP
        )
        
        # 图片画廊页面
        self.addSubInterface(
            interface=self.gallery_interface,
            icon=FluentIcons.get_icon('gallery'),
            text='图片画廊',
            position=NavigationItemPosition.TOP
        )
        
        # 提示词修改页面
        self.addSubInterface(
            interface=self.prompt_editor_interface,
            icon=FluentIcons.get_icon('edit'),
            text='提示词修改',
            position=NavigationItemPosition.TOP
        )
        
        # 提示词反推页面
        self.addSubInterface(
            interface=self.prompt_reverser_interface,
            icon=FluentIcons.get_icon('magic'),
            text='提示词反推',
            position=NavigationItemPosition.TOP
        )
        
        # 设置页面
        self.addSubInterface(
            interface=self.settings_interface,
            icon=FluentIcons.get_icon('settings'),
            text='设置',
            position=NavigationItemPosition.BOTTOM
        )
        
        # 激活页面（始终显示，方便用户激活）
        self.addSubInterface(
            interface=self.create_activation_interface(),
            icon=FluentIcons.get_icon('key') if hasattr(FluentIcons, 'get_icon') else '🔑',
            text='软件激活',
            position=NavigationItemPosition.BOTTOM
        )
        
    def create_extraction_interface(self):
        """创建信息提取界面"""
        self.extraction_interface = QWidget()
        self.extraction_interface.setAcceptDrops(True)  # 使整个界面支持拖拽
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                     FluentSpacing.MD, FluentSpacing.MD)
        main_layout.setSpacing(FluentSpacing.SM)
        
        # 许可证状态栏
        self.create_license_status_bar(main_layout)
        
        # 主要内容布局
        layout = QHBoxLayout()
        layout.setSpacing(FluentSpacing.LG)
        
        # 左侧区域 - 图片信息展示
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(FluentSpacing.MD)
        left_widget.setLayout(left_layout)
        
        # 移除原来的拖拽区域组件，改为提示信息
        info_label = BodyLabel("🖼️ 将图片或文件夹拖拽到此界面的任意位置即可开始处理")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-size: 14px;
            padding: 20px;
            background-color: {FluentColors.get_color('bg_secondary')};
            border-radius: 12px;
            border: 2px dashed {FluentColors.get_color('border_primary')};
        """)
        left_layout.addWidget(info_label)
        
        # 图片信息组件
        self.image_info_widget = FluentImageInfoWidget()
        self.image_info_widget.setVisible(True)  # 确保可见
        self.image_info_widget.show()  # 强制显示
        print(f"图片信息组件创建: {self.image_info_widget}")
        print(f"图片信息组件初始可见性: {self.image_info_widget.isVisible()}")
        left_layout.addWidget(self.image_info_widget)
        
        # 右侧区域 - 历史记录
        self.history_widget = FluentHistoryWidget(self.data_manager)
        
        # 添加到布局
        layout.addWidget(left_widget, 3)  # 左侧占3份
        layout.addWidget(self.history_widget, 2)  # 右侧占2份
        
        # 将主要内容布局添加到主布局
        main_layout.addLayout(layout)
        
        self.extraction_interface.setLayout(main_layout)
        
        # 设置对象名称
        self.extraction_interface.setObjectName("extraction")
        
        # 创建拖拽蒙层
        self.drag_overlay = DragOverlay(self.extraction_interface)
        
        # 重写拖拽事件
        self.extraction_interface.dragEnterEvent = self.dragEnterEvent
        self.extraction_interface.dragLeaveEvent = self.dragLeaveEvent
        self.extraction_interface.dropEvent = self.dropEvent
        
        # 加载历史记录
        self.history_widget.load_history()
        
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 确保蒙层大小与界面同步
        if hasattr(self, 'drag_overlay') and hasattr(self, 'extraction_interface'):
            self.drag_overlay.resize(self.extraction_interface.size())
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有支持的文件格式或文件夹
            has_valid_items = False
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    import os
                    # 检查是否是文件夹或支持的图片格式
                    if os.path.isdir(file_path) or file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        has_valid_items = True
                        break
            
            if has_valid_items:
                event.accept()
                # 显示蒙层
                self.drag_overlay.resize(self.extraction_interface.size())
                self.drag_overlay.show()
            else:
                event.ignore()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 隐藏蒙层
        self.drag_overlay.hide()
        
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        import os
        files = []
        folders = []
        
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if os.path.isdir(file_path):
                    folders.append(file_path)
                elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    files.append(file_path)
        
        # 隐藏蒙层
        self.drag_overlay.hide()
        
        # 优先处理文件夹（批量处理）
        if folders:
            # 只处理第一个文件夹
            self.handle_folder_dropped(folders[0])
        elif files:
            self.handle_files_dropped(files)
        
        event.accept()
    
    def create_gallery_interface(self):
        """创建图片画廊界面"""
        self.gallery_interface = FluentGalleryWidget(self.data_manager)
        self.gallery_interface.record_selected.connect(self.on_gallery_record_selected)
        
        # 设置对象名称
        self.gallery_interface.setObjectName("gallery")
        
    def create_prompt_editor_interface(self):
        """创建提示词编辑界面"""
        self.prompt_editor_interface = FluentPromptEditorWidget()
        
        # 设置对象名称
        self.prompt_editor_interface.setObjectName("prompt_editor")
        
    def create_prompt_reverser_interface(self):
        """创建提示词反推界面"""
        self.prompt_reverser_interface = FluentPromptReverserWidget()
        
        # 设置对象名称
        self.prompt_reverser_interface.setObjectName("prompt_reverser")
        
    def create_settings_interface(self):
        """创建设置界面"""
        self.settings_interface = FluentSettingsWidget()
        
        # 设置对象名称
        self.settings_interface.setObjectName("settings")
        
    def create_activation_interface(self):
        """创建激活界面"""
        # 创建一个简单的激活状态显示界面
        activation_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                 FluentSpacing.LG, FluentSpacing.LG)
        
        # 激活状态卡片
        status_card = CardWidget()
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                       FluentSpacing.LG, FluentSpacing.LG)
        
        # 标题
        title_label = TitleLabel("软件激活")
        status_layout.addWidget(title_label)
        
        # 当前状态
        self.license_status_label = BodyLabel("检查中...")
        status_layout.addWidget(self.license_status_label)
        
        # 激活按钮
        activate_btn = PrimaryPushButton("激活软件")
        activate_btn.clicked.connect(self.show_activation_dialog)
        status_layout.addWidget(activate_btn)
        
        status_card.setLayout(status_layout)
        layout.addWidget(status_card)
        layout.addStretch()
        
        activation_widget.setLayout(layout)
        activation_widget.setObjectName("activation")
        
        return activation_widget
    
    def create_license_status_bar(self, parent_layout):
        """创建许可证状态栏"""
        self.license_status_card = CardWidget()
        self.license_status_card.setFixedHeight(60)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.SM, 
                                       FluentSpacing.MD, FluentSpacing.SM)
        
        # 状态图标和文本
        self.license_status_icon = BodyLabel("🔓")
        self.license_status_icon.setStyleSheet("font-size: 16px;")
        
        self.license_status_text = BodyLabel("检查许可证状态中...")
        self.license_status_text.setStyleSheet("font-weight: 500;")
        
        # 快速激活按钮
        self.quick_activate_btn = PrimaryPushButton("立即激活")
        self.quick_activate_btn.setFixedSize(80, 32)
        self.quick_activate_btn.clicked.connect(self.show_activation_dialog)
        
        # 布局
        status_layout.addWidget(self.license_status_icon)
        status_layout.addWidget(self.license_status_text)
        status_layout.addStretch()
        status_layout.addWidget(self.quick_activate_btn)
        
        self.license_status_card.setLayout(status_layout)
        parent_layout.addWidget(self.license_status_card)
        
    def setup_connections(self):
        """设置信号连接"""
        # 移除原来的拖拽区域信号连接
        # self.drop_area.filesDropped.connect(self.handle_files_dropped)
        # self.drop_area.folderDropped.connect(self.handle_folder_dropped)
        
        # 图片信息组件信号
        self.image_info_widget.save_btn.clicked.connect(self.save_record)
        self.image_info_widget.copy_info_btn.clicked.connect(self.copy_info)
        self.image_info_widget.share_html_btn.clicked.connect(self.share_as_html)
        self.image_info_widget.auto_tag_btn.clicked.connect(self.auto_tag_image)
        self.image_info_widget.edit_prompt_requested.connect(self.handle_edit_prompt_request)
        
        # 历史记录信号
        self.history_widget.record_selected.connect(self.load_from_history_record)
        
        # 监听用户输入变化，启动自动保存定时器
        self.image_info_widget.file_name_edit.textChanged.connect(self.on_user_input_changed)
        self.image_info_widget.tags_edit.textChanged.connect(self.on_user_input_changed)
        self.image_info_widget.notes_text.textChanged.connect(self.on_user_input_changed)
        
    def handle_files_dropped(self, files):
        """处理拖拽的文件"""
        if files:
            self.process_image(files[0])  # 处理第一个文件
            
    def handle_folder_dropped(self, folder_path):
        """处理拖拽的文件夹"""
        try:
            # 显示批量处理对话框
            from .fluent_batch_folder_dialog import FluentBatchFolderDialog
            
            dialog = FluentBatchFolderDialog(folder_path, self.data_manager, self)
            if dialog.exec_() == dialog.Accepted:
                # 刷新历史记录和画廊
                self.history_widget.load_history()
                self.gallery_interface.load_records()
                
                InfoBar.success(
                    title="批量处理完成",
                    content="文件夹中的图片已成功处理",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
        except Exception as e:
            print(f"处理文件夹时出错: {e}")
            InfoBar.error(
                title="处理失败",
                content=f"处理文件夹时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
    def process_image(self, file_path):
        """处理图片文件"""
        try:
            self.current_file_path = file_path
            
            # 读取图片信息
            image_info = self.image_reader.extract_info(file_path)
            
            # 显示图片信息
            self.image_info_widget.display_image_info(file_path, image_info)
            
            # 自动保存记录
            self.auto_save_record(file_path, image_info)
            
            # 启用自动保存功能
            self.auto_save_enabled = True
            print(f"[处理图片] 已为图片 {file_path} 启用自动保存功能")
            
            # 刷新历史记录和画廊
            self.history_widget.load_history()
            self.gallery_interface.load_records()
            
        except Exception as e:
            print(f"处理图片时出错: {e}")
            InfoBar.error(
                title="处理失败",
                content=f"处理图片时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
    def auto_save_record(self, file_path, image_info):
        """自动保存记录"""
        try:
            record_data = {
                'file_path': file_path,
                'custom_name': '',
                'tags': '',
                'notes': '',
            }
            
            if image_info:
                record_data.update(image_info)
            
            record_id = self.data_manager.save_record(record_data)
            
            if record_id:
                print(f"自动保存成功，记录ID: {record_id}")
            else:
                print("自动保存失败")
                
        except Exception as e:
            print(f"自动保存记录时出错: {e}")
            
    def save_record(self):
        """保存/更新记录"""
        if not self.current_file_path:
            InfoBar.warning(
                title="提示",
                content="请先选择一个图片文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
            
        try:
            # 获取用户输入的信息
            custom_name = self.image_info_widget.file_name_edit.text().strip()
            tags = self.image_info_widget.tags_edit.text().strip()
            notes = self.image_info_widget.notes_text.toPlainText().strip()
            
            # 重新读取图片信息
            image_info = self.image_reader.extract_info(self.current_file_path)
            
            record_data = {
                'file_path': self.current_file_path,
                'custom_name': custom_name,
                'tags': tags,
                'notes': notes,
            }
            
            if image_info:
                record_data.update(image_info)
            
            record_id = self.data_manager.save_record(record_data)
            
            if record_id:
                InfoBar.success(
                    title="保存成功",
                    content="记录保存成功！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                # 刷新历史记录和画廊
                self.history_widget.load_history()
                self.gallery_interface.load_records()
            else:
                InfoBar.error(
                    title="保存失败",
                    content="保存记录失败",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="保存失败",
                content=f"保存记录时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
    def copy_info(self):
        """复制信息到剪贴板"""
        try:
            info_text = []
            
            if self.current_file_path:
                info_text.append(f"文件路径: {self.current_file_path}")
                
            if self.image_info_widget.prompt_text.toPlainText():
                info_text.append(f"Prompt: {self.image_info_widget.prompt_text.toPlainText()}")
                
            if self.image_info_widget.neg_prompt_text.toPlainText():
                info_text.append(f"Negative Prompt: {self.image_info_widget.neg_prompt_text.toPlainText()}")
                
            if self.image_info_widget.model_edit.text():
                info_text.append(f"模型: {self.image_info_widget.model_edit.text()}")
                
            if self.image_info_widget.sampler_edit.text():
                info_text.append(f"采样器: {self.image_info_widget.sampler_edit.text()}")
                
            if self.image_info_widget.steps_edit.text():
                info_text.append(f"Steps: {self.image_info_widget.steps_edit.text()}")
                
            if self.image_info_widget.cfg_edit.text():
                info_text.append(f"CFG Scale: {self.image_info_widget.cfg_edit.text()}")
                
            if self.image_info_widget.seed_edit.text():
                info_text.append(f"Seed: {self.image_info_widget.seed_edit.text()}")
                
            if self.image_info_widget.lora_text.toPlainText():
                info_text.append(f"Lora信息: {self.image_info_widget.lora_text.toPlainText()}")
            
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(info_text))
            
            InfoBar.success(
                title="复制成功",
                content="信息已复制到剪贴板",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                title="复制失败",
                content=f"复制信息时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def share_as_html(self):
        """分享为HTML"""
        if not self.current_file_path:
            InfoBar.warning(
                title="提示",
                content="请先选择一个图片文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
            
        try:
            # 获取当前图片的记录数据
            record_id = self.data_manager.get_record_id_by_path(self.current_file_path)
            if not record_id:
                InfoBar.warning(
                    title="提示",
                    content="请先保存当前记录",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            
            record_data = self.data_manager.get_record_by_id(record_id)
            if not record_data:
                InfoBar.error(
                    title="错误",
                    content="无法获取记录数据",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # 获取用户自定义信息
            if hasattr(self.image_info_widget, 'file_name_edit'):
                record_data['custom_name'] = self.image_info_widget.file_name_edit.text()
            if hasattr(self.image_info_widget, 'tags_edit'):
                record_data['tags'] = self.image_info_widget.tags_edit.text()
            if hasattr(self.image_info_widget, 'notes_text'):
                record_data['notes'] = self.image_info_widget.notes_text.toPlainText()
            
            from PyQt5.QtWidgets import QFileDialog
            
            # 生成默认文件名
            file_name = record_data.get('custom_name') or record_data.get('file_name', '未命名图片')
            if '.' in file_name:
                file_name = file_name.rsplit('.', 1)[0]
            default_name = f"{file_name}_分享.html"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存HTML分享文件", default_name, 
                "HTML文件 (*.html);;所有文件 (*.*)"
            )
            
            if file_path:
                # 导出HTML
                success = self.html_exporter.export_to_html(record_data, file_path, include_image=True)
                
                if success:
                    InfoBar.success(
                        title="分享成功",
                        content=f"HTML分享文件已保存到: {file_path}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                    
                    # 询问是否打开文件
                    from PyQt5.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self, "打开文件", 
                        "是否现在打开HTML文件预览?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        import webbrowser
                        webbrowser.open(f"file:///{file_path.replace(chr(92), '/')}")
                else:
                    InfoBar.error(
                        title="分享失败",
                        content="生成HTML文件时出错",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                    
        except Exception as e:
            InfoBar.error(
                title="分享失败",
                content=f"生成HTML分享文件时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
    def export_data(self):
        """导出数据"""
        try:
            records = self.data_manager.get_all_records()
            
            if not records:
                InfoBar.info(
                    title="提示",
                    content="没有数据可导出",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
                
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出数据", "ai_image_data.json", 
                "JSON文件 (*.json);;所有文件 (*.*)"
            )
            
            if file_path:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                    
                InfoBar.success(
                    title="导出成功",
                    content=f"数据已导出到: {file_path}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="导出失败",
                content=f"导出数据时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def auto_tag_image(self):
        """AI自动打标签"""
        if not self.current_file_path:
            InfoBar.warning(
                title="提示",
                content="请先选择一个图片文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        
        if not self.ai_tagger:
            InfoBar.error(
                title="AI服务不可用",
                content="AI图像打标签器未正确初始化，请检查API配置",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        # 禁用按钮防止重复点击
        self.image_info_widget.auto_tag_btn.setEnabled(False)
        self.image_info_widget.auto_tag_btn.setText("🤖 分析中...")
        
        try:
            InfoBar.info(
                title="开始分析",
                content="正在使用AI分析图片内容，请稍候...",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            
            # 获取已存在的标签
            existing_tags = self.data_manager.get_all_unique_tags()
            print(f"获取到 {len(existing_tags)} 个已存在标签")
            
            # 创建工作线程
            self.ai_worker_thread = QThread()
            self.ai_worker = AITagWorker(self.ai_tagger, self.current_file_path, existing_tags)
            self.ai_worker.moveToThread(self.ai_worker_thread)
            
            # 连接信号
            self.ai_worker_thread.started.connect(self.ai_worker.run)
            self.ai_worker.finished.connect(self.handle_ai_tag_finished)
            self.ai_worker.finished.connect(self.ai_worker_thread.quit)
            self.ai_worker_thread.finished.connect(self.ai_worker_thread.deleteLater)
            
            # 启动线程
            self.ai_worker_thread.start()
            
        except Exception as e:
            InfoBar.error(
                title="分析错误",
                content=f"AI分析过程中出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
            print(f"AI分析异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 恢复按钮状态
            self.image_info_widget.auto_tag_btn.setEnabled(True)
            self.image_info_widget.auto_tag_btn.setText("🤖 AI自动打标签")
            
    def handle_ai_tag_finished(self, success, result):
        """处理AI标签分析完成后的信号"""
        # 恢复按钮状态
        self.image_info_widget.auto_tag_btn.setEnabled(True)
        self.image_info_widget.auto_tag_btn.setText("🤖 AI自动打标签")
        
        if success:
            # 获取生成的标签字符串
            tags_string = result.get('tags_string', '')
            tags_list = result.get('tags', [])
            ai_description = result.get('ai_analysis', {}).get('description', '')
            matching_result = result.get('matching_result', {})
            
            # 更新标签输入框
            if tags_string:
                current_tags = self.image_info_widget.tags_edit.text().strip()
                if current_tags:
                    # 如果已有标签，追加新标签
                    new_tags = f"{current_tags}, {tags_string}"
                else:
                    new_tags = tags_string
                
                self.image_info_widget.tags_edit.setText(new_tags)
                
                # 在备注中添加AI分析描述
                if ai_description:
                    current_notes = self.image_info_widget.notes_text.toPlainText().strip()
                    ai_note = f"AI分析: {ai_description}"
                    if current_notes:
                        new_notes = f"{current_notes}\n\n{ai_note}"
                    else:
                        new_notes = ai_note
                    self.image_info_widget.notes_text.setPlainText(new_notes)
            
            # AI打标完成后自动保存
            print("[AI打标] 开始自动保存标签到数据库...")  
            self.save_record()  # 调用现有的保存方法
            print("[AI打标] 自动保存完成")
            
            # 显示详细结果
            matched_count = len(matching_result.get('matched_tags', []))
            new_count = len(matching_result.get('new_tags', []))
            
            success_message = f"AI分析完成！生成了 {len(tags_list)} 个标签并已自动保存"
            if matched_count > 0 or new_count > 0:
                success_message += f"（匹配已有: {matched_count}, 新创建: {new_count}）"
            
            InfoBar.success(
                title="标签生成成功",
                content=success_message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
            
            print(f"AI生成标签: {tags_list}")
            print(f"匹配结果: 已有标签 {matched_count} 个，新标签 {new_count} 个")
            
        else:
            error_msg = result.get('error', '未知错误')
            InfoBar.error(
                title="分析失败",
                content=f"AI分析失败: {error_msg}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
            print(f"AI分析失败: {error_msg}")
            
    def load_from_history_record(self, record):
        """从历史记录加载"""
        try:
            print(f"主窗口接收到历史记录信号: {record.get('file_path', '未知')}")
            file_path = record.get('file_path', '')
            
            if not os.path.exists(file_path):
                InfoBar.warning(
                    title="文件不存在",
                    content="文件不存在，可能已被移动或删除",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
                
            # 切换到信息提取页面
            self.stackedWidget.setCurrentWidget(self.extraction_interface)
            
            self.current_file_path = file_path
            
            # 重新读取图片信息
            image_info = self.image_reader.extract_info(file_path)
            
            # 显示图片信息
            self.image_info_widget.display_image_info(file_path, image_info)
            
            # 加载用户自定义信息
            if hasattr(self.image_info_widget, 'file_name_edit'):
                self.image_info_widget.file_name_edit.setText(record.get('custom_name', ''))
            if hasattr(self.image_info_widget, 'tags_edit'):
                self.image_info_widget.tags_edit.setText(record.get('tags', ''))
            if hasattr(self.image_info_widget, 'notes_text'):
                self.image_info_widget.notes_text.setPlainText(record.get('notes', ''))
            
            # 启用自动保存功能
            self.auto_save_enabled = True
            print(f"[历史记录] 已为记录 {file_path} 启用自动保存功能")
            
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"加载历史记录时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
    def handle_edit_prompt_request(self, prompt_text, scene_name):
        """处理编辑提示词请求"""
        try:
            print(f"开始处理编辑提示词请求: {scene_name}")
            print(f"提示词内容: {prompt_text}")
            
            # 解析提示词（按逗号分割）
            prompts = [prompt.strip() for prompt in prompt_text.split(',') if prompt.strip()]
            print(f"解析后的提示词: {prompts}")
            
            # 切换到提示词编辑页面
            print("正在切换到提示词编辑页面...")
            self.stackedWidget.setCurrentWidget(self.prompt_editor_interface)
            
            # 确保组件可见
            self.prompt_editor_interface.setVisible(True)
            self.prompt_editor_interface.show()
            print(f"提示词编辑器可见性: {self.prompt_editor_interface.isVisible()}")
            
            # 先收起所有现有场景
            for editor_info in self.prompt_editor_interface.editors:
                accordion = editor_info['accordion']
                accordion.setExpanded(False)
            
            # 在提示词编辑器中添加新场景
            print(f"正在添加新场景: {scene_name}")
            editor_panel = self.prompt_editor_interface.add_editor(scene_name)
            
            # 设置英文提示词
            editor_panel.set_prompts(english_prompts=prompts)
            print("已设置提示词内容")
            
            # 只展开新添加的场景
            if self.prompt_editor_interface.editors:
                last_editor = self.prompt_editor_interface.editors[-1]
                accordion = last_editor['accordion']
                accordion.setExpanded(True)
                print("已展开新场景")
                
                # 确保新场景可见，滚动到该位置
                try:
                    self.prompt_editor_interface.ensureWidgetVisible(accordion)
                    print("已滚动到新场景位置")
                except Exception as scroll_error:
                    print(f"滚动到新场景时出错: {scroll_error}")
            
            print(f"成功导入提示词到场景: {scene_name}")
            
            # 显示成功提示
            InfoBar.success(
                title="提示词已导入",
                content=f"已将提示词导入到新场景：{scene_name}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
        except Exception as e:
            print(f"处理编辑提示词请求时出错: {e}")
            import traceback
            traceback.print_exc()
            InfoBar.error(
                title="导入失败",
                content=f"导入提示词时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def on_gallery_record_selected(self, record_data):
        """画廊记录选中事件"""
        print(f"画廊记录被选中: {record_data.get('file_path', '未知')}")
        
        # 切换到信息提取页面
        self.stackedWidget.setCurrentWidget(self.extraction_interface)
        print("已切换到信息提取页面")
        
        # 检查界面状态
        print(f"信息提取页面可见: {self.extraction_interface.isVisible()}")
        print(f"图片信息组件可见: {self.image_info_widget.isVisible()}")
        
        # 强制显示组件
        self.extraction_interface.setVisible(True)
        self.image_info_widget.setVisible(True)
        self.image_info_widget.show()
        
        # 加载选中的记录
        self.load_from_history_record(record_data)
        
        InfoBar.success(
            title="记录已加载",
            content=f"已加载记录：{os.path.basename(record_data.get('file_path', ''))}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def handle_new_file_from_instance(self, file_path):
        """处理来自其他实例的新文件"""
        if file_path and os.path.exists(file_path):
            print(f"[单实例] 接收到新文件: {file_path}")
            # 激活窗口到前台
            self.activateWindow()
            self.raise_()
            self.showNormal()
            # 处理图片
            self.process_image(file_path)
        else:
            # 空文件路径，只是激活窗口
            print(f"[单实例] 激活窗口")
            self.activateWindow()
            self.raise_()
            self.showNormal()
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 清理AI工作线程
            if self.ai_worker_thread and self.ai_worker_thread.isRunning():
                print("正在停止AI工作线程...")
                self.ai_worker_thread.quit()
                self.ai_worker_thread.wait(3000)  # 等待最多3秒
                if self.ai_worker_thread.isRunning():
                    self.ai_worker_thread.terminate()
                print("AI工作线程已停止")
            
            # 保存提示词编辑器数据
            if hasattr(self, 'prompt_editor_widget') and self.prompt_editor_widget:
                self.prompt_editor_widget.save_history_data()
                print("应用关闭时自动保存了提示词数据")
        except Exception as e:
            print(f"关闭时保存数据失败: {e}")
        
        event.accept()
    
    def setup_shortcuts(self):
        """设置快捷键"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+S 保存快捷键
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_record)
        print("设置Ctrl+S快捷键")
        
    def on_user_input_changed(self):
        """用户输入变化时的处理"""
        if not self.current_file_path:
            return  # 没有当前文件时不启动自动保存
            
        # 启用自动保存并重启定时器
        self.auto_save_enabled = True
        self.auto_save_timer.stop()  # 先停止当前定时器
        self.auto_save_timer.start(5000)  # 5秒后触发
        print("[自动保存] 检测到用户输入变化，将在5秒后自动保存")
        
    def auto_save_current_record(self):
        """自动保存当前记录"""
        if not self.auto_save_enabled or not self.current_file_path:
            return
            
        try:
            print("[自动保存] 开始自动保存当前记录...")
            
            # 获取用户输入的信息
            custom_name = self.image_info_widget.file_name_edit.text().strip()
            tags = self.image_info_widget.tags_edit.text().strip()
            notes = self.image_info_widget.notes_text.toPlainText().strip()
            
            # 重新读取图片信息
            image_info = self.image_reader.extract_info(self.current_file_path)
            
            record_data = {
                'file_path': self.current_file_path,
                'custom_name': custom_name,
                'tags': tags,
                'notes': notes,
            }
            
            if image_info:
                record_data.update(image_info)
            
            record_id = self.data_manager.save_record(record_data)
            
            if record_id:
                print(f"[自动保存] 自动保存成功，记录ID: {record_id}")
                # 显示静默的自动保存提示
                InfoBar.info(
                    title="自动保存",
                    content="记录已自动保存",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=1500,
                    parent=self
                )
                # 刷新历史记录和画廊
                self.history_widget.load_history()
                self.gallery_interface.load_records()
            else:
                print("[自动保存] 自动保存失败")
                
        except Exception as e:
            print(f"[自动保存] 自动保存记录时出错: {e}")
        
        # 停止定时器，等待下次用户输入变化
        self.auto_save_timer.stop()
    
    def set_license_status(self, is_valid, message, data):
        """设置许可证状态"""
        self.license_status = {
            "is_valid": is_valid,
            "message": message,
            "data": data
        }
        
        # 更新激活界面的状态标签
        if hasattr(self, 'license_status_label'):
            if is_valid:
                if data.get("trial", False):
                    remaining_days = data.get("remaining_days", 0)
                    self.license_status_label.setText(f"✅ 试用期 - 剩余 {remaining_days} 天")
                else:
                    self.license_status_label.setText("✅ 已激活 - 感谢您的支持！")
            else:
                self.license_status_label.setText(f"❌ {message}")
        
        # 更新顶部状态栏
        if hasattr(self, 'license_status_card'):
            if is_valid and not data.get("trial", False):
                # 软件已激活且非试用期时，隐藏状态栏以节省空间
                self.license_status_card.setVisible(False)
            else:
                # 试用期或未激活时，显示状态栏
                self.license_status_card.setVisible(True)
                
                if hasattr(self, 'license_status_text') and hasattr(self, 'license_status_icon'):
                    if is_valid:
                        if data.get("trial", False):
                            remaining_days = data.get("remaining_days", 0)
                            self.license_status_icon.setText("⏰")
                            self.license_status_text.setText(f"试用期剩余 {remaining_days} 天")
                            self.license_status_card.setStyleSheet("background-color: rgba(255, 193, 7, 0.1);")
                            self.quick_activate_btn.setVisible(True)
                            self.quick_activate_btn.setText("立即激活")
                    else:
                        self.license_status_icon.setText("❌")
                        self.license_status_text.setText(message)
                        self.license_status_card.setStyleSheet("background-color: rgba(255, 99, 71, 0.1);")
                        self.quick_activate_btn.setVisible(True)
                        self.quick_activate_btn.setText("立即激活")
        
        # 更新导航栏
        self.update_navigation_for_activation()
    
    def show_activation_dialog(self):
        """显示激活对话框"""
        dialog = FluentActivationDialog(self)
        dialog.activation_completed.connect(self.on_activation_completed)
        dialog.exec_()
    
    def on_activation_completed(self, success, message):
        """激活完成回调"""
        if success:
            # 重新检查许可证状态
            is_valid, msg, data = self.license_manager.check_license_validity()
            self.set_license_status(is_valid, msg, data)
            
            InfoBar.success(
                title="激活成功",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.error(
                title="激活失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def update_navigation_for_activation(self):
        """更新导航栏以反映激活状态"""
        # 这里可以添加代码来移除或更新激活相关的导航项
        # 具体实现取决于PyQt-Fluent-Widgets的API
        pass
    
    def check_feature_access(self, feature_name):
        """检查功能访问权限"""
        if not self.license_status.get("is_valid", False):
            InfoBar.warning(
                title="功能受限",
                content=f"{feature_name}需要激活软件后才能使用",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return False
        return True


def main():
    """主函数"""
    app = QApplication([])
    
    # 显示启动画面（可选）
    # splash = SplashScreen(":/images/splash.png", app)
    # splash.show()
    
    window = FluentMainWindow()
    window.show()
    
    # 关闭启动画面
    # splash.finish(window)
    
    app.exec_()


if __name__ == "__main__":
    main() 