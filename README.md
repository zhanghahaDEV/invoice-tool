# 发票提单号提取重命名工具

从发票PDF中提取Order Reference（提单号），并按提单号自动重命名文件。

## 功能特点

- 🚀 **简单易用**：拖拽即用，无需安装Python
- 📋 **智能识别**：自动识别提单号格式，兼容多种发票模板
- 🔄 **处理重复**：提单号重复时自动添加序号（如 `SIS00017078-1.pdf`）
- 📊 **可追溯**：生成文件名映射表和验证报告
- 🛡️ **安全可靠**：只读取复制，不修改原始文件

## 下载

前往 [Releases](https://github.com/your-repo/releases) 页面下载：

- **Windows**: `invoice-tool-windows.zip`（双击 `invoice-tool.exe` 运行）
- **Mac**: `invoice-tool-mac.zip`（双击 `invoice-tool` 运行）
- **Linux**: `invoice-tool-linux.tar.gz`

## 使用方法

### 方法一：拖拽（推荐）

1. 下载并解压对应系统的版本
2. 将程序复制到任意位置
3. 将包含发票PDF的**文件夹**拖拽到程序图标上
4. 等待处理完成
5. 在原文件夹下的 `output/` 目录中查看结果

### 方法二：命令行

**Windows:**
```cmd
invoice-tool.exe "D:\invoices"
invoice-tool.exe "D:\invoices" -o "D:\output"
```

**Mac/Linux:**
```bash
./invoice-tool "~/invoices"
./invoice-tool "~/invoices" -o "~/output"
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `input` | 输入目录路径 |
| `-o, --output` | 输出目录路径 |
| `-c, --config` | 配置文件路径 |
| `-p, --pattern` | 自定义提取正则 |
| `-r, --remove-suffix` | 去除的尾部字符串 |
| `-q, --quiet` | 静默模式 |

## 配置文件

```json
{
    "pattern": "Order Reference:([^:;]+)[:;]",
    "remove_suffix": "TOTAL",
    "min_length": 6,
    "max_length": 20,
    "require_letter": true,
    "require_digit": true
}
```

## 从源码构建

### 自动构建（推荐）

1. Fork 此仓库
2. 推送 tag：`git tag v1.0.0 && git push origin v1.0.0`
3. GitHub Actions 自动为 Windows/Mac/Linux 三个平台构建
4. 在 Releases 页面下载

### 手动构建

**Windows:**
```cmd
pip install -r requirements.txt
pip install pyinstaller
pyinstaller invoice_tool.spec --clean
```

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
pip3 install pyinstaller
pyinstaller invoice_tool.spec --clean
```

### 本地调试打包

如果打包过程中遇到问题，可以使用以下方法调试：

**1. 直接运行Python脚本（不打包）**
```bash
# 测试基本功能
python3 invoice_tool.py /path/to/invoices -o /path/to/output

# 查看详细输出
python3 invoice_tool.py /path/to/invoices -v
```

**2. 使用调试脚本检查PDF提取**
```bash
# 运行调试脚本查看提取过程
python3 debug_chars2.py

# 检查特定文件
python3 -c "
from invoice_tool import InvoiceTool
tool = InvoiceTool()
ref = tool.extract_order_reference('path/to/invoice.pdf')
print(f'Extracted: {repr(ref)}')
"
```

**3. PyInstaller单文件模式调试**
```bash
# 打包为单文件（方便测试）
pyinstaller --onefile --console invoice_tool.py

# 运行并查看错误输出
./dist/invoice_tool /path/to/invoices
```

**4. 常见问题排查**

| 问题 | 解决方法 |
|------|---------|
| 打包后运行无反应 | 使用 `--console` 参数重新打包，查看错误输出 |
| 缺少依赖 | 确保 `requirements.txt` 中所有包都已安装 |
| 文件找不到 | 检查 `invoice_tool.spec` 中的 `pathex` 配置 |
| 权限不足（Mac） | 运行 `chmod +x dist/invoice-tool/invoice-tool` |

**5. 清理缓存重新打包**
```bash
# 删除构建缓存
rm -rf build/ dist/ __pycache__/

# 重新打包
pyinstaller invoice_tool.spec --clean
```

## 技术栈

- Python 3.8+
- [pypdf](https://pypdf.readthedocs.io/) - PDF文本提取
- [PyInstaller](https://pyinstaller.org/) - 打包为可执行文件

## 许可证

MIT License
