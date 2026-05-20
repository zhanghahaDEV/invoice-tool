#!/bin/bash
# 发票提单号提取工具 - Mac/Linux打包脚本

echo "========================================"
echo "发票提单号提取工具 - Mac/Linux打包脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未检测到pip3"
    exit 1
fi

# 安装依赖
echo "[1/3] 安装依赖..."
pip3 install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

# 安装PyInstaller
echo "[2/3] 安装PyInstaller..."
pip3 install pyinstaller --quiet
if [ $? -ne 0 ]; then
    echo "[错误] PyInstaller安装失败"
    exit 1
fi

# 打包
echo "[3/3] 正在打包..."
pyinstaller invoice_tool.spec --clean

if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo "输出目录: dist/invoice-tool/"
echo ""
echo "使用方法:"
echo "  1. 打开 dist/invoice-tool/ 目录"
echo "  2. 双击 invoice-tool 运行"
echo "  3. 选择发票文件夹或拖拽到程序上"
echo "  4. 等待处理完成，查看 output 文件夹"
echo ""
