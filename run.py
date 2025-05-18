#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运行入口脚本
"""

import sys
import os

# 将项目根目录添加到Python模块搜索路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 然后导入main模块
from drission_gui_tool.main import main

if __name__ == "__main__":
    main() 