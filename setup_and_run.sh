#!/bin/bash

# 白泽AI - macOS 环境设置和运行脚本
# 这个脚本会自动设置PATH环境变量并运行应用程序

echo "=== 白泽AI - macOS 运行助手 ==="

# 设置PATH环境变量
export PATH="/Users/arthurdon/Library/Python/3.9/bin:$PATH"

# 检查PyInstaller是否可用
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller未正确安装或PATH未设置"
    echo "请运行: pip3 install pyinstaller"
    exit 1
fi

echo "✅ Python环境已设置"

# 检查是否需要构建
if [ ! -f "dist/白泽.app/Contents/MacOS/白泽" ]; then
    echo "📦 正在构建应用程序..."
    python3 build_mac.py
    
    if [ $? -eq 0 ]; then
        echo "✅ 构建成功！"
    else
        echo "❌ 构建失败"
        exit 1
    fi
fi

echo "🚀 启动应用程序..."
echo "💡 提示：如果系统提示安全警告，请在系统偏好设置 > 安全性与隐私中允许运行"
echo ""

# 运行应用程序
open "dist/白泽.app"

echo "应用程序已启动！" 