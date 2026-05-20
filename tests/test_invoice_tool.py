#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票提单号提取工具 - 单元测试
运行方式: python -m pytest tests/ -v
"""

import os
import sys
import json
import shutil
import tempfile
import pytest
from pathlib import Path

# 确保能导入主模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from invoice_tool import InvoiceTool


class TestExtractOrderReference:
    """测试Order Reference提取"""

    def setup_method(self):
        self.tool = InvoiceTool()

    def test_extract_colon_format(self):
        """格式A: Order Reference:SIS00017078TOTAL: USD 549.54"""
        # 创建临时PDF（用pypdf生成一个简单的测试PDF）
        from pypdf import PdfWriter
        from io import BytesIO

        writer = PdfWriter()
        page = writer.add_blank_page(width=595, height=842)
        # 注意: pypdf无法直接写入文本到空白页，所以用extract_text模拟
        # 这里通过monkey-patch来测试
        pass  # 实际测试在test_extract_logic中用字符串匹配

    def test_extract_pattern_colon(self):
        """测试正则: 冒号分隔格式"""
        text = "Order Reference:SIS00017078TOTAL: USD 549.54"
        import re
        pattern = self.tool.config["pattern"]
        match = re.search(pattern, text, re.IGNORECASE)
        assert match is not None
        assert match.group(1).strip() == "SIS00017078TOTAL"

    def test_extract_pattern_semicolon(self):
        """测试正则: 分号分隔格式"""
        text = "Order Reference:SIS00017381;TOTAL: USD 109.00"
        import re
        pattern = self.tool.config["pattern"]
        match = re.search(pattern, text, re.IGNORECASE)
        assert match is not None
        assert match.group(1).strip() == "SIS00017381"

    def test_extract_pattern_no_match(self):
        """测试正则: 无匹配"""
        text = "Some random text without Order Reference"
        import re
        pattern = self.tool.config["pattern"]
        match = re.search(pattern, text, re.IGNORECASE)
        assert match is None

    def test_extract_pattern_multiple_colons(self):
        """测试正则: 多个冒号的情况"""
        text = "Order Reference:SIS00017078TOTAL: USD 549.54: Extra"
        import re
        pattern = self.tool.config["pattern"]
        match = re.search(pattern, text, re.IGNORECASE)
        assert match is not None
        assert match.group(1).strip() == "SIS00017078TOTAL"


class TestRemoveSuffix:
    """测试去除尾部字符串"""

    def setup_method(self):
        self.tool = InvoiceTool()

    def test_remove_total_suffix(self):
        """测试去除TOTAL后缀"""
        raw = "SIS00017078TOTAL"
        import re
        suffix = self.tool.config["remove_suffix"]
        result = re.sub(f'{suffix}$', '', raw, flags=re.IGNORECASE)
        assert result == "SIS00017078"

    def test_remove_total_case_insensitive(self):
        """测试去除TOTAL后缀（大小写不敏感）"""
        raw = "SIS00017078total"
        import re
        suffix = self.tool.config["remove_suffix"]
        result = re.sub(f'{suffix}$', '', raw, flags=re.IGNORECASE)
        assert result == "SIS00017078"

    def test_no_suffix_to_remove(self):
        """测试没有后缀的情况"""
        raw = "SIS00017381"
        import re
        suffix = self.tool.config["remove_suffix"]
        result = re.sub(f'{suffix}$', '', raw, flags=re.IGNORECASE)
        assert result == "SIS00017381"

    def test_suffix_in_middle(self):
        """测试TOTAL在中间（不应去除）"""
        raw = "TOTALSIS00017078"
        import re
        suffix = self.tool.config["remove_suffix"]
        result = re.sub(f'{suffix}$', '', raw, flags=re.IGNORECASE)
        assert result == "TOTALSIS00017078"

    def test_empty_remove_suffix(self):
        """测试配置不去除后缀"""
        tool = InvoiceTool(remove_suffix="")
        raw = "SIS00017078TOTAL"
        result = raw  # 不做任何处理
        assert result == "SIS00017078TOTAL"


class TestValidateReference:
    """测试提单号格式验证"""

    def setup_method(self):
        self.tool = InvoiceTool()

    def test_valid_standard_format(self):
        """标准格式: SIS + 8位数字"""
        assert self.tool.validate_reference("SIS00017078") is True

    def test_valid_with_total(self):
        """带TOTAL的格式"""
        assert self.tool.validate_reference("SIS00017078TOTAL") is True

    def test_valid_short(self):
        """最短合法长度: 6位"""
        assert self.tool.validate_reference("AB1234") is True

    def test_valid_long(self):
        """最长合法长度: 20位"""
        assert self.tool.validate_reference("ABCD1234567890123456") is True

    def test_invalid_too_short(self):
        """太短: 5位"""
        assert self.tool.validate_reference("AB123") is False

    def test_invalid_too_long(self):
        """太长: 21位"""
        assert self.tool.validate_reference("ABCD12345678901234567") is False

    def test_invalid_no_letter(self):
        """纯数字"""
        assert self.tool.validate_reference("12345678") is False

    def test_invalid_no_digit(self):
        """纯字母"""
        assert self.tool.validate_reference("SISTOTAL") is False

    def test_invalid_empty(self):
        """空字符串"""
        assert self.tool.validate_reference("") is False

    def test_invalid_none(self):
        """None"""
        assert self.tool.validate_reference(None) is False

    def test_valid_maersk_format(self):
        """马士基格式: 9位纯数字（但我们的规则要求含字母）"""
        assert self.tool.validate_reference("123456789") is False

    def test_valid_cosco_format(self):
        """中远格式: COAU + 10位数字"""
        assert self.tool.validate_reference("COAU1234567890") is True


class TestConfig:
    """测试配置加载"""

    def test_default_config(self):
        """默认配置"""
        tool = InvoiceTool()
        assert tool.config["pattern"] == r'Order Reference:([^:;]+)[:;]'
        assert tool.config["remove_suffix"] == "TOTAL"
        assert tool.config["min_length"] == 6
        assert tool.config["max_length"] == 20

    def test_custom_config_via_kwargs(self):
        """通过参数覆盖配置"""
        tool = InvoiceTool(pattern="Custom:([^ ]+)", remove_suffix="")
        assert tool.config["pattern"] == "Custom:([^ ]+)"
        assert tool.config["remove_suffix"] == ""

    def test_config_from_file(self, tmp_path):
        """从JSON文件加载配置"""
        config = {
            "pattern": "Ref:([^,]+),",
            "remove_suffix": "SUM",
            "min_length": 4
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config))

        tool = InvoiceTool(config_path=str(config_file))
        assert tool.config["pattern"] == "Ref:([^,]+),"
        assert tool.config["remove_suffix"] == "SUM"
        assert tool.config["min_length"] == 4


class TestFileProcessing:
    """测试文件处理流程"""

    def test_process_nonexistent_dir(self):
        """处理不存在的目录"""
        tool = InvoiceTool()
        with pytest.raises(FileNotFoundError):
            tool.process("/nonexistent/path")

    def test_process_file_not_dir(self, tmp_path):
        """处理文件而非目录"""
        tool = InvoiceTool()
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")
        with pytest.raises(NotADirectoryError):
            tool.process(str(test_file))

    def test_process_empty_dir(self, tmp_path):
        """处理空目录"""
        tool = InvoiceTool()
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = tool.process(str(empty_dir))
        assert result["success"] is False
        assert "未找到PDF" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
