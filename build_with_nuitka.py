#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Nuitka打包DrissionPage自动化GUI工具
Nuitka通常可以生成比PyInstaller更小、更快的可执行文件
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import site

def main():
    """使用Nuitka打包应用程序"""
    print("开始使用Nuitka打包DrissionPage自动化GUI工具...")
    
    # 检查Nuitka是否已安装
    try:
        import nuitka
    except ImportError:
        print("错误: Nuitka未安装")
        print("请运行: pip install nuitka")
        return False
    
    # 确保在正确的目录中
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 检查操作系统，设置不同的图标
    icon_file = ""
    if platform.system() == "Darwin":  # macOS
        icon_path = script_dir / "app_icon.icns"
        if icon_path.exists():
            icon_file = str(icon_path)
    elif platform.system() == "Windows":
        icon_path = script_dir / "app_icon.ico"
        if icon_path.exists():
            icon_file = str(icon_path)
    
    # 准备主脚本路径
    main_script = script_dir / "main.py"
    main_script_str = str(main_script)
    
    # 构建Nuitka命令
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--follow-imports",
        "--show-memory",
        "--show-progress",
        "--include-package=DrissionPage",
        "--include-package=PyQt5",
        "--include-package=pandas",
        "--include-package=lxml",
        "--include-package=PIL",
        "--include-package=openpyxl",
        "--include-package=requests",
        "--disable-console",
        f"--output-dir={str(script_dir / 'dist_nuitka')}",
        "--remove-output"
    ]
    
    # 添加解决lxml模块错误的参数
    cmd.extend([
        "--include-module=lxml.etree",
        "--include-module=lxml.sax",
        "--include-module=lxml._elementpath",
        "--noinclude-default-mode=nofollow"
    ])
    
    # 尝试找到lxml包位置并添加数据文件
    try:
        import lxml
        lxml_path = os.path.dirname(lxml.__file__)
        if os.path.exists(lxml_path):
            cmd.append(f"--include-data-dir={lxml_path}={os.path.basename(lxml_path)}")
            print(f"已找到lxml路径: {lxml_path}")
    except ImportError:
        print("警告: 无法导入lxml模块")
    
    # 添加图标（如果存在）
    if icon_file:
        cmd.append(f"--windows-icon-from-ico={icon_file}")
    
    # 添加特定平台选项
    if platform.system() == "Darwin":
        cmd.extend([
            "--macos-create-app-bundle",
            "--macos-app-name=DrissionPage自动化工具",
            "--macos-app-mode=gui"
        ])
    elif platform.system() == "Windows":
        cmd.extend([
            "--windows-uac-admin",
            "--windows-company-name=DrissionPage",
            "--windows-product-name=DrissionPage自动化工具",
            "--windows-file-version=1.0.0.0",
            "--windows-product-version=1.0.0.0",
            "--windows-file-description=DrissionPage自动化GUI工具"
        ])
    
    # 添加主脚本
    cmd.append(main_script_str)
    
    # 执行Nuitka命令
    print(f"执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True)
        success = result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"打包错误: {e}")
        success = False
    except Exception as e:
        print(f"未知错误: {e}")
        success = False
    
    if not success:
        print("打包失败！")
        print("如果问题与lxml模块有关，建议使用以下解决方案：")
        print("1. 尝试使用PyInstaller替代: python build.py")
        print("2. 手动从源码编译lxml后再尝试: pip uninstall lxml && pip install lxml --no-binary=lxml")
        return False
    
    print("打包成功！")
    
    # 输出位置
    dist_nuitka_dir = script_dir / "dist_nuitka"
    if platform.system() == "Darwin":
        print(f"可执行程序位于: {dist_nuitka_dir / 'DrissionPage自动化工具.app'}")
    elif platform.system() == "Windows":
        print(f"可执行程序位于: {dist_nuitka_dir / 'main.exe'}")
    else:
        print(f"可执行程序位于: {dist_nuitka_dir / 'main.bin'}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 