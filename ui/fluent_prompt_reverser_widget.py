#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 提示词反推组件
"""

import os
import json
from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QTextEdit, QPushButton, QLineEdit, QComboBox,
                            QGroupBox, QProgressBar, QSplitter, QFrame, QScrollArea,
                            QFileDialog, QCheckBox, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QSettings
from PyQt5.QtGui import QFont, QPixmap, QIcon

from qfluentwidgets import (CardWidget, BodyLabel, CaptionLabel, PrimaryPushButton,
                           PushButton, LineEdit, ComboBox, TextEdit, InfoBar, 
                           InfoBarPosition, ProgressBar, SmoothScrollArea,
                           CheckBox, SpinBox, FlowLayout, setTheme, Theme)

from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing
from .fluent_drop_area import FluentDropArea
from core.prompt_reverser import PromptReverser


class ApiTestWorker(QThread):
    """API测试工作线程"""
    
    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(bool, str)  # 完成信号 (成功, 消息)
    error = pyqtSignal(str)  # 错误信息
    
    def __init__(self, api_key, model, base_url):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
    def run(self):
        try:
            from core.prompt_reverser import PromptReverser
            
            self.progress.emit("正在创建API客户端...")
            reverser = PromptReverser(api_key=self.api_key, model=self.model, base_url=self.base_url)
            
            self.progress.emit("正在测试API连接...")
            success, msg = reverser.test_api_connection()
            
            if success:
                self.finished.emit(True, msg)
            else:
                self.finished.emit(False, msg)
                
        except Exception as e:
            self.error.emit(f"测试异常: {str(e)}")


class PromptReverseWorker(QThread):
    """提示词反推工作线程"""
    
    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(bool, dict)  # 完成信号 (成功, 结果)
    error = pyqtSignal(str)  # 错误信息
    
    def __init__(self, image_path, api_key, model, base_url=None):
        super().__init__()
        self.image_path = image_path
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
    def run(self):
        try:
            self.progress.emit("正在初始化API连接...")
            
            # 创建提示词反推器
            reverser = PromptReverser(api_key=self.api_key, model=self.model, base_url=self.base_url)
            
            # 测试连接 - 添加更详细的进度信息
            self.progress.emit(f"正在测试API连接 (模型: {self.model})...")
            
            # 使用QTimer来避免UI阻塞
            import time
            start_time = time.time()
            
            success, msg = reverser.test_api_connection()
            
            elapsed_time = time.time() - start_time
            
            if not success:
                self.error.emit(f"API连接测试失败: {msg}")
                return
            
            self.progress.emit(f"API连接成功 ({elapsed_time:.1f}秒)")
            
            # 分析图片
            self.progress.emit("正在分析图片...")
            success, result = reverser.analyze_image(self.image_path)
            
            if success:
                self.progress.emit("分析完成！")
                self.finished.emit(True, result)
            else:
                self.error.emit(result.get('error', '未知错误'))
                
        except Exception as e:
            self.error.emit(f"处理过程出错: {str(e)}")


class FluentSettingsCard(CardWidget):
    """Fluent Design 设置卡片"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.init_ui(title)
        
    def init_ui(self, title):
        self.setFixedHeight(120)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD,
                                 FluentSpacing.MD, FluentSpacing.MD)
        layout.setSpacing(FluentSpacing.SM)
        
        # 标题
        title_label = BodyLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        layout.addWidget(title_label)
        
        # 内容区域
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(FluentSpacing.SM)
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)


