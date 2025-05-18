#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主题管理器
实现暗黑模式和自定义主题颜色
"""

from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPalette, QColor

from typing import Dict, Any, List, Optional
import os
import json

# 尝试导入第三方主题库
try:
    import qdarkstyle
    QDARKSTYLE_AVAILABLE = True
except ImportError:
    QDARKSTYLE_AVAILABLE = False

try:
    from qt_material import apply_stylesheet
    QT_MATERIAL_AVAILABLE = True
except ImportError:
    QT_MATERIAL_AVAILABLE = False


class ThemeManager:
    """主题管理器"""
    
    # 主题类型
    THEME_LIGHT = "light"  # 浅色主题
    THEME_DARK = "dark"  # 暗色主题
    THEME_SYSTEM = "system"  # 跟随系统
    THEME_CUSTOM = "custom"  # 自定义主题
    
    # 内置主题
    BUILT_IN_THEMES = {
        "light": "浅色主题",
        "dark": "暗色主题",
        "blue": "蓝色主题",
        "green": "绿色主题",
        "orange": "橙色主题",
        "purple": "紫色主题",
        "red": "红色主题",
        "high_contrast": "高对比度"
    }
    
    def __init__(self, app: QApplication):
        """
        初始化主题管理器
        
        Args:
            app: QApplication实例
        """
        self._app = app
        
        # 当前主题
        self._current_theme = self.THEME_LIGHT
        self._custom_theme = {}
        self._material_theme = ""
        
        # 主题设置
        self._settings = QSettings("DrissionPage", "ThemeManager")
        
        # 恢复上次主题
        self._restore_theme()
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        应用主题
        
        Args:
            theme_name: 主题名称
            
        Returns:
            是否成功应用主题
        """
        # 系统内置主题
        if theme_name == self.THEME_LIGHT:
            return self._apply_light_theme()
        elif theme_name == self.THEME_DARK:
            return self._apply_dark_theme()
        elif theme_name == self.THEME_SYSTEM:
            return self._apply_system_theme()
        elif theme_name == "high_contrast":
            return self._apply_high_contrast_theme()
        
        # Material主题
        elif QT_MATERIAL_AVAILABLE and theme_name in [
            "blue", "green", "orange", "purple", "red"
        ]:
            return self._apply_material_theme(theme_name)
        
        # 自定义主题
        elif theme_name == self.THEME_CUSTOM:
            return self._apply_custom_theme()
        
        # 未知主题
        else:
            return False
    
    def get_current_theme(self) -> str:
        """
        获取当前主题名称
        
        Returns:
            主题名称
        """
        return self._current_theme
    
    def get_available_themes(self) -> Dict[str, str]:
        """
        获取可用主题列表
        
        Returns:
            主题ID和显示名的字典
        """
        themes = {}
        
        # 内置主题
        themes[self.THEME_LIGHT] = "浅色主题"
        themes[self.THEME_DARK] = "暗色主题"
        themes[self.THEME_SYSTEM] = "跟随系统"
        
        # Material主题
        if QT_MATERIAL_AVAILABLE:
            themes.update({
                "blue": "蓝色主题",
                "green": "绿色主题",
                "orange": "橙色主题",
                "purple": "紫色主题",
                "red": "红色主题"
            })
        
        # 高对比度主题
        themes["high_contrast"] = "高对比度"
        
        # 自定义主题
        if self._custom_theme:
            themes[self.THEME_CUSTOM] = "自定义主题"
        
        return themes
    
    def set_custom_theme(self, theme_data: Dict[str, Any]) -> bool:
        """
        设置自定义主题
        
        Args:
            theme_data: 主题数据
            
        Returns:
            是否成功设置
        """
        # 验证主题数据
        if not self._validate_theme_data(theme_data):
            return False
        
        # 保存主题数据
        self._custom_theme = theme_data
        
        # 保存到设置
        self._settings.setValue("custom_theme", json.dumps(theme_data, ensure_ascii=False))
        
        # 如果当前是自定义主题，则应用新主题
        if self._current_theme == self.THEME_CUSTOM:
            return self._apply_custom_theme()
        
        return True
    
    def get_custom_theme(self) -> Dict[str, Any]:
        """
        获取自定义主题数据
        
        Returns:
            主题数据
        """
        return self._custom_theme.copy()
    
    def _validate_theme_data(self, theme_data: Dict[str, Any]) -> bool:
        """
        验证主题数据
        
        Args:
            theme_data: 主题数据
            
        Returns:
            是否有效
        """
        # 必须包含基本颜色
        required_colors = ["window", "text", "highlight", "highlighted_text"]
        for color in required_colors:
            if color not in theme_data:
                return False
        
        return True
    
    def _apply_light_theme(self) -> bool:
        """
        应用浅色主题
        
        Returns:
            是否成功
        """
        # 恢复默认样式
        self._app.setStyle(QStyleFactory.create("Fusion"))
        
        # 设置浅色调色板
        palette = QPalette()
        self._app.setPalette(palette)
        
        # 清除样式表
        self._app.setStyleSheet("")
        
        # 更新当前主题
        self._current_theme = self.THEME_LIGHT
        self._save_theme()
        
        return True
    
    def _apply_dark_theme(self) -> bool:
        """
        应用暗色主题
        
        Returns:
            是否成功
        """
        # 使用内置或第三方暗色主题
        if QDARKSTYLE_AVAILABLE:
            # 使用QDarkStyle
            self._app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            # 使用自定义暗色调色板
            self._app.setStyle(QStyleFactory.create("Fusion"))
            
            dark_palette = QPalette()
            
            # 设置暗色调色板
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            
            # 应用调色板
            self._app.setPalette(dark_palette)
            
            # 添加一些额外的样式
            self._app.setStyleSheet("""
                QToolTip { 
                    color: #ffffff; 
                    background-color: #2a82da; 
                    border: 1px solid white; 
                }
                
                QMenu::item:selected { 
                    background-color: #2a82da;
                }
            """)
        
        # 更新当前主题
        self._current_theme = self.THEME_DARK
        self._save_theme()
        
        return True
    
    def _apply_system_theme(self) -> bool:
        """
        应用系统主题
        
        Returns:
            是否成功
        """
        # 尝试检测系统主题
        if hasattr(QApplication, "isDarkMode") and callable(getattr(QApplication, "isDarkMode")):
            # PyQt5.15.4+
            if QApplication.isDarkMode():
                return self._apply_dark_theme()
            else:
                return self._apply_light_theme()
        else:
            # 无法检测系统主题，默认使用浅色主题
            return self._apply_light_theme()
    
    def _apply_high_contrast_theme(self) -> bool:
        """
        应用高对比度主题
        
        Returns:
            是否成功
        """
        # 设置高对比度调色板
        self._app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        
        # 黑色背景，白色文字
        palette.setColor(QPalette.Window, Qt.black)
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, Qt.black)
        palette.setColor(QPalette.AlternateBase, QColor(10, 10, 10))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, Qt.black)
        palette.setColor(QPalette.ButtonText, Qt.white)
        
        # 高对比度高亮（黄色）
        palette.setColor(QPalette.Highlight, QColor(255, 255, 0))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # 链接颜色（鲜亮的蓝色）
        palette.setColor(QPalette.Link, QColor(0, 255, 255))
        
        # 应用调色板
        self._app.setPalette(palette)
        
        # 添加一些额外的样式
        self._app.setStyleSheet("""
            QToolTip { 
                color: #000000; 
                background-color: #ffff00; 
                border: 1px solid white; 
            }
            
            QMenu::item:selected { 
                background-color: #ffff00;
                color: #000000;
            }
            
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
            
            QPushButton {
                background-color: #000000;
                color: #ffffff;
                border: 2px solid #ffffff;
                padding: 4px;
            }
            
            QPushButton:hover {
                background-color: #303030;
            }
            
            QPushButton:pressed {
                background-color: #ffff00;
                color: #000000;
            }
        """)
        
        # 更新当前主题
        self._current_theme = "high_contrast"
        self._save_theme()
        
        return True
    
    def _apply_material_theme(self, theme_name: str) -> bool:
        """
        应用Material主题
        
        Args:
            theme_name: 主题名称
            
        Returns:
            是否成功
        """
        if not QT_MATERIAL_AVAILABLE:
            return False
        
        # 映射主题名称为qt-material主题
        theme_map = {
            "blue": "light_blue",
            "green": "light_green",
            "orange": "amber",
            "purple": "purple",
            "red": "red"
        }
        
        material_theme = theme_map.get(theme_name)
        if not material_theme:
            return False
        
        # 应用Material主题
        apply_stylesheet(self._app, theme=material_theme)
        
        # 更新当前主题
        self._current_theme = theme_name
        self._material_theme = material_theme
        self._save_theme()
        
        return True
    
    def _apply_custom_theme(self) -> bool:
        """
        应用自定义主题
        
        Returns:
            是否成功
        """
        if not self._custom_theme:
            return False
        
        # 设置自定义调色板
        self._app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        
        # 设置基本颜色
        for role_name, color_str in self._custom_theme.items():
            if hasattr(QPalette, role_name):
                role = getattr(QPalette, role_name)
                palette.setColor(role, QColor(color_str))
        
        # 应用调色板
        self._app.setPalette(palette)
        
        # 更新当前主题
        self._current_theme = self.THEME_CUSTOM
        self._save_theme()
        
        return True
    
    def _save_theme(self):
        """保存主题设置"""
        self._settings.setValue("current_theme", self._current_theme)
        
        if self._current_theme == self.THEME_CUSTOM:
            self._settings.setValue("custom_theme", json.dumps(self._custom_theme, ensure_ascii=False))
        elif QT_MATERIAL_AVAILABLE and self._material_theme:
            self._settings.setValue("material_theme", self._material_theme)
    
    def _restore_theme(self):
        """恢复主题设置"""
        # 恢复自定义主题
        custom_theme = self._settings.value("custom_theme", "")
        if custom_theme:
            try:
                self._custom_theme = json.loads(custom_theme)
            except:
                self._custom_theme = {}
        
        # 恢复Material主题
        self._material_theme = self._settings.value("material_theme", "")
        
        # 恢复当前主题
        theme = self._settings.value("current_theme", self.THEME_LIGHT)
        if theme:
            self.apply_theme(theme)
        else:
            self._apply_light_theme() 