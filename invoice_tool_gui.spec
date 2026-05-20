# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# 根据平台选择图标格式
if sys.platform == 'win32':
    icon_file = 'gui/icon.ico'
    datas=[
        ('gui/index.html', 'gui'),
        ('gui/icon.ico', 'gui'),
        ('config.example.json', '.'),
    ]
elif sys.platform == 'darwin':
    icon_file = 'gui/icon.icns'
    datas=[
        ('gui/index.html', 'gui'),
        ('gui/icon.icns', 'gui'),
        ('config.example.json', '.'),
    ]
else:
    icon_file = None
    datas=[
        ('gui/index.html', 'gui'),
        ('config.example.json', '.'),
    ]

a = Analysis(
    ['invoice_tool_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
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
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='invoice-tool',
)