class FluentResultCard(CardWidget):
    """Fluent Design 结果展示卡片"""
    
    copy_clicked = pyqtSignal(str, str)  # (类型, 内容)
    
    def __init__(self, title, content_zh, content_en, card_type="sd", parent=None):
        super().__init__(parent)
        self.title = title
        self.content_zh = content_zh
        self.content_en = content_en
        self.card_type = card_type
        self.current_lang = "zh"  # 默认显示中文
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD,
                                 FluentSpacing.MD, FluentSpacing.MD)
        layout.setSpacing(FluentSpacing.SM)
        
        # 标题栏
        header_layout = QHBoxLayout()
        header_layout.setSpacing(FluentSpacing.SM)
        
        title_label = BodyLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                font-size: 16px;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 语言切换按钮
        self.lang_btn = PushButton("中/EN")
        self.lang_btn.setFixedSize(50, 28)
        self.lang_btn.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.lang_btn)
        
        # 复制按钮
        self.copy_btn = PushButton("复制")
        self.copy_btn.setFixedSize(60, 28)
        self.copy_btn.clicked.connect(self.copy_current_content)
        header_layout.addWidget(self.copy_btn)
        
        layout.addLayout(header_layout)
        
        # 内容区域
        self.content_edit = TextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setFixedHeight(120)
        self.update_content()
        layout.addWidget(self.content_edit)
        
        self.setLayout(layout)
        
    def toggle_language(self):
        """切换语言显示"""
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self.update_content()
        
    def update_content(self):
        """更新显示内容"""
        if self.current_lang == "zh":
            self.content_edit.setPlainText(self.content_zh)
            self.lang_btn.setText("EN")
        else:
            self.content_edit.setPlainText(self.content_en)
            self.lang_btn.setText("中")
            
    def copy_current_content(self):
        """复制当前显示的内容"""
        current_content = self.content_zh if self.current_lang == "zh" else self.content_en
        self.copy_clicked.emit(self.card_type, current_content)


