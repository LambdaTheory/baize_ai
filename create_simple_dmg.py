#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建简单但带背景的DMG
"""

import os
import shutil
import subprocess
import time

def create_simple_dmg_with_background():
    """创建简单的带背景DMG"""
    app_name = "白泽"
    app_path = f"dist/{app_name}.app"
    dmg_path = f"dist/{app_name}_with_background.dmg"
    temp_dmg_dir = f"dist/dmg_simple_temp"
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用文件 {app_path}")
        return False
    
    # 清理
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    if os.path.exists(temp_dmg_dir):
        shutil.rmtree(temp_dmg_dir)
    
    try:
        # 创建临时目录
        os.makedirs(temp_dmg_dir, exist_ok=True)
        
        # 复制文件
        shutil.copytree(app_path, f"{temp_dmg_dir}/{app_name}.app")
        os.symlink("/Applications", f"{temp_dmg_dir}/Applications")
        
        # 复制背景图片
        if os.path.exists("assets/dmg_background.png"):
            shutil.copy2("assets/dmg_background.png", f"{temp_dmg_dir}/.background.png")
            print("✅ 背景图片已复制")
        
        # 创建说明文件
        with open(f"{temp_dmg_dir}/安装说明.txt", "w", encoding="utf-8") as f:
            f.write(f"""将 {app_name}.app 拖拽到 Applications 文件夹即可安装。

如遇安全警告，请在系统偏好设置 > 安全性与隐私中允许运行。
""")
        
        # 直接创建压缩DMG（不使用临时转换）
        print("正在创建DMG...")
        subprocess.run([
            'hdiutil', 'create',
            '-volname', f'{app_name}AI Installer',
            '-srcfolder', temp_dmg_dir,
            '-ov', '-format', 'UDZO',
            '-imagekey', 'zlib-level=6',
            dmg_path
        ], check=True)
        
        # 清理
        shutil.rmtree(temp_dmg_dir)
        
        print(f"✅ 简单DMG创建成功: {dmg_path}")
        
        # 显示文件大小
        if os.path.exists(dmg_path):
            file_size = os.path.getsize(dmg_path) / (1024 * 1024)
            print(f"📦 文件大小: {file_size:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        if os.path.exists(temp_dmg_dir):
            shutil.rmtree(temp_dmg_dir)
        return False

if __name__ == "__main__":
    create_simple_dmg_with_background()
