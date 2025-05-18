#!/bin/bash

# 一键打包DrissionPage自动化GUI工具
# 此脚本会自动检测系统、创建图标并执行打包操作

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}  DrissionPage自动化GUI工具 - 一键打包脚本${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    
        SYSTEM="MacOS"
        ICON_SCRIPT="create_macos_icon.py"
        ;;
    Linux*)     
        SYSTEM="Linux"
        ICON_SCRIPT=""
        ;;
    MINGW*|MSYS*|CYGWIN*)    
        SYSTEM="Windows"
        ICON_SCRIPT="create_windows_icon.py"
        ;;
    *)          
        SYSTEM="UNKNOWN"
        ICON_SCRIPT=""
        ;;
esac

echo -e "${GREEN}检测到您的系统是: ${SYSTEM}${NC}"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}错误: 未找到Python环境，请先安装Python 3.8+${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo -e "${GREEN}Python版本: ${PYTHON_VERSION}${NC}"

# 检查并安装依赖
echo -e "${BLUE}正在检查并安装必要的依赖...${NC}"
$PYTHON_CMD -m pip install -q pyinstaller pillow

# 检查app_icon.png是否存在
if [ ! -f "app_icon.png" ]; then
    echo -e "${YELLOW}警告: 未找到app_icon.png文件${NC}"
    echo -e "${YELLOW}如果您想要自定义应用图标，请准备一个1024x1024的PNG图片并命名为app_icon.png${NC}"
    echo -e "${YELLOW}是否使用默认图标继续? (y/n)${NC}"
    read -p "请输入选择 [y]: " use_default
    use_default=${use_default:-y}
    
    if [ "$use_default" != "y" ] && [ "$use_default" != "Y" ]; then
        echo -e "${YELLOW}请准备app_icon.png文件后再运行此脚本${NC}"
        exit 0
    fi
    
    # 创建一个简单的默认图标
    echo -e "${BLUE}创建默认图标...${NC}"
    # 使用Python生成一个简单的图标
    $PYTHON_CMD -c "
from PIL import Image, ImageDraw
import os

# 创建1024x1024的透明背景图像
img = Image.new('RGBA', (1024, 1024), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 绘制蓝色圆形
draw.ellipse((100, 100, 924, 924), fill=(65, 105, 225, 255))

# 绘制白色字母'D'
draw.rectangle((400, 300, 500, 700), fill=(255, 255, 255, 255))
draw.arc((300, 300, 500, 700), 270, 90, fill=(255, 255, 255, 255), width=100)

# 保存图片
img.save('app_icon.png')
print('已创建默认图标: app_icon.png')
    "
else
    echo -e "${GREEN}已找到app_icon.png文件${NC}"
fi

# 如果有对应平台的图标生成脚本，就运行它
if [ -n "$ICON_SCRIPT" ]; then
    echo -e "${BLUE}正在生成${SYSTEM}应用图标...${NC}"
    $PYTHON_CMD "$ICON_SCRIPT"
fi

# 选择打包方式
echo ""
echo -e "${BLUE}请选择打包方式:${NC}"
echo "1) 标准打包 (PyInstaller基本模式，推荐初次使用)"
echo "2) 高级打包 (PyInstaller高级模式，使用spec文件)"
echo "3) Nuitka打包 (可能生成更小更快的可执行文件，需要额外安装)"
echo ""
read -p "请输入选择 [1]: " package_method
package_method=${package_method:-1}

# 执行打包
echo ""
case $package_method in
    1)
        echo -e "${BLUE}开始标准打包...${NC}"
        $PYTHON_CMD build.py
        ;;
    2)
        echo -e "${BLUE}开始高级打包...${NC}"
        $PYTHON_CMD build_advanced.py
        ;;
    3)
        echo -e "${BLUE}开始Nuitka打包...${NC}"
        echo -e "${YELLOW}检查是否安装Nuitka...${NC}"
        if ! $PYTHON_CMD -c "import nuitka" &> /dev/null; then
            echo -e "${YELLOW}未找到Nuitka，正在安装...${NC}"
            $PYTHON_CMD -m pip install nuitka
        fi
        $PYTHON_CMD build_with_nuitka.py
        ;;
    *)
        echo -e "${RED}无效的选择，退出${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}打包过程完成!${NC}"
echo -e "${GREEN}请检查dist目录获取打包结果${NC}"
echo ""

# 打包后的提示
if [ "$SYSTEM" = "MacOS" ]; then
    echo -e "${YELLOW}注意: 在macOS上，您可能需要为应用程序赋予执行权限:${NC}"
    echo -e "chmod +x \"dist/DrissionPage自动化工具/DrissionPage自动化工具.app/Contents/MacOS/DrissionPage自动化工具\""
elif [ "$SYSTEM" = "Windows" ]; then
    echo -e "${YELLOW}注意: 在Windows上，您可能需要以管理员身份运行应用程序${NC}"
fi

echo ""
echo -e "${BLUE}感谢使用DrissionPage自动化GUI工具!${NC}" 