class FluentPromptReverserWidget(QWidget):
    """Fluent Design 提示词反推组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.worker = None
        self.api_test_worker = None  # 添加API测试工作线程
        self.settings = QSettings("PicTool", "PromptReverser")
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD,
                                      FluentSpacing.MD, FluentSpacing.MD)
        main_layout.setSpacing(FluentSpacing.LG)
        
        # 左侧面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # 右侧结果面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)
        
        self.setLayout(main_layout)
        
    def create_left_panel(self):
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(FluentSpacing.MD)
        
        # 拖拽区域
        self.drop_area = FluentDropArea()
        self.drop_area.filesDropped.connect(self.handle_files_dropped)
        # 使用FluentDropArea的默认高度，不再强制设置
        layout.addWidget(self.drop_area)
        
        # 当前图片信息
        self.image_info_card = CardWidget()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD,
                                      FluentSpacing.MD, FluentSpacing.MD)
        
        self.image_label = QLabel("请拖入图片文件")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(150)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {FluentColors.get_color('border_secondary')};
                border-radius: 8px;
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_tertiary')};
                font-size: 14px;
            }}
        """)
        info_layout.addWidget(self.image_label)
        
        self.file_name_label = CaptionLabel("")
        info_layout.addWidget(self.file_name_label)
        
        self.image_info_card.setLayout(info_layout)
        layout.addWidget(self.image_info_card)
        
        # API设置
        api_card = FluentSettingsCard("API设置")
        api_card.setFixedHeight(160)  # 增加高度以容纳更多内容
        
        # 创建垂直布局用于多行设置
        api_content_layout = QVBoxLayout()
        api_content_layout.setSpacing(FluentSpacing.SM)
        
        # API Key输入
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = LineEdit()
        self.api_key_edit.setPlaceholderText("请输入API Key")
        self.api_key_edit.setEchoMode(LineEdit.Password)
        self.api_key_edit.setText("sk-CnEoNNdwU8KeJfIoEg6rcNeLeO5XbF3HafEMckZkuZXvKSGS")  # 设置默认值
        api_key_layout.addWidget(self.api_key_edit)
        api_content_layout.addLayout(api_key_layout)
        
        # Base URL输入
        base_url_layout = QHBoxLayout()
        base_url_layout.addWidget(QLabel("Base URL:"))
        self.base_url_edit = LineEdit()
        self.base_url_edit.setPlaceholderText("API基础URL")
        self.base_url_edit.setText("https://api.ssopen.top/v1")  # 设置默认值
        base_url_layout.addWidget(self.base_url_edit)
        api_content_layout.addLayout(base_url_layout)
        
        # 将垂直布局添加到卡片的内容布局中
        api_card.content_layout.addLayout(api_content_layout)
        
        layout.addWidget(api_card)
        
        # 模型设置
        model_card = FluentSettingsCard("模型设置")
        
        self.model_combo = ComboBox()
        self.model_combo.addItems([
            "gpt-4o-mini",
            "gpt-4o", 
            "gpt-4-vision-preview",
            "gpt-4-turbo"
        ])
        # 添加模型切换处理
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        
        model_card.content_layout.addWidget(QLabel("模型:"))
        model_card.content_layout.addWidget(self.model_combo)
        
        # 添加API测试按钮
        self.test_api_btn = PushButton("测试API")
        self.test_api_btn.setFixedSize(80, 32)
        self.test_api_btn.clicked.connect(self.test_api_connection)
        model_card.content_layout.addWidget(self.test_api_btn)
        
        layout.addWidget(model_card)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(FluentSpacing.SM)
        
        self.analyze_btn = PrimaryPushButton("分析图片")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.analyze_btn)
        
        self.select_file_btn = PushButton("选择文件")
        self.select_file_btn.clicked.connect(self.select_image_file)
        button_layout.addWidget(self.select_file_btn)
        
        layout.addLayout(button_layout)
        
        # 进度显示
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = CaptionLabel("")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def create_right_panel(self):
        """创建右侧结果面板"""
        scroll_area = SmoothScrollArea()
        scroll_widget = QWidget()
        
        self.results_layout = QVBoxLayout()
        self.results_layout.setSpacing(FluentSpacing.MD)
        
        # 默认提示
        self.empty_label = QLabel("分析完成后，结果将在这里显示")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_tertiary')};
                font-size: 16px;
                padding: 60px;
            }}
        """)
        self.results_layout.addWidget(self.empty_label)
        
        self.results_layout.addStretch()
        
        scroll_widget.setLayout(self.results_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        return scroll_area
        
    def handle_files_dropped(self, files):
        """处理拖拽的文件"""
        if files:
            self.load_image(files[0])
            
    def select_image_file(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, image_path):
        """加载图片"""
        try:
            if not os.path.exists(image_path):
                self.show_error("文件不存在")
                return
                
            self.current_image_path = image_path
            
            # 显示图片预览
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.image_label.size(), 
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet(f"""
                    QLabel {{
                        border: 2px solid {FluentColors.get_color('accent')};
                        border-radius: 8px;
                        background-color: {FluentColors.get_color('bg_primary')};
                    }}
                """)
            
            # 显示文件名
            file_name = Path(image_path).name
            if len(file_name) > 30:
                file_name = file_name[:27] + "..."
            self.file_name_label.setText(file_name)
            
            # 启用分析按钮
            self.analyze_btn.setEnabled(True)
            self.status_label.setText("图片已加载，可以开始分析")
            
        except Exception as e:
            self.show_error(f"加载图片失败: {str(e)}")
            
    def start_analysis(self):
        """开始分析"""
        if not self.current_image_path:
            self.show_error("请先选择图片")
            return
            
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            self.show_error("请输入API Key")
            return
            
        base_url = self.base_url_edit.text().strip()
        if not base_url:
            self.show_error("请输入Base URL")
            return
            
        model = self.model_combo.currentText()
        
        # 保存设置
        self.save_settings()
        
        # 开始分析
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 创建工作线程
        self.worker = PromptReverseWorker(self.current_image_path, api_key, model, base_url)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()
        
    def update_progress(self, message):
        """更新进度"""
        self.status_label.setText(message)
        
    def on_analysis_finished(self, success, result):
        """分析完成"""
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.display_results(result)
            self.status_label.setText("分析完成！")
            self.show_success("提示词反推完成")
        else:
            self.show_error("分析失败")
            
    def on_analysis_error(self, error_msg):
        """分析错误"""
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("分析失败")
        self.show_error(error_msg)
        
    def display_results(self, result_data):
        """显示分析结果"""
        # 清除之前的结果
        self.clear_results()
        
        prompts = result_data.get("prompts", {})
        usage = result_data.get("usage", {})
        
        # 添加统计信息
        stats_card = CardWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD,
                                       FluentSpacing.MD, FluentSpacing.MD)
        
        stats_title = BodyLabel("分析统计")
        stats_title.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        stats_layout.addWidget(stats_title)
        
        stats_text = f"""模型: {result_data.get('model', 'unknown')}
