#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本3：检查实际处理流程生成的文件名
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from invoice_tool import InvoiceTool
from pathlib import Path
from collections import Counter

EXPORT_DIR = "/sessions/6a0d1eac64d070586e45580d/workspace/export"
OUTPUT_DIR = "/sessions/6a0d1eac64d070586e45580d/workspace/output_debug"

# 清理输出目录
import shutil
if Path(OUTPUT_DIR).exists():
    shutil.rmtree(OUTPUT_DIR)

tool = InvoiceTool()

print("=" * 80)
print("检查实际生成的文件名")
print("=" * 80)

# 模拟 process 方法的关键逻辑
input_path = Path(EXPORT_DIR)
pdf_files = sorted([f for f in input_path.glob("*.pdf")])

# 提取每个文件的Order Reference
results = []
for pdf_file in pdf_files:
    ref = tool.extract_order_reference(str(pdf_file))
    valid = tool.validate_reference(ref)
    results.append({
        "source": pdf_file.name,
        "reference": ref,
        "valid": valid
    })
    
    if "16885" in pdf_file.name or "16884" in pdf_file.name:
        print(f"\n{pdf_file.name}:")
        print(f"  reference: '{ref}'")
        print(f"  字节: {ref.encode('utf-8') if ref else 'None'}")
        print(f"  valid: {valid}")

# 统计唯一值和重复
valid_refs = [r for r in results if r["valid"]]
ref_counter = Counter(r["reference"] for r in valid_refs)

print(f"\n{'='*80}")
print("生成目标文件名")
print(f"{'='*80}")

ref_sequence = Counter()
for item in results:
    if not item["valid"]:
        item["target"] = item["source"]
    elif ref_counter[item["reference"]] == 1:
        item["target"] = f"{item['reference']}.pdf"
    else:
        ref_sequence[item["reference"]] += 1
        seq = ref_sequence[item["reference"]]
        item["target"] = f"{item['reference']}-{seq}.pdf"
    
    if "16885" in item["source"] or (item["reference"] and "16885" in item["reference"]):
        print(f"\n{item['source']}:")
        print(f"  -> '{item['target']}'")
        print(f"  字节: {item['target'].encode('utf-8')}")
