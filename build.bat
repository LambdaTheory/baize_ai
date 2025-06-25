@echo off
chcp 65001
echo ======================================
echo    AI图片信息提取工具 - exe打包程序
echo ======================================
echo.

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo.
echo 检查依赖包...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo.
echo 开始打包exe文件...
echo 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo 使用PyInstaller打包...
pyinstaller --onefile --windowed --name="AI图片信息提取工具" --hidden-import=PyQt5.sip --hidden-import=qfluentwidgets --add-data="assets;assets" main.py

if %errorlevel% eq 0 (
    echo.
    echo ======================================
    echo           打包成功完成！
    echo ======================================
    echo exe文件位置: dist\AI图片信息提取工具.exe
    echo 文件大小: 
    dir dist\*.exe
    echo.
    echo 是否打开dist目录？ (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" explorer dist
) else (
    echo.
    echo ======================================
    echo           打包失败！
    echo ======================================
    echo 请检查错误信息并修复问题
)

echo.
pause 