Token使用: {usage.get('total_tokens', 0)} (输入: {usage.get('prompt_tokens', 0)}, 输出: {usage.get('completion_tokens', 0)})"""
        
        stats_label = CaptionLabel(stats_text)
        stats_layout.addWidget(stats_label)
        
        stats_card.setLayout(stats_layout)
        self.results_layout.addWidget(stats_card)
        
        # SD提示词
        sd_data = prompts.get("sd", {})
        if sd_data:
            # 正向提示词
            positive_data = sd_data.get("positive", {})
            positive_card = FluentResultCard(
                "🎨 Stable Diffusion - 正向提示词",
                positive_data.get("zh", ""),
                positive_data.get("en", ""),
                "sd_positive"
            )
            positive_card.copy_clicked.connect(self.copy_to_clipboard)
            self.results_layout.addWidget(positive_card)
            
            # 负向提示词
            negative_data = sd_data.get("negative", {})
            negative_card = FluentResultCard(
                "🚫 Stable Diffusion - 负向提示词", 
                negative_data.get("zh", ""),
                negative_data.get("en", ""),
                "sd_negative"
            )
            negative_card.copy_clicked.connect(self.copy_to_clipboard)
            self.results_layout.addWidget(negative_card)
            
        # ComfyUI提示词
        comfyui_data = prompts.get("comfyui", {})
        if comfyui_data:
            # CLIP提示词
            clip_data = comfyui_data.get("clip", {})
            clip_card = FluentResultCard(
                "📎 ComfyUI - CLIP提示词",
                clip_data.get("zh", ""),
                clip_data.get("en", ""),
                "comfyui_clip"
            )
            clip_card.copy_clicked.connect(self.copy_to_clipboard)
            self.results_layout.addWidget(clip_card)
            
            # T5提示词
            t5_data = comfyui_data.get("t5", {})
            t5_card = FluentResultCard(
                "🔤 ComfyUI - T5提示词",
                t5_data.get("zh", ""),
                t5_data.get("en", ""),
                "comfyui_t5"
            )
            t5_card.copy_clicked.connect(self.copy_to_clipboard)
            self.results_layout.addWidget(t5_card)
            
            # 附加信息
            style_data = comfyui_data.get("style", {})
            extra_info_zh = f"""CLIP权重: {comfyui_data.get('clip_weight', 0.8)}
风格分类: {style_data.get('zh', '未指定')}"""
            extra_info_en = f"""CLIP Weight: {comfyui_data.get('clip_weight', 0.8)}
