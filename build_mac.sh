#!/bin/bash
# 白泽AI - macOS 打包脚本
# 使用此脚本简化macOS应用打包流程

set -e  # 遇到错误时退出

echo "=== 白泽AI - macOS 打包助手 ==="
echo

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

echo "检查Python版本..."
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python版本: $python_version (满足要求)"
else
    echo "✗ Python版本: $python_version (需要$required_version或更高版本)"
    exit 1
fi

# 检查是否在macOS上运行
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✓ 运行环境: macOS"
else
    echo "⚠ 警告: 当前不在macOS环境，但仍将继续执行"
fi

# 检查PyInstaller是否安装
echo "检查PyInstaller..."
if command -v pyinstaller &> /dev/null; then
    echo "✓ PyInstaller已安装"
else
    echo "✗ PyInstaller未安装，正在安装..."
    pip3 install pyinstaller
fi

echo

# 提供打包选项
echo "请选择打包选项:"
echo "1. 基本打包 (.app文件)"
echo "2. 创建DMG安装包"
echo "3. 免激活版本"
echo "4. 免激活版本 + DMG安装包"
echo

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "开始基本打包..."
        python3 build_mac.py
        ;;
    2)
        echo "开始打包并创建DMG..."
        python3 build_mac.py --create-dmg
        ;;
    3)
        echo "开始打包免激活版本..."
        python3 build_mac.py --no-activation
        ;;
    4)
        echo "开始打包免激活版本并创建DMG..."
        python3 build_mac.py --no-activation --create-dmg
        ;;
    *)
        echo "无效选择，使用默认选项（基本打包）..."
        python3 build_mac.py
        ;;
esac

echo
echo "=== 打包完成 ==="

# 检查打包结果
if [ -d "dist/白泽.app" ]; then
    echo "✓ 成功创建: dist/白泽.app"
    
    # 显示应用包大小
    size=$(du -sh "dist/白泽.app" | cut -f1)
    echo "  应用包大小: $size"
fi

if [ -f "dist/白泽.dmg" ]; then
    echo "✓ 成功创建: dist/白泽.dmg"
    
    # 显示DMG文件大小
    size=$(du -sh "dist/白泽.dmg" | cut -f1)
    echo "  DMG文件大小: $size"
fi

echo
echo "后续步骤:"
echo "1. 测试应用: 双击 dist/白泽.app 验证功能"
echo "2. 分发应用: 将文件分享给其他用户"
echo "3. 如需签名: 参考 macOS打包说明.md 中的代码签名部分"
echo

echo "感谢使用白泽AI打包工具！" 