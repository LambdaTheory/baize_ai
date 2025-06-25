#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包配置文件
用于PyInstaller打包
"""

from setuptools import setup, find_packages

setup(
    name="ai-image-info-reader",
    version="1.0.0",
    description="白泽AI - 智能图片信息提取工具",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyQt5>=5.15.0",
        "Pillow>=9.0.0",
        "pyinstaller>=5.0",
        "exifread>=3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "ai-image-reader=main:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 