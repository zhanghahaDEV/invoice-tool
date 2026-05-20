#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本2：详细检查每个处理步骤
"""

import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from pypdf import PdfReader

EXPORT_DIR = "/sessions/6a0d1eac64d070586e45580d/workspace/export"

# 检查 SIS00016885 相关的文件
target_files = [
    "发票2026-05-07 15-27-35_18.pdf",
    "发票2026-05-07 15-27-35_36.pdf", 
    "发票2026-05-07 15-27-35_42.pdf"
]

print("=" * 80)
print("逐步检查提取过程")
print("=" * 80)

pattern = r'Order Reference:([^:;]+)[:;]'
remove_suffix = "TOTAL"

for filename in target_files:
    pdf_path = Path(EXPORT_DIR) / filename
    if not pdf_path.exists():
        print(f"\n{filename}: 文件不存在")
        continue
    
    print(f"\n{'='*80}")
    print(f"文件: {filename}")
    print(f"{'='*80}")
    
    # Step 1: 提取PDF文本
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    
    # Step 2: 查找匹配
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        raw_ref = match.group(1)
        print(f"Step 1 - 原始匹配: '{raw_ref}'")
        print(f"         字节: {raw_ref.encode('utf-8')}")
        print(f"         长度: {len(raw_ref)}")
        
        # Step 3: strip
        stripped = raw_ref.strip()
        print(f"Step 2 - strip后: '{stripped}'")
        print(f"         字节: {stripped.encode('utf-8')}")
        print(f"         长度: {len(stripped)}")
        
        # Step 4: 去除TOTAL
        no_total = re.sub(f'{remove_suffix}$', '', stripped, flags=re.IGNORECASE)
        print(f"Step 3 - 去TOTAL: '{no_total}'")
        print(f"         字节: {no_total.encode('utf-8')}")
        print(f"         长度: {len(no_total)}")
        
        # Step 5: clean_filename (如果存在)
        cleaned = re.sub(r'[^A-Za-z0-9\-]', '', no_total)
        print(f"Step 4 - 清理后: '{cleaned}'")
        print(f"         字节: {cleaned.encode('utf-8')}")
        print(f"         长度: {len(cleaned)}")
        
        # 检查原始匹配的前后字符
        start = match.start()
        end = match.end()
        context_before = text[max(0, start-10):start]
        context_after = text[end:min(len(text), end+10)]
        print(f"\n上下文:")
        print(f"  前面: '{context_before}'")
        print(f"  匹配: '{match.group(0)}'")
        print(f"  后面: '{context_after}'")
    else:
        print("未找到匹配")
