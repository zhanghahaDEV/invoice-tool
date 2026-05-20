#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票提单号提取工具 - GUI版本
PyWebView + HTML，明亮极简风格
"""

import os
import sys
import webview
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoice_tool import InvoiceTool


class Api:
    """暴露给前端的API（参考官方 js_api 示例）"""

    def __init__(self):
        self.tool = InvoiceTool()
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_directory(self):
        """选择目录对话框"""
        result = self._window.create_file_dialog(
            dialog_type=webview.FOLDER_DIALOG,
        )
        if result and len(result) > 0:
            return {"success": True, "path": result[0]}
        return {"success": False, "path": ""}

    def preview(self, input_dir):
        """预览：扫描全部PDF文件，返回汇总数据"""
        input_path = Path(input_dir)
        if not input_path.exists():
            return {"success": False, "error": "目录不存在"}

        pdf_files = sorted([f for f in input_path.glob("*.pdf")])
        if not pdf_files:
            return {"success": False, "error": "未找到PDF文件"}

        # 扫描全部文件
        valid_count = 0
        refs = {}
        for pdf_file in pdf_files:
            ref = self.tool.extract_order_reference(str(pdf_file))
            if ref and self.tool.validate_reference(ref):
                valid_count += 1
                refs[ref] = refs.get(ref, 0) + 1

        unique_count = len(refs)
        dup_count = sum(1 for v in refs.values() if v > 1)
        unrecognizable = len(pdf_files) - valid_count

        return {
            "success": True,
            "total_files": len(pdf_files),
            "valid_count": valid_count,
            "unique_count": unique_count,
            "dup_count": dup_count,
            "unrecognizable": unrecognizable
        }

    def process(self, input_dir, output_dir=""):
        """执行处理"""
        result = self.tool.process(input_dir, output_dir if output_dir else None)

        if result["success"]:
            return {
                "success": True,
                "total": result["total"],
                "processed": result["processed"],
                "unique": result["unique"],
                "duplicates": result["duplicates"],
                "output_dir": result["output_dir"],
                "mappings": [
                    {
                        "source": m["source"],
                        "output": m["output"],
                        "reference": m["reference"],
                        "valid": m["valid"]
                    }
                    for m in result["mappings"]
                ]
            }
        else:
            return {"success": False, "error": result["error"]}

    def open_directory(self, path):
        """打开目录"""
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
        return {"success": True}


def main():
    api = Api()
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui", "index.html")

    # 允许 file:// 协议
    webview.settings['ALLOW_FILE_URLS'] = True

    window = webview.create_window(
        title="Invoice Tool",
        url=html_path,
        js_api=api,
        width=680,
        height=580,
        min_size=(520, 480),
        resizable=True,
        text_select=False,
    )

    api.set_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
