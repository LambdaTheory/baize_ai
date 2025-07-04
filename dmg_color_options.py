#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DMG颜色选项配置
"""

# macOS颜色值使用0-65535范围
DMG_COLOR_OPTIONS = {
    "white": (65535, 65535, 65535),           # 纯白色 - 简洁专业
    "light_gray": (58000, 58000, 58000),      # 浅灰色 - 现代感
    "warm_white": (65535, 64000, 62000),      # 暖白色 - 温和
    "cool_gray": (56000, 58000, 60000),       # 冷灰色 - 科技感
    "light_blue": (58000, 62000, 65535),      # 浅蓝色 - 清新
    "mint": (58000, 65535, 62000),            # 薄荷色 - 清爽
    "cream": (65535, 63000, 58000),           # 奶油色 - 温暖
    "pearl": (62000, 63000, 64000),           # 珍珠色 - 优雅
}

def get_dmg_color(color_name="light_gray"):
    """获取DMG背景颜色"""
    return DMG_COLOR_OPTIONS.get(color_name, DMG_COLOR_OPTIONS["light_gray"])

def list_color_options():
    """列出所有颜色选项"""
    print("可用的DMG背景颜色:")
    for name, rgb in DMG_COLOR_OPTIONS.items():
        print(f"  {name}: RGB{rgb}")

if __name__ == "__main__":
    list_color_options()
