@echo off
chcp 65001 >nul
echo ========================================
echo 发票提单号提取工具 - Windows打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到pip
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 安装依赖...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 安装PyInstaller
echo [2/3] 安装PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [错误] PyInstaller安装失败
    pause
    exit /b 1
)

REM 打包
echo [3/3] 正在打包...
pyinstaller invoice_tool.spec --clean

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo 输出目录: dist\invoice-tool\
echo.
echo 使用方法:
echo   1. 将 invoice-tool.exe 复制到任意位置
echo   2. 将发票文件夹拖拽到 invoice-tool.exe 上
echo   3. 等待处理完成，查看 output 文件夹
echo.
pause
