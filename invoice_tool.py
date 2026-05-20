#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票提单号提取重命名工具
支持拖拽使用，Windows/Mac双平台

用法:
    invoice-tool.exe "D:\\invoices"              # 指定输入目录
    invoice-tool.exe "D:\\invoices" -o "D:\\out"  # 指定输出目录
    invoice-tool.exe --config config.json         # 使用配置文件
"""

import os
import sys
import re
import json
import shutil
import argparse
from collections import Counter
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("错误: 缺少pypdf库，请重新安装")
    sys.exit(1)


class InvoiceTool:
    """发票提单号提取重命名工具"""

    # 默认配置
    DEFAULT_CONFIG = {
        "pattern": r'Order Reference:([^:;]+)[:;]',
        "remove_suffix": "TOTAL",
        "min_length": 6,
        "max_length": 20,
        "require_letter": True,
        "require_digit": True
    }

    def __init__(self, config_path=None, **kwargs):
        """初始化工具"""
        self.config = self.DEFAULT_CONFIG.copy()
        
        # 加载配置文件
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config.update(json.load(f))
        
        # 命令行参数覆盖配置
        for key, value in kwargs.items():
            if value is not None:
                self.config[key] = value

    def clean_filename(self, text):
        """清理文件名，移除非法字符，保留连字符"""
        if not text:
            return ""
        # 移除所有非字母数字和连字符的字符（包括换行符、空格等）
        cleaned = re.sub(r'[^A-Za-z0-9\-]', '', text)
        return cleaned

    def extract_order_reference(self, pdf_path):
        """从PDF中提取Order Reference"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            if not text:
                return None

            pattern = self.config.get("pattern", self.DEFAULT_CONFIG["pattern"])
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                ref = match.group(1).strip()
                
                # 去掉配置的尾部字符串（如TOTAL）
                suffix = self.config.get("remove_suffix")
                if suffix:
                    ref = re.sub(f'{suffix}$', '', ref, flags=re.IGNORECASE)
                
                # 清理文件名中的特殊字符（换行符等）
                ref = self.clean_filename(ref)
                
                return ref
            
            return None

        except Exception as e:
            return None

    def validate_reference(self, ref):
        """验证提单号格式"""
        if not ref:
            return False
        
        min_len = self.config.get("min_length", 6)
        max_len = self.config.get("max_length", 20)
        
        if len(ref) < min_len or len(ref) > max_len:
            return False
        
        if self.config.get("require_letter", True):
            if not re.search(r'[A-Za-z]', ref):
                return False
        
        if self.config.get("require_digit", True):
            if not re.search(r'\d', ref):
                return False
        
        return True

    def process(self, input_dir, output_dir=None):
        """
        处理发票目录
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径，默认为输入目录下的output/
        
        Returns:
            处理结果字典
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        if not input_path.is_dir():
            raise NotADirectoryError(f"不是有效目录: {input_dir}")

        # 确定输出目录
        if output_dir is None:
            output_dir = input_path / "output"
        else:
            output_dir = Path(output_dir)
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)

        # 收集所有PDF文件
        pdf_files = sorted([f for f in input_path.glob("*.pdf")])
        
        if not pdf_files:
            return {
                "success": False,
                "error": "未找到PDF文件",
                "total": 0,
                "processed": 0
            }

        # 提取每个文件的Order Reference
        results = []
        for pdf_file in pdf_files:
            ref = self.extract_order_reference(str(pdf_file))
            results.append({
                "source": pdf_file.name,
                "reference": ref,
                "valid": self.validate_reference(ref)
            })

        # 统计唯一值和重复
        valid_refs = [r for r in results if r["valid"]]
        ref_counter = Counter(r["reference"] for r in valid_refs)

        # 生成文件名映射
        ref_sequence = Counter()
        mappings = []
        
        for item in results:
            if not item["valid"]:
                # 无效或缺失的Order Reference，保留原名
                item["target"] = item["source"]
                item["duplicate_index"] = None
            elif ref_counter[item["reference"]] == 1:
                # 唯一的Order Reference
                item["target"] = f"{item['reference']}.pdf"
                item["duplicate_index"] = None
            else:
                # 重复的Order Reference，添加序号
                ref_sequence[item["reference"]] += 1
                seq = ref_sequence[item["reference"]]
                item["target"] = f"{item['reference']}-{seq}.pdf"
                item["duplicate_index"] = seq

            mappings.append(item)

        # 复制并重命名文件
        for item in mappings:
            src = input_path / item["source"]
            dst = output_dir / item["target"]
            
            # 处理文件名冲突
            counter = 1
            while dst.exists():
                base = item["target"].replace('.pdf', '')
                dst = output_dir / f"{base}_{counter}.pdf"
                counter += 1
            
            shutil.copy2(src, dst)
            item["output"] = dst.name

        # 生成报告
        report = self._generate_report(mappings, ref_counter, output_dir)

        return {
            "success": True,
            "input_dir": str(input_path),
            "output_dir": str(output_dir),
            "total": len(pdf_files),
            "processed": len(valid_refs),
            "unique": len(ref_counter),
            "duplicates": len([v for v in ref_counter.values() if v > 1]),
            "mappings": mappings,
            "report": report
        }

    def _generate_report(self, mappings, ref_counter, output_dir):
        """生成映射文件和验证报告"""
        # 映射文件
        mapping_file = output_dir / "filename_mapping.txt"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("发票提单号提取 - 文件名映射表\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"{'序号':<4} {'原文件名':<40} {'新文件名':<30}\n")
            f.write("-" * 70 + "\n")
            
            for i, item in enumerate(mappings, 1):
                f.write(f"{i:<4} {item['source']:<40} {item['output']:<30}\n")
            
            f.write("-" * 70 + "\n")
            f.write(f"\n统计汇总:\n")
            f.write(f"  总文件数: {len(mappings)}\n")
            f.write(f"  有效提单号: {len([m for m in mappings if m['valid']])}\n")
            f.write(f"  唯一提单号: {len(ref_counter)}\n")
            f.write(f"  重复提单号: {len([v for v in ref_counter.values() if v > 1])}\n")

        # 验证报告
        verification_file = output_dir / "verification_report.txt"
        with open(verification_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("验证报告\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("重复提单号明细:\n")
            f.write("-" * 70 + "\n")
            
            dup_refs = {k: v for k, v in ref_counter.items() if v > 1}
            if dup_refs:
                for ref, count in sorted(dup_refs.items()):
                    f.write(f"\n{ref} ({count}个文件):\n")
                    for item in mappings:
                        if item["reference"] == ref:
                            f.write(f"  - {item['source']} -> {item['output']}\n")
            else:
                f.write("无重复提单号\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"唯一提单号列表 ({len(ref_counter)}个):\n")
            f.write("-" * 70 + "\n")
            for ref in sorted(ref_counter.keys()):
                f.write(f"  {ref}\n")

        return {
            "mapping_file": str(mapping_file),
            "verification_file": str(verification_file)
        }


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="发票提单号提取重命名工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "D:\\invoices"                    # 处理目录，输出到 同目录/output
  %(prog)s "D:\\invoices" -o "D:\\output"    # 指定输出目录
  %(prog)s --config config.json              # 使用配置文件
  %(prog)s --pattern "Order ID:([^ ]+) "     # 自定义提取正则

拖拽使用:
  直接将文件夹拖拽到程序图标上即可
        """
    )
    
    parser.add_argument("input", nargs="?", help="输入目录路径")
    parser.add_argument("-o", "--output", help="输出目录路径（默认为输入目录下的output/）")
    parser.add_argument("-c", "--config", help="配置文件路径（JSON格式）")
    parser.add_argument("-p", "--pattern", help="自定义Order Reference提取正则")
    parser.add_argument("-r", "--remove-suffix", help="需要去除的尾部字符串（如TOTAL）")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式，不显示进度")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    # 处理拖拽输入（Windows会把文件路径作为参数传入）
    inputs = []
    if args.input:
        inputs.append(args.input)
    # 也检查sys.argv中的其他参数（拖拽时可能只传了路径）
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isdir(arg) and arg not in inputs:
                inputs.append(arg)
    
    if not inputs:
        parser.print_help()
        print("\n错误: 请指定输入目录，或将文件夹拖拽到程序上")
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 处理第一个输入目录
    input_dir = inputs[0]
    
    # 构建配置
    config = {}
    if args.config:
        config["config_path"] = args.config
    if args.pattern:
        config["pattern"] = args.pattern
    if args.remove_suffix:
        config["remove_suffix"] = args.remove_suffix
    
    try:
        tool = InvoiceTool(**config)
        
        if not args.quiet:
            print("=" * 50)
            print("发票提单号提取重命名工具 v1.0.0")
            print("=" * 50)
            print(f"输入目录: {input_dir}")
            print(f"正在处理...")
        
        result = tool.process(input_dir, args.output)
        
        if result["success"]:
            if not args.quiet:
                print(f"\n✅ 处理完成!")
                print(f"   总文件数: {result['total']}")
                print(f"   有效提单号: {result['processed']}")
                print(f"   唯一提单号: {result['unique']}")
                print(f"   重复提单号: {result['duplicates']}")
                print(f"\n📁 输出目录: {result['output_dir']}")
                print(f"   📄 filename_mapping.txt")
                print(f"   📄 verification_report.txt")
                
                # 自动打开输出目录
                try:
                    if sys.platform == 'win32':
                        os.startfile(result['output_dir'])
                    elif sys.platform == 'darwin':
                        os.system(f'open "{result["output_dir"]}"')
                    else:
                        os.system(f'xdg-open "{result["output_dir"]}"')
                except:
                    pass
        else:
            print(f"\n❌ 处理失败: {result['error']}")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if not args.quiet:
            input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
