#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成macOS应用图标(.icns)文件
使用方法：准备一个1024x1024的PNG图像，命名为app_icon.png，然后运行此脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """生成icns图标文件"""
    print("开始生成macOS应用图标...")
    
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 检查源图片
    source_image = script_dir / "app_icon.png"
    if not source_image.exists():
        print("错误: 未找到源图片 app_icon.png")
        print("请准备一个1024x1024像素的PNG图像，并命名为app_icon.png")
        return False
    
    # 创建临时目录结构
    iconset_dir = script_dir / "app_icon.iconset"
    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    
    os.makedirs(iconset_dir)
    
    # 生成各种尺寸的图标
    icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in icon_sizes:
        # 普通尺寸
        out_file = iconset_dir / f"icon_{size}x{size}.png"
        cmd = f"sips -z {size} {size} {source_image} --out {out_file}"
        os.system(cmd)
        
        # 高分辨率尺寸 (@2x)
        if size < 1024:  # 1024足够大了，不需要@2x版本
            out_file = iconset_dir / f"icon_{size}x{size}@2x.png"
            doubled = size * 2
            cmd = f"sips -z {doubled} {doubled} {source_image} --out {out_file}"
            os.system(cmd)
    
    # 生成.icns文件
    output_icon = script_dir / "app_icon.icns"
    cmd = f"iconutil -c icns {iconset_dir}"
    result = os.system(cmd)
    
    # 清理临时文件
    shutil.rmtree(iconset_dir)
    
    if result == 0 and output_icon.exists():
        print(f"成功生成图标文件: {output_icon}")
        return True
    else:
        print("生成图标文件失败")
        return False

if __name__ == "__main__":
    # 此脚本仅在macOS上运行
    if sys.platform != "darwin":
        print("此脚本仅支持在macOS上运行")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1) 