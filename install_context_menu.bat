@echo off
chcp 65001
echo ============================================================
echo AI图片信息提取工具 - Windows右键菜单安装程序
echo ============================================================
echo.

REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  警告: 建议以管理员权限运行此脚本
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo 正在启动安装程序...
echo.

python install_context_menu.py

echo.
pause 