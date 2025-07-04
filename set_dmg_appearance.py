#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置DMG外观的脚本
"""

import subprocess
import time
import os

def set_dmg_appearance(volume_name="白泽AI Installer 2"):
    """设置DMG的外观"""
    
    mount_point = f"/Volumes/{volume_name}"
    
    if not os.path.exists(mount_point):
        print(f"错误: 找不到挂载点 {mount_point}")
        return False
    
    # AppleScript来设置外观
    applescript = f'''
tell application "Finder"
    tell disk "{volume_name}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {{100, 100, 740, 500}}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        
        -- 设置背景图片
        try
            set background picture of viewOptions to file ".background.png"
            delay 1
        on error
            -- 如果设置背景失败，继续其他设置
        end try
        
        -- 设置图标位置
        try
            set position of item "白泽.app" of container window to {{150, 200}}
            set position of item "Applications" of container window to {{490, 200}}
            set position of item "安装说明.txt" of container window to {{320, 350}}
        on error
            -- 如果设置位置失败，继续
        end try
        
        -- 更新窗口
        update without registering applications
        delay 2
        
        -- 关闭窗口但保持设置
        close
    end tell
end tell
'''
    
    try:
        print(f"正在设置 {volume_name} 的外观...")
        subprocess.run(['osascript', '-e', applescript], 
                     check=True, timeout=60)
        print("✅ DMG外观设置完成")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"❌ 设置DMG外观失败: {e}")
        return False

if __name__ == "__main__":
    set_dmg_appearance()
