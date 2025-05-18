#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
打包脚本，用于将DrissionPage自动化GUI工具打包成独立可执行程序
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """主函数，执行打包流程"""
    print("开始打包DrissionPage自动化GUI工具...")
    
    # 确保在正确的目录中
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 创建临时目录
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    # 清理之前的构建
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 构建PyInstaller命令
    icon_path = ""
    for ext in ['.icns', '.ico', '.png']:
        potential_icon = script_dir / f"app_icon{ext}"
        if potential_icon.exists():
            icon_path = str(potential_icon)
            break
    
    # 准备主脚本路径
    main_script = script_dir / "run_gui_tool.py"
    main_script_str = str(main_script)
    
    cmd = [
        "pyinstaller",
        "--clean",
        "--name=DrissionPage自动化工具",
        "--windowed",  # 使用GUI模式，不显示控制台
        "--onedir",    # 可以改为--onefile生成单文件应用
        "--noconfirm"
    ]
    
    # 添加图标（如果存在）
    if icon_path:
        cmd.append(f"--icon={icon_path}")
    
    # 添加隐藏导入，确保所有需要的库都被包含
    cmd.extend([
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=PIL",
        "--hidden-import=requests",
        "--hidden-import=DrissionPage",
        "--hidden-import=PyQt5",
        "--hidden-import=lxml",
        "--hidden-import=lxml.etree",
        # 添加项目内部模块
        "--hidden-import=drission_gui_tool",
        "--hidden-import=drission_gui_tool.core",
        "--hidden-import=drission_gui_tool.gui",
        "--hidden-import=drission_gui_tool.common",
        "--hidden-import=drission_gui_tool.common.constants",
        "--hidden-import=drission_gui_tool.core.project_manager",
        "--hidden-import=drission_gui_tool.gui.main_window"
    ])
    
    # 添加主脚本
    cmd.append(main_script_str)
    
    # 执行PyInstaller命令
    print(f"执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("打包失败！")
            print("错误输出:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"打包过程中发生错误: {e}")
        return False
    
    print("打包成功！")
    print(f"可执行程序位于: {dist_dir / 'DrissionPage自动化工具'}")
    
    # 添加必要的运行时文件
    runtime_files = ["requirements.txt", "README.md"]
    for file in runtime_files:
        if Path(file).exists():
            shutil.copy(file, dist_dir / "DrissionPage自动化工具")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 