#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成Windows应用图标(.ico)文件
使用方法：准备一个256x256的PNG图像，命名为app_icon.png，然后运行此脚本
需要安装Pillow库：pip install Pillow
"""

import os
import sys
from pathlib import Path
from PIL import Image

def main():
    """生成ico图标文件"""
    print("开始生成Windows应用图标...")
    
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 检查源图片
    source_image_path = script_dir / "app_icon.png"
    if not source_image_path.exists():
        print("错误: 未找到源图片 app_icon.png")
        print("请准备一个PNG图像，并命名为app_icon.png")
        return False
    
    # 确保PIL库已安装
    try:
        from PIL import Image
    except ImportError:
        print("错误: 未安装PIL库")
        print("请运行: pip install Pillow")
        return False
        
    # 生成不同尺寸的图像
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    images = []
    source_image = Image.open(source_image_path)
    
    for size in sizes:
        resized_image = source_image.resize(size, Image.LANCZOS)
        images.append(resized_image)
    
    # 生成.ico文件
    output_icon = script_dir / "app_icon.ico"
    
    # 保存为ico格式
    images[0].save(
        output_icon,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    
    if output_icon.exists():
        print(f"成功生成图标文件: {output_icon}")
        return True
    else:
        print("生成图标文件失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 