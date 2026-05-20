# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# 基础配置
base_datas = [
    ('gui/index.html', 'gui'),
    ('config.example.json', '.'),
]

a = Analysis(
    ['invoice_tool_gui.py'],
    pathex=[],
    binaries=[],
    datas=base_datas,
    hiddenimports=['pypdf', 'webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# macOS: 创建 .app bundle
if sys.platform == 'darwin':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='InvoiceTool',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,  # macOS 需要启用
        target_arch=None,
        codesign_identity=None,  # 使用 ad-hoc 签名
        entitlements_file=None,
        icon='gui/icon.icns',
    )
    
    app = BUNDLE(
        exe,
        name='InvoiceTool.app',
        icon='gui/icon.icns',
        bundle_identifier='com.invoice-tool.app',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13',
        },
    )

# Windows: 创建单文件可执行程序
elif sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='InvoiceTool',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='gui/icon.ico',
    )

# Linux: 创建单文件可执行程序
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='invoice-tool',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,
    )