Style Category: {style_data.get('en', 'Not specified')}"""
            
            # 创建附加信息卡片（也支持语言切换）
            extra_card = FluentResultCard(
                "⚙️ ComfyUI - 附加设置",
                extra_info_zh,
                extra_info_en,
                "comfyui_extra"
            )
            extra_card.copy_clicked.connect(self.copy_to_clipboard)
            self.results_layout.addWidget(extra_card)
        
        # 操作按钮
        action_layout = QHBoxLayout() 
        action_layout.setSpacing(FluentSpacing.SM)
        
        export_btn = PushButton("导出为文本")
        export_btn.clicked.connect(lambda: self.export_results(result_data))
        action_layout.addWidget(export_btn)
        
        action_layout.addStretch()
        
        self.results_layout.addLayout(action_layout)
        
        # 移除空状态标签
        if self.empty_label:
            self.empty_label.setVisible(False)
            
    def clear_results(self):
        """清除结果显示"""
        # 清除所有结果组件
        for i in reversed(range(self.results_layout.count())):
            item = self.results_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget and widget != self.empty_label:
                    widget.deleteLater()
                    
        # 显示空状态
        if self.empty_label:
            self.empty_label.setVisible(True)
            
    def copy_to_clipboard(self, prompt_type, content):
        """复制到剪贴板"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            self.show_success(f"已复制{prompt_type}到剪贴板")
        except Exception as e:
            self.show_error(f"复制失败: {str(e)}")
            
    def export_results(self, result_data):
        """导出结果"""
        try:
            from core.prompt_reverser import PromptReverser
            reverser = PromptReverser()
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出提示词结果",
                f"{Path(self.current_image_path).stem}_prompts.txt",
                "文本文件 (*.txt)"
            )
            
            if file_path:
                reverser.export_prompts_to_text(result_data, file_path)
                self.show_success(f"结果已导出到: {file_path}")
                
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")
            
    def save_settings(self):
        """保存设置"""
        self.settings.setValue("api_key", self.api_key_edit.text())
        self.settings.setValue("base_url", self.base_url_edit.text())
        self.settings.setValue("model", self.model_combo.currentText())
        
    def load_settings(self):
        """加载设置"""
        api_key = self.settings.value("api_key", "sk-CnEoNNdwU8KeJfIoEg6rcNeLeO5XbF3HafEMckZkuZXvKSGS")
        base_url = self.settings.value("base_url", "https://api.ssopen.top/v1")
        model = self.settings.value("model", "gpt-4o-mini")
        
        self.api_key_edit.setText(api_key)
        self.base_url_edit.setText(base_url)
        
        # 设置模型选择
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
            
    def show_success(self, message):
        """显示成功消息"""
        InfoBar.success(
            title="成功",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
    def show_error(self, message):
        """显示错误消息"""
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def on_model_changed(self):
        """模型切换处理"""
        current_model = self.model_combo.currentText()
        print(f"[UI] 模型切换到: {current_model}")
        
        # 重置测试API按钮状态
        self.test_api_btn.setEnabled(True)
        self.test_api_btn.setText("测试API")
        
        self.status_label.setText(f"已切换到模型: {current_model}")
        # 保存设置
        self.save_settings()
        print(f"[UI] 模型切换完成，设置已保存")

    def test_api_connection(self):
        """测试API连接"""
        print(f"[UI] 开始API连接测试...")
        
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            print(f"[UI] API Key为空")
            self.show_error("请先输入API Key")
            return
            
        base_url = self.base_url_edit.text().strip()
        if not base_url:
            print(f"[UI] Base URL为空")
            self.show_error("请先输入Base URL")
            return
            
        model = self.model_combo.currentText()
        print(f"[UI] 测试参数 - 模型: {model}, Base URL: {base_url}")
        
        # 停止之前的测试线程（如果存在）
        if self.api_test_worker and self.api_test_worker.isRunning():
            print(f"[UI] 停止之前的测试线程...")
            self.api_test_worker.terminate()
            self.api_test_worker.wait()
        
        # 禁用测试按钮防止重复点击
        self.test_api_btn.setEnabled(False)
        self.test_api_btn.setText("测试中...")
        self.status_label.setText(f"正在测试API连接 (模型: {model})...")
        
        try:
            print(f"[UI] 创建API测试工作线程...")
            # 创建API测试工作线程
            self.api_test_worker = ApiTestWorker(api_key, model, base_url)
            self.api_test_worker.progress.connect(self.update_test_progress)
            self.api_test_worker.finished.connect(self.on_api_test_finished)
            self.api_test_worker.error.connect(self.on_api_test_error)
            
            print(f"[UI] 启动API测试工作线程...")
            self.api_test_worker.start()
            
        except Exception as e:
            print(f"[UI] 创建测试线程异常: {str(e)}")
            self.on_api_test_error(f"创建测试线程失败: {str(e)}")
    
    def update_test_progress(self, message):
        """更新测试进度"""
        print(f"[UI] 测试进度: {message}")
        self.status_label.setText(message)
    
    def on_api_test_finished(self, success, message):
        """API测试完成"""
        print(f"[UI] API测试完成: success={success}, message={message}")
        
        # 恢复测试按钮
        self.test_api_btn.setEnabled(True)
        self.test_api_btn.setText("测试API")
        
        if success:
            print(f"[UI] 测试成功，显示成功消息")
            self.show_success(message)
            self.status_label.setText(message)
        else:
            print(f"[UI] 测试失败，显示错误消息")
            self.show_error(message)
            self.status_label.setText(f"API测试失败: {message}")
    
    def on_api_test_error(self, error_msg):
        """API测试错误"""
        print(f"[UI] API测试错误: {error_msg}")
        
        # 恢复测试按钮
        self.test_api_btn.setEnabled(True)
        self.test_api_btn.setText("测试API")
        
        self.show_error(error_msg)
        self.status_label.setText(f"API测试错误: {error_msg}") 