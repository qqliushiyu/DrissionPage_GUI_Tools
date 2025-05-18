#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DrissionPage 自动化 GUI 工具
高级演示流程测试脚本
"""

import sys
import os
import logging

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 将项目根目录添加到模块搜索路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from drission_gui_tool.gui.main_window import MainWindow

def run_advanced_demo():
    """运行高级演示流程"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格，跨平台一致性好
    
    window = MainWindow()
    window.show()
    
    # 连接日志信号到控制台
    window.log_display_widget.log_message_added.connect(lambda msg, level: print(f"[{level}] {msg}"))
    
    logger.info("应用程序已启动，准备创建和运行高级演示流程...")
    
    # 使用定时器延迟执行创建和运行高级演示流程
    QTimer.singleShot(1000, lambda: create_and_run_demo(window))
    
    sys.exit(app.exec_())

def create_and_run_demo(window):
    """创建并运行高级演示流程"""
    logger.info("开始创建高级演示流程...")
    
    # 创建高级演示流程
    window._create_advanced_demo_flow()
    logger.info("高级演示流程创建完成，准备运行...")
    
    # 运行流程
    QTimer.singleShot(500, lambda: run_flow(window))

def run_flow(window):
    """运行流程"""
    logger.info("开始执行高级演示流程...")
    window._handle_start_execution()

if __name__ == "__main__":
    run_advanced_demo() 