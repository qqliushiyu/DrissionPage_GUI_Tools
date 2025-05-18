#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级打包脚本，使用PyInstaller的spec文件实现更精细的控制
"""

import os
import sys
import shutil
import platform
from pathlib import Path

def main():
    """主函数，执行高级打包流程"""
    print("开始高级打包DrissionPage自动化GUI工具...")
    
    # 确保在正确的目录中
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 创建spec文件
    spec_path = create_spec_file(script_dir)
    
    # 使用spec文件构建
    os.system(f'pyinstaller --clean --noconfirm "{spec_path}"')
    
    print("打包完成，检查dist目录获取可执行程序")
    return True

def create_spec_file(script_dir):
    """创建PyInstaller spec文件"""
    app_name = "DrissionPage自动化工具"
    
    # 检测操作系统，设置不同的图标
    icon_file = ""
    if platform.system() == "Darwin":  # macOS
        icon_path = script_dir / "app_icon.icns"
        if icon_path.exists():
            icon_file = str(icon_path)
    elif platform.system() == "Windows":
        icon_path = script_dir / "app_icon.ico"
        if icon_path.exists():
            icon_file = str(icon_path)
    
    # 正确处理包含空格的路径
    run_script_path = script_dir / "main.py"
    script_dir_str = str(script_dir).replace("'", "\\'")
    run_script_path_str = str(run_script_path).replace("'", "\\'")
    
    # 为macOS创建BUNDLE部分处理图标
    bundle_icon_line = ""
    if platform.system() == "Darwin":
        if icon_file:
            bundle_icon_line = f'icon=r"{icon_file}",'
        else:
            bundle_icon_line = 'icon=None,'
    
    # 创建spec文件内容
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import sys
import platform
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 获取DrissionPage的所有子模块
drission_imports = collect_submodules('DrissionPage')
pandas_imports = collect_submodules('pandas')
pyqt_imports = collect_submodules('PyQt5')

# 收集数据文件
datas = []
datas += collect_data_files('DrissionPage')
 
a = Analysis(
    [r'{run_script_path_str}'],
    pathex=[r'{script_dir_str}'],
    binaries=[],
    datas=datas,
    hiddenimports=drission_imports + pandas_imports + pyqt_imports + [
        'pandas',
        'openpyxl',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'json',
        'logging',
        'sqlite3',
        'lxml',
        'lxml.etree',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['_gtkagg', '_tkagg', 'botocore', 'boto3', 'pytest', 'doctest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {f"icon=r'{icon_file}'" if icon_file else ''}
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)

# macOS应用程序包
if platform.system() == "Darwin":
    app = BUNDLE(
        coll,
        name='{app_name}.app',
        {bundle_icon_line}
        bundle_identifier='com.drissionpage.guitool',
        info_plist={{
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {{
                    'CFBundleTypeName': 'DrissionPage GUI Tool Flow',
                    'CFBundleTypeExtensions': ['dgflow'],
                    'CFBundleTypeRole': 'Editor',
                }}
            ]
        }},
    )
"""
    
    # 写入spec文件
    spec_path = script_dir / f"{app_name}.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"spec文件已创建: {spec_path}")
    return spec_path

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 