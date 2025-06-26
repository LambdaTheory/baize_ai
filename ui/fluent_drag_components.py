#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拖拽相关组件
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QFont, QLinearGradient


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
        painter.drawText(subtitle_rect, Qt.AlignCenter, "支持文件夹或从浏览器拖拽图片")
        
        # 底部装饰点
        dot_pen = QPen(QColor(200, 200, 200, 150))
        painter.setPen(dot_pen)
        painter.setBrush(QBrush(QColor(200, 200, 200, 150)))
        
        # 装饰点位置：副标题下方40px
        dots_y = subtitle_y + 60
        
        for i in range(5):
            dot_x = center_x - 40 + i * 20
            painter.drawEllipse(dot_x - 2, dots_y - 2, 4, 4) 