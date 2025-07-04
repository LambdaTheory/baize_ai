#!/bin/bash
# 白泽AI启动脚本

echo "=== 白泽AI启动脚本 ==="
echo "正在启动应用..."

# 切换到应用目录
cd "$(dirname "$0")/dist"

# 启动应用
open 白泽.app

echo "应用已启动！"
echo "如果应用没有显示，请检查系统偏好设置 > 安全性与隐私"
