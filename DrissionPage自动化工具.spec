# -*- mode: python ; coding: utf-8 -*-

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
    [r'/Users/leaymacbookpro/Desktop/Desktop/DrissionPage 自动化 GUI 工具/drission_gui_tool/main.py'],
    pathex=[r'/Users/leaymacbookpro/Desktop/Desktop/DrissionPage 自动化 GUI 工具/drission_gui_tool'],
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
    hooksconfig={},
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
    name='DrissionPage自动化工具',
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
    
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DrissionPage自动化工具',
)

# macOS应用程序包
if platform.system() == "Darwin":
    app = BUNDLE(
        coll,
        name='DrissionPage自动化工具.app',
        icon=None,
        bundle_identifier='com.drissionpage.guitool',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'DrissionPage GUI Tool Flow',
                    'CFBundleTypeExtensions': ['dgflow'],
                    'CFBundleTypeRole': 'Editor',
                }
            ]
        },
    )
