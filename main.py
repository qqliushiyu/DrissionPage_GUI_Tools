#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DrissionPage 自动化 GUI 工具
主程序入口
"""

import sys
import os

# 将项目根目录添加到模块搜索路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication, QStyleFactory, QAction, QMenu
from PyQt5.QtCore import QSettings
from drission_gui_tool.gui.main_window import MainWindow
from drission_gui_tool.gui.widgets.theme_manager import ThemeManager

def main():
    """
    应用程序主入口
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格，跨平台一致性好
    
    # 创建主题管理器
    theme_manager = ThemeManager(app)
    
    # 创建主窗口
    window = MainWindow()
    
    # 添加主题菜单
    theme_menu = QMenu("主题", window.menuBar())
    window.menuBar().addMenu(theme_menu)
    
    # 添加主题切换操作
    themes = theme_manager.get_available_themes()
    theme_actions = {}
    
    for theme_id, theme_name in themes.items():
        action = QAction(theme_name, window)
        action.setCheckable(True)
        
        # 检查是否为当前主题
        if theme_id == theme_manager.get_current_theme():
            action.setChecked(True)
        
        # 设置切换主题的处理函数
        action.triggered.connect(lambda checked, tid=theme_id: 
                               _switch_theme(theme_manager, theme_actions, tid))
        
        theme_menu.addAction(action)
        theme_actions[theme_id] = action
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

def _switch_theme(theme_manager, theme_actions, theme_id):
    """
    切换主题
    
    Args:
        theme_manager: 主题管理器
        theme_actions: 主题操作字典
        theme_id: 主题ID
    """
    # 应用主题
    success = theme_manager.apply_theme(theme_id)
    
    if success:
        # 更新选中状态
        for tid, action in theme_actions.items():
            action.setChecked(tid == theme_id)

if __name__ == "__main__":
    main()
