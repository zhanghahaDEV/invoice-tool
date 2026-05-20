#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：检查提取的提单号中是否有特殊字符
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from invoice_tool import InvoiceTool
from pathlib import Path

EXPORT_DIR = "/sessions/6a0d1eac64d070586e45580d/workspace/export"

tool = InvoiceTool()
pdf_files = sorted([f for f in Path(EXPORT_DIR).glob("*.pdf")])

print("=" * 80)
print("检查每个文件提取的提单号字符")
print("=" * 80)

for pdf_file in pdf_files[:10]:  # 只检查前10个
    ref = tool.extract_order_reference(str(pdf_file))
    if ref:
        # 显示每个字符的 Unicode 码点
        chars_info = []
        for i, char in enumerate(ref):
            code = ord(char)
            if code > 127 or code < 32:  # 非ASCII或控制字符
                chars_info.append(f"[{i}]'{char}'(U+{code:04X})")
        
        if chars_info:
            print(f"\n{pdf_file.name}:")
            print(f"  提取值: '{ref}'")
            print(f"  特殊字符: {', '.join(chars_info)}")
        else:
            print(f"{pdf_file.name}: '{ref}' (无特殊字符)")

print("\n" + "=" * 80)
print("检查重复文件（带序号的）")
print("=" * 80)

# 检查 SIS00016885 相关的文件
target_files = [f for f in pdf_files if "16885" in f.name or "16884" in f.name]
for pdf_file in target_files:
    ref = tool.extract_order_reference(str(pdf_file))
    print(f"\n{pdf_file.name}:")
    print(f"  提取值: '{ref}'")
    print(f"  字节表示: {ref.encode('utf-8') if ref else 'None'}")
    
    # 模拟生成目标文件名
    if ref:
        target = f"{ref}-1.pdf"
        print(f"  目标文件名: '{target}'")
        print(f"  目标文件名字节: {target.encode('utf-8')}")
