#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白泽AI - Fluent Design 启动画面
"""

import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QThread, QRect
from PyQt5.QtGui import QPixmap, QFont, QPainter, QBrush, QColor, QPainterPath, QLinearGradient, QIcon

from qfluentwidgets import IndeterminateProgressBar, FluentIcon
from .fluent_styles import FluentColors, FluentSpacing


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持PyInstaller打包后的路径"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 在开发环境下，使用脚本文件所在目录的上级目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


class BaizeSplashScreen(QWidget):
    """白泽AI启动画面"""
    
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 400)
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.XL, FluentSpacing.XL, 
                                      FluentSpacing.XL, FluentSpacing.XL)
        main_layout.setSpacing(FluentSpacing.LG)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Logo区域
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Logo图片
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(180, 180)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        
        # 尝试加载logo图片
        self.load_logo()
        
        logo_layout.addWidget(self.logo_label)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        title_layout.setSpacing(FluentSpacing.SM)
        
        # 主标题
        self.title_label = QLabel("白泽AI")
        title_font = QFont("Microsoft YaHei", 32, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                background: transparent;
                border: none;
            }}
        """)
        
        # 副标题
        self.subtitle_label = QLabel("智能图片信息提取工具")
        subtitle_font = QFont("Microsoft YaHei", 14)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: #E0E0E0;
                background: transparent;
                border: none;
            }}
        """)
        
        # 版本信息
        self.version_label = QLabel("v1.0.0")
        version_font = QFont("Microsoft YaHei", 10)
        self.version_label.setFont(version_font)
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet(f"""
            QLabel {{
                color: #A0A0A0;
                background: transparent;
                border: none;
            }}
        """)
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        title_layout.addWidget(self.version_label)
        
        # 进度条区域
        progress_layout = QVBoxLayout()
        progress_layout.setAlignment(Qt.AlignCenter)
        progress_layout.setSpacing(FluentSpacing.SM)
        
        # 状态文本
        self.status_label = QLabel("正在启动...")
        status_font = QFont("Microsoft YaHei", 10)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: #C0C0C0;
                background: transparent;
                border: none;
            }}
        """)
        
        # 进度条
        self.progress_bar = IndeterminateProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            IndeterminateProgressBar {
                border: none;
                border-radius: 2px;
                background-color: rgba(255, 255, 255, 0.2);
            }
            IndeterminateProgressBar::chunk {
                border-radius: 2px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4FC3F7, stop: 1 #29B6F6);
            }
        """)
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        
        # 添加到主布局
        main_layout.addLayout(logo_layout)
        main_layout.addLayout(title_layout)
        main_layout.addStretch()
        main_layout.addLayout(progress_layout)
        
        self.setLayout(main_layout)
        
    def load_logo(self):
        """加载logo图片"""
        # 优先级顺序查找logo文件
        logo_paths = [
            "assets/baize_logo_modern.png",
            "assets/baize_logo_traditional.png", 
            "assets/baize_logo_tech.png",
            "assets/baize_logo.png",          # 实际存在的logo文件
            "assets/baize_icon.png",          # 实际存在的icon文件
            "assets/app_icon.png",            # 应用图标
        ]
        
        logo_loaded = False
        for relative_path in logo_paths:
            logo_path = get_resource_path(relative_path)
            print(f"尝试加载Logo: {logo_path}")
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    # 缩放到合适尺寸
                    scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(scaled_pixmap)
                    logo_loaded = True
                    print(f"✅ 成功加载Logo: {logo_path}")
                    break
                else:
                    print(f"❌ 图片加载失败（pixmap为空）: {logo_path}")
            else:
                print(f"❌ 文件不存在: {logo_path}")
        
        if not logo_loaded:
            # 如果没有找到logo，显示默认的白泽图标
            self.logo_label.setText("🐉")
            self.logo_label.setStyleSheet("""
                QLabel {
                    font-size: 96px;
                    color: #4FC3F7;
                    border: none;
                    background: transparent;
                }
            """)
            print("⚠️ 未找到Logo文件，使用默认图标")
    
    def setup_animations(self):
        """设置动画效果"""
        # Logo渐入动画
        self.logo_opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.logo_opacity_animation.setDuration(800)
        self.logo_opacity_animation.setStartValue(0.0)
        self.logo_opacity_animation.setEndValue(1.0)
        self.logo_opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def paintEvent(self, event):
        """自定义绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角矩形路径
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(45, 55, 72))      # 深蓝灰
        gradient.setColorAt(0.5, QColor(55, 65, 82))    # 中蓝灰
        gradient.setColorAt(1, QColor(30, 41, 59))      # 更深蓝灰
        
        # 绘制背景
        painter.fillPath(path, QBrush(gradient))
        
        # 添加光晕效果
        glow_gradient = QLinearGradient(0, 0, self.width(), 0)
        glow_gradient.setColorAt(0, QColor(79, 195, 247, 20))   # 淡蓝色光晕
        glow_gradient.setColorAt(0.5, QColor(79, 195, 247, 40))
        glow_gradient.setColorAt(1, QColor(79, 195, 247, 20))
        
        glow_path = QPainterPath()
        glow_path.addRoundedRect(2, 2, self.width()-4, self.height()-4, 18, 18)
        painter.fillPath(glow_path, QBrush(glow_gradient))
        
        super().paintEvent(event)
    
    def show_splash(self):
        """显示启动画面"""
        # 居中显示
        self.move_to_center()
        self.show()
        self.raise_()
        self.activateWindow()
        
        self.logo_opacity_animation.start()
        
        # 启动进度条
        self.progress_bar.start()
        
        # 模拟加载过程
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.update_loading_status)
        self.load_timer.start(800)  # 每800ms更新一次状态
        
        self.loading_step = 0
        self.loading_messages = [
            "正在启动...",
            "加载核心模块...",
            "初始化AI引擎...",
            "准备用户界面...",
            "启动完成！"
        ]
    
    def move_to_center(self):
        """将窗口移动到屏幕中央"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def update_loading_status(self):
        """更新加载状态"""
        if self.loading_step < len(self.loading_messages):
            self.status_label.setText(self.loading_messages[self.loading_step])
            self.loading_step += 1
        else:
            # 加载完成
            self.load_timer.stop()
            self.progress_bar.stop()
            
            # 延迟一点时间后关闭
            QTimer.singleShot(1000, self.fade_out)
    
    def fade_out(self):
        """淡出动画"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.finished.connect(self.on_fade_finished)
        self.fade_animation.start()
    
    def on_fade_finished(self):
        """淡出完成"""
        self.finished.emit()
        self.close()
    
    def mousePressEvent(self, event):
        """点击跳过启动画面"""
        if event.button() == Qt.LeftButton:
            self.fade_out()


# 便利函数
def show_splash_screen(parent=None):
    """显示启动画面的便利函数"""
    splash = BaizeSplashScreen(parent)
    splash.show_splash()
    return splash 