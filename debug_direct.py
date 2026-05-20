#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path
from pypdf import PdfReader

EXPORT_DIR = "/sessions/6a0d1eac64d070586e45580d/workspace/export"

def clean_filename(text):
    """清理文件名，移除非法字符，保留连字符"""
    if not text:
        return ""
    cleaned = re.sub(r'[^A-Za-z0-9\-]', '', text)
    return cleaned

def extract_order_reference(pdf_path):
    """从PDF中提取Order Reference"""
    try:
        print(f"Opening: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if not text:
            print("No text extracted")
            return None

        pattern = r'Order Reference:([^:;]+)[:;]'
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"Match: {match}")
        
        if match:
            ref = match.group(1).strip()
            print(f"1. After strip: {repr(ref)}")
            
            suffix = "TOTAL"
            if suffix:
                ref = re.sub(f'{suffix}$', '', ref, flags=re.IGNORECASE)
                print(f"2. After remove TOTAL: {repr(ref)}")
            
            ref = clean_filename(ref)
            print(f"3. After clean: {repr(ref)}")
            
            return ref
        
        return None

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# 测试
pdf_file = Path(EXPORT_DIR) / "发票2026-05-07 15-27-35_18.pdf"
result = extract_order_reference(str(pdf_file))
print(f"\nFinal result: {repr(result)}")
