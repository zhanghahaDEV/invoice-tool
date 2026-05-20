#!/usr/bin/env python3
"""
生成各平台的应用图标
从 gui/icon.jpg 生成 Windows .ico 和 macOS .icns
"""

from PIL import Image
import struct
import io
import sys


def create_windows_ico(input_path, output_path):
    """创建 Windows .ico 文件"""
    img = Image.open(input_path)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, sizes=icon_sizes)
    print(f"Created {output_path} for Windows")


def create_macos_icns(input_path, output_path):
    """创建 macOS .icns 文件"""
    img = Image.open(input_path)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    icon_types = {
        16: b'icp4', 32: b'icp5', 64: b'icp6',
        128: b'ic07', 256: b'ic08', 512: b'ic09', 1024: b'ic10'
    }

    entries = []
    for size in sizes:
        resized = img.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format='PNG')
        entries.append((icon_types[size], buf.getvalue()))

    header_size = 8
    entries_size = sum(8 + len(data) for _, data in entries)
    total_size = header_size + entries_size

    with open(output_path, 'wb') as f:
        f.write(b'icns')
        f.write(struct.pack('>I', total_size))
        for icon_type, data in entries:
            f.write(icon_type)
            f.write(struct.pack('>I', 8 + len(data)))
            f.write(data)

    print(f"Created {output_path} for macOS")


def main():
    input_file = 'gui/icon.jpg'

    try:
        create_windows_ico(input_file, 'gui/icon.ico')
        create_macos_icns(input_file, 'gui/icon.icns')
        print("Icons prepared successfully!")
        return 0
    except Exception as e:
        print(f"Error preparing icons: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
