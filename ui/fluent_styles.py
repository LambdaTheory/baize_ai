#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design UI样式管理器
使用PyQt-Fluent-Widgets组件库
"""

from qfluentwidgets import (FluentIcon, setTheme, Theme, setThemeColor,
                           qconfig, QConfig, ConfigItem, ColorConfigItem)
from PyQt5.QtGui import QColor


class FluentTheme:
    """Fluent主题管理器"""
    
    # 定义主题色
    PRIMARY_COLOR = QColor(79, 70, 229)  # 蓝紫色
    SECONDARY_COLOR = QColor(156, 163, 175)  # 灰色
    SUCCESS_COLOR = QColor(34, 197, 94)  # 绿色
    WARNING_COLOR = QColor(251, 191, 36)  # 黄色
    ERROR_COLOR = QColor(239, 68, 68)  # 红色
    
    @staticmethod
    def init_theme():
        """初始化主题"""
        # 设置主题色
        setThemeColor(FluentTheme.PRIMARY_COLOR)
        # 默认使用浅色主题
        setTheme(Theme.LIGHT)
    
    @staticmethod
    def get_card_style():
        """获取卡片样式"""
        return """
            QWidget {
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 16px;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(79, 70, 229, 0.2);
            }
        """
    
    @staticmethod
    def get_glass_effect_style():
        """获取毛玻璃效果样式"""
        return """
            QWidget {
                background-color: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
            }
        """


class FluentIcons:
    """Fluent图标管理器"""
    
    # 常用图标映射
    ICONS = {
        'refresh': FluentIcon.SYNC,
        'image': FluentIcon.PHOTO,
        'save': FluentIcon.SAVE,
        'copy': FluentIcon.COPY,
        'export': FluentIcon.SHARE,
        'delete': FluentIcon.DELETE,
        'folder': FluentIcon.FOLDER,
        'search': FluentIcon.SEARCH,
        'filter': FluentIcon.FILTER,
        'settings': FluentIcon.SETTING,
        'info': FluentIcon.INFO,
        'tag': FluentIcon.TAG,
        'time': FluentIcon.HISTORY,
        'model': FluentIcon.ROBOT,
        'gallery': FluentIcon.ALBUM,
        'extract': FluentIcon.DOCUMENT,
        'close': FluentIcon.CLOSE,
        'minimize': FluentIcon.MINIMIZE,
        'maximize': FluentIcon.UP,
        'home': FluentIcon.HOME,
        'add': FluentIcon.ADD,
        'folder_add': FluentIcon.FOLDER_ADD,
        'edit': FluentIcon.EDIT,
        'magic': FluentIcon.BRUSH
    }
    
    @staticmethod
    def get_icon(name):
        """获取图标"""
        return FluentIcons.ICONS.get(name, FluentIcon.INFO)


class FluentColors:
    """Fluent颜色管理器"""
    
    # 语义化颜色
    COLORS = {
        'primary': '#4F46E5',
        'secondary': '#9CA3AF',
        'success': '#22C55E',
        'warning': '#FBD024',
        'error': '#EF4444',
        'info': '#3B82F6',
        
        # 背景色
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8FAFC',
        'bg_tertiary': '#F1F5F9',
        
        # 文本色
        'text_primary': '#1F2937',
        'text_secondary': '#6B7280',
        'text_tertiary': '#9CA3AF',
        
        # 边框色
        'border_primary': '#E5E7EB',
        'border_secondary': '#F3F4F6',
        
        # 阴影色
        'shadow_light': 'rgba(0, 0, 0, 0.05)',
        'shadow_medium': 'rgba(0, 0, 0, 0.1)',
        'shadow_heavy': 'rgba(0, 0, 0, 0.15)',
    }
    
    @staticmethod
    def get_color(name):
        """获取颜色"""
        return FluentColors.COLORS.get(name, '#000000')


class FluentAnimations:
    """Fluent动画管理器"""
    
    # 动画时长
    DURATION_FAST = 150
    DURATION_NORMAL = 250
    DURATION_SLOW = 350
    
    # 缓动函数
    EASING_STANDARD = "cubic-bezier(0.4, 0.0, 0.2, 1)"
    EASING_DECELERATE = "cubic-bezier(0.0, 0.0, 0.2, 1)"
    EASING_ACCELERATE = "cubic-bezier(0.4, 0.0, 1, 1)"


class FluentSpacing:
    """Fluent间距管理器"""
    
    # 标准间距
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48
    
    # 边距
    MARGIN_SM = 12
    MARGIN_MD = 20
    MARGIN_LG = 32
    
    # 内边距
    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24


class FluentTypography:
    """Fluent字体管理器"""
    
    # 字体大小
    FONT_SIZES = {
        'caption': 12,
        'body': 14,
        'subtitle': 16,
        'title': 20,
        'headline': 24,
        'display': 32
    }
    
    # 字体权重
    FONT_WEIGHTS = {
        'light': 300,
        'regular': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700
    }
    
    @staticmethod
    def get_font_style(size_key='body', weight_key='regular'):
        """获取字体样式"""
        size = FluentTypography.FONT_SIZES.get(size_key, 14)
        weight = FluentTypography.FONT_WEIGHTS.get(weight_key, 400)
        return f"font-size: {size}px; font-weight: {weight};" 