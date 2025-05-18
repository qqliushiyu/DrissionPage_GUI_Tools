@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%===============================================%NC%
echo %BLUE%  DrissionPage自动化GUI工具 - 一键打包脚本（Windows版）%NC%
echo %BLUE%===============================================%NC%
echo.

:: 检查Python环境
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%错误: 未找到Python环境，请先安装Python 3.8+%NC%
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set PYTHON_VERSION=%%a
echo %GREEN%Python版本: %PYTHON_VERSION%%NC%

:: 检查并安装依赖
echo %BLUE%正在检查并安装必要的依赖...%NC%
python -m pip install -q pyinstaller pillow

:: 检查app_icon.png是否存在
if not exist "app_icon.png" (
    echo %YELLOW%警告: 未找到app_icon.png文件%NC%
    echo %YELLOW%如果您想要自定义应用图标，请准备一个1024x1024的PNG图片并命名为app_icon.png%NC%
    
    set /p use_default="是否使用默认图标继续? (y/n) [y]: "
    if "!use_default!"=="" set use_default=y
    
    if /i not "!use_default!"=="y" (
        echo %YELLOW%请准备app_icon.png文件后再运行此脚本%NC%
        pause
        exit /b 0
    )
    
    :: 创建一个简单的默认图标
    echo %BLUE%创建默认图标...%NC%
    python -c "^
from PIL import Image, ImageDraw; ^
img = Image.new('RGBA', (1024, 1024), color=(0, 0, 0, 0)); ^
draw = ImageDraw.Draw(img); ^
draw.ellipse((100, 100, 924, 924), fill=(65, 105, 225, 255)); ^
draw.rectangle((400, 300, 500, 700), fill=(255, 255, 255, 255)); ^
draw.arc((300, 300, 500, 700), 270, 90, fill=(255, 255, 255, 255), width=100); ^
img.save('app_icon.png'); ^
print('已创建默认图标: app_icon.png') ^
    "
) else (
    echo %GREEN%已找到app_icon.png文件%NC%
)

:: 生成Windows图标
echo %BLUE%正在生成Windows应用图标...%NC%
python create_windows_icon.py

:: 选择打包方式
echo.
echo %BLUE%请选择打包方式:%NC%
echo 1) 标准打包 (PyInstaller基本模式，推荐初次使用)
echo 2) 高级打包 (PyInstaller高级模式，使用spec文件)
echo 3) Nuitka打包 (可能生成更小更快的可执行文件，需要额外安装)
echo.
set /p package_method="请输入选择 [1]: "
if "!package_method!"=="" set package_method=1

:: 执行打包
echo.
if "!package_method!"=="1" (
    echo %BLUE%开始标准打包...%NC%
    python build.py
) else if "!package_method!"=="2" (
    echo %BLUE%开始高级打包...%NC%
    python build_advanced.py
) else if "!package_method!"=="3" (
    echo %BLUE%开始Nuitka打包...%NC%
    echo %YELLOW%检查是否安装Nuitka...%NC%
    
    python -c "import nuitka" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo %YELLOW%未找到Nuitka，正在安装...%NC%
        python -m pip install nuitka
    )
    
    python build_with_nuitka.py
) else (
    echo %RED%无效的选择，退出%NC%
    pause
    exit /b 1
)

echo.
echo %GREEN%打包过程完成!%NC%
echo %GREEN%请检查dist目录获取打包结果%NC%
echo.

echo %YELLOW%注意: 在Windows上，您可能需要以管理员身份运行应用程序%NC%

echo.
echo %BLUE%感谢使用DrissionPage自动化GUI工具!%NC%

pause 