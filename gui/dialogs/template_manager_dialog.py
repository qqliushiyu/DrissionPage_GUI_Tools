#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模板管理对话框模块，提供模板的浏览、导入、导出等功能。
"""

from PyQt5.QtWidgets import (
    QDialog, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QMessageBox, 
    QLineEdit, QLabel, QHeaderView, QFileDialog, QInputDialog,
    QGroupBox, QWidget, QFormLayout, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSlot, QSize
from PyQt5.QtGui import QIcon

from typing import Dict, List, Tuple, Any, Optional, Union
import os
import time
import json

from drission_gui_tool.core.template_manager import TemplateManager
from drission_gui_tool.common.constants import TEMPLATE_FILE_EXTENSION, TEMPLATE_FILE_FILTER


class TemplateTableWidget(QTableWidget):
    """模板列表表格控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置列
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["名称", "描述", "更新时间", "ID"])
        
        # 设置表格属性
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置列宽
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # 添加右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        # 创建右键菜单
        menu = QMenu(self)
        edit_action = menu.addAction("编辑模板")
        delete_action = menu.addAction("删除模板")
        menu.addSeparator()
        export_action = menu.addAction("导出模板")
        
        # 显示菜单并获取选中的操作
        action = menu.exec_(self.mapToGlobal(pos))
        
        # 根据选中的操作触发相应的信号
        if action == edit_action:
            self.edit_template()
        elif action == delete_action:
            self.delete_template()
        elif action == export_action:
            self.export_template()
    
    def edit_template(self):
        """编辑模板"""
        # 获取选中的模板信息
        template_info = self.get_selected_template_info()
        if not template_info:
            QMessageBox.warning(self, "编辑失败", "请先选择一个模板")
            return
        
        template_id = template_info.get("id")
        category_id = template_info.get("category")
        
        if not template_id or not category_id:
            QMessageBox.warning(self, "编辑失败", "模板信息不完整")
            return
        
        # 获取模板管理器 - 查找父级对话框
        parent_dialog = self
        while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
            parent_dialog = parent_dialog.parent()
            
        if not parent_dialog:
            QMessageBox.warning(self, "编辑失败", "无法获取模板管理器")
            return
            
        template_manager = parent_dialog.get_template_manager()
        
        # 加载完整模板数据
        success, template_data = template_manager.load_template(template_id, category_id)
        if not success:
            QMessageBox.warning(self, "编辑失败", f"加载模板失败: {template_data}")
            return
        
        # 获取模板名称
        name, ok = QInputDialog.getText(
            self, "编辑模板", "模板名称:", 
            text=template_data.get("template_name", "")
        )
        if not ok:
            return
        
        # 获取模板描述
        description, ok = QInputDialog.getText(
            self, "编辑模板", "模板描述:", 
            text=template_data.get("description", "")
        )
        if not ok:
            return
        
        # 更新模板数据
        template_data["template_name"] = name
        template_data["description"] = description
        template_data["updated_at"] = time.time()
        
        # 保存模板数据
        success, result = template_manager.save_template(template_data, category_id)
        if success:
            QMessageBox.information(self, "保存成功", f"模板已保存")
            # 刷新模板列表 - 查找父级对话框
            parent_dialog = self
            while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
                parent_dialog = parent_dialog.parent()
                
            if parent_dialog:
                parent_dialog.refresh_templates()
        else:
            QMessageBox.warning(self, "保存失败", result)
    
    def delete_template(self):
        """删除模板"""
        # 获取选中的模板信息
        template_info = self.get_selected_template_info()
        if not template_info:
            QMessageBox.warning(self, "删除失败", "请先选择一个模板")
            return
        
        template_id = template_info.get("id")
        category_id = template_info.get("category")
        template_name = template_info.get("name", "未命名模板")
        
        if not template_id or not category_id:
            QMessageBox.warning(self, "删除失败", "模板信息不完整")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, "删除确认",
            f"确定要删除模板 '{template_name}' 吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        # 获取模板管理器 - 查找父级对话框
        parent_dialog = self
        while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
            parent_dialog = parent_dialog.parent()
            
        if not parent_dialog:
            QMessageBox.warning(self, "删除失败", "无法获取模板管理器")
            return
            
        template_manager = parent_dialog.get_template_manager()
        
        # 删除模板
        success, message = template_manager.delete_template(template_id, category_id)
        if success:
            QMessageBox.information(self, "删除成功", message)
            # 刷新模板列表 - 查找父级对话框
            parent_dialog = self
            while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
                parent_dialog = parent_dialog.parent()
                
            if parent_dialog:
                parent_dialog.refresh_templates()
        else:
            QMessageBox.warning(self, "删除失败", message)
    
    def export_template(self):
        """导出模板"""
        # 获取选中的模板信息
        template_info = self.get_selected_template_info()
        if not template_info:
            QMessageBox.warning(self, "导出失败", "请先选择一个模板")
            return
        
        template_id = template_info.get("id")
        category_id = template_info.get("category")
        template_name = template_info.get("name", "未命名模板")
        
        if not template_id or not category_id:
            QMessageBox.warning(self, "导出失败", "模板信息不完整")
            return
        
        # 选择导出路径
        export_path, _ = QFileDialog.getSaveFileName(
            self, "导出模板", 
            f"{template_name}{TEMPLATE_FILE_EXTENSION}",
            TEMPLATE_FILE_FILTER
        )
        
        if not export_path:
            return
        
        # 确保文件扩展名正确
        if not export_path.endswith(TEMPLATE_FILE_EXTENSION):
            export_path += TEMPLATE_FILE_EXTENSION
        
        # 获取模板管理器 - 查找父级对话框
        parent_dialog = self
        while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
            parent_dialog = parent_dialog.parent()
            
        if not parent_dialog:
            QMessageBox.warning(self, "导出失败", "无法获取模板管理器")
            return
            
        template_manager = parent_dialog.get_template_manager()
        
        # 导出模板
        success, message = template_manager.export_template(template_id, category_id, export_path)
        if success:
            QMessageBox.information(self, "导出成功", f"模板已导出到:\n{export_path}")
        else:
            QMessageBox.warning(self, "导出失败", message)
    
    def get_selected_template_id(self) -> Optional[str]:
        """获取选中的模板ID"""
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        id_item = self.item(row, 3)  # ID 列
        
        return id_item.text() if id_item else None
    
    def get_selected_template_info(self) -> Optional[Dict[str, Any]]:
        """获取选中的模板信息"""
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        id_item = self.item(row, 3)  # ID 列
        
        if id_item:
            # 从用户数据中获取完整的模板信息
            return id_item.data(Qt.UserRole)
        
        return None
    
    def populate_templates(self, templates: List[Dict[str, Any]]) -> None:
        """
        填充模板数据到表格
        
        Args:
            templates: 模板数据列表
        """
        self.setRowCount(0)  # 清空表格
        
        for row, template in enumerate(templates):
            self.insertRow(row)
            
            # 设置模板名称
            name_item = QTableWidgetItem(template.get("name", "未命名模板"))
            self.setItem(row, 0, name_item)
            
            # 设置描述
            description = template.get("description", "")
            if len(description) > 100:
                description = description[:100] + "..."
            self.setItem(row, 1, QTableWidgetItem(description))
            
            # 设置更新时间
            updated_at = template.get("updated_at", 0)
            if updated_at:
                from datetime import datetime
                time_str = datetime.fromtimestamp(updated_at).strftime("%Y-%m-%d %H:%M")
                self.setItem(row, 2, QTableWidgetItem(time_str))
            else:
                self.setItem(row, 2, QTableWidgetItem("未知"))
            
            # 设置ID
            id_item = QTableWidgetItem(template.get("id", ""))
            id_item.setData(Qt.UserRole, template)  # 存储完整模板数据
            self.setItem(row, 3, id_item)


class TemplateCategoryTree(QTreeWidget):
    """模板分类树控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置树控件属性
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setMinimumWidth(150)
        
        # 添加右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.itemAt(pos)
        if not item:
            # 空白区域右键
            menu = QMenu(self)
            add_category_action = menu.addAction("添加分类")
            
            action = menu.exec_(self.mapToGlobal(pos))
            
            if action == add_category_action:
                self.add_category()
        else:
            # 分类项右键
            menu = QMenu(self)
            rename_action = menu.addAction("重命名分类")
            delete_action = menu.addAction("删除分类")
            
            action = menu.exec_(self.mapToGlobal(pos))
            
            if action == rename_action:
                self.rename_category(item)
            elif action == delete_action:
                self.delete_category(item)
    
    def add_category(self):
        """添加分类"""
        # 获取分类ID
        category_id, ok = QInputDialog.getText(
            self, "添加分类", "分类ID (仅使用字母、数字和下划线):"
        )
        if not ok or not category_id:
            return
        
        # 验证分类ID格式
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', category_id):
            QMessageBox.warning(
                self, "格式错误", 
                "分类ID仅能包含字母、数字和下划线"
            )
            return
        
        # 获取分类显示名称
        display_name, ok = QInputDialog.getText(
            self, "添加分类", "分类显示名称:"
        )
        if not ok or not display_name:
            return
        
        # 获取模板管理器 - 查找父级对话框
        parent_dialog = self
        while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
            parent_dialog = parent_dialog.parent()
            
        if not parent_dialog:
            QMessageBox.warning(self, "添加失败", "无法获取模板管理器")
            return
            
        template_manager = parent_dialog.get_template_manager()
        
        # 添加分类
        success, message = template_manager.add_category(category_id, display_name)
        
        if success:
            QMessageBox.information(self, "添加成功", message)
            # 刷新分类列表 - 查找父级对话框
            parent_dialog = self
            while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
                parent_dialog = parent_dialog.parent()
                
            if parent_dialog:
                parent_dialog._refresh_categories()
        else:
            QMessageBox.warning(self, "添加失败", message)
    
    def rename_category(self, item):
        """重命名分类"""
        # 获取分类ID
        category_id = item.data(0, Qt.UserRole)
        if not category_id:
            QMessageBox.warning(self, "无效的分类", "无法获取分类ID")
            return
        
        # 获取当前显示名称
        current_name = item.text(0)
        
        # 获取新的显示名称
        new_name, ok = QInputDialog.getText(
            self, "重命名分类", "分类显示名称:", 
            text=current_name
        )
        if not ok or not new_name or new_name == current_name:
            return
        
        # 获取模板管理器 - 查找父级对话框
        parent_dialog = self
        while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
            parent_dialog = parent_dialog.parent()
            
        if not parent_dialog:
            QMessageBox.warning(self, "重命名失败", "无法获取模板管理器")
            return
            
        template_manager = parent_dialog.get_template_manager()
        
        # 重命名分类
        success, message = template_manager.rename_category(category_id, new_name)
        
        if success:
            QMessageBox.information(self, "重命名成功", message)
            # 刷新分类列表 - 查找父级对话框
            parent_dialog = self
            while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
                parent_dialog = parent_dialog.parent()
                
            if parent_dialog:
                parent_dialog._refresh_categories()
        else:
            QMessageBox.warning(self, "重命名失败", message)
    
    def delete_category(self, item):
        """删除分类"""
        # 获取分类ID和显示名称
        category_id = item.data(0, Qt.UserRole)
        display_name = item.text(0)
        
        if not category_id:
            QMessageBox.warning(self, "无效的分类", "无法获取分类ID")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, "删除确认",
            f"确定要删除分类 '{display_name}' 吗？\n注意: 只能删除不包含模板的空分类。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        # 获取模板管理器 - 查找父级对话框
        parent_dialog = self
        while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
            parent_dialog = parent_dialog.parent()
            
        if not parent_dialog:
            QMessageBox.warning(self, "删除失败", "无法获取模板管理器")
            return
            
        template_manager = parent_dialog.get_template_manager()
        
        # 删除分类
        success, message = template_manager.delete_category(category_id)
        
        if success:
            QMessageBox.information(self, "删除成功", message)
            # 刷新分类列表 - 查找父级对话框
            parent_dialog = self
            while parent_dialog and not isinstance(parent_dialog, TemplateManagerDialog):
                parent_dialog = parent_dialog.parent()
                
            if parent_dialog:
                parent_dialog._refresh_categories()
        else:
            QMessageBox.warning(self, "删除失败", message)
    
    def populate_categories(self, categories: Dict[str, str]) -> None:
        """
        填充分类数据到树控件
        
        Args:
            categories: 分类数据字典 {category_id: display_name}
        """
        self.clear()  # 清空树
        
        for category_id, display_name in categories.items():
            item = QTreeWidgetItem(self)
            item.setText(0, display_name)
            item.setData(0, Qt.UserRole, category_id)
    
    def get_selected_category_id(self) -> Optional[str]:
        """获取选中的分类ID"""
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        item = selected_items[0]
        return item.data(0, Qt.UserRole)


class TemplateManagerDialog(QDialog):
    """模板管理对话框"""
    
    def __init__(self, parent=None, template_manager: TemplateManager = None):
        """
        初始化模板管理对话框
        
        Args:
            parent: 父窗口
            template_manager: 模板管理器实例
        """
        super().__init__(parent)
        
        # 初始化成员变量
        self._template_manager = template_manager or TemplateManager()
        self._selected_template = None
        
        # 初始化UI
        self._init_ui()
        
        # 刷新分类和模板
        self._refresh_all()
        
        # 设置窗口标题和大小
        self.setWindowTitle("模板管理")
        self.resize(800, 600)

    def _init_ui(self) -> None:
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧分类树
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加分类标题和搜索框
        category_header = QHBoxLayout()
        category_label = QLabel("模板分类")
        category_header.addWidget(category_label)
        
        left_layout.addLayout(category_header)
        
        # 添加分类树
        self.category_tree = TemplateCategoryTree()
        self.category_tree.itemSelectionChanged.connect(self._on_category_selected)
        left_layout.addWidget(self.category_tree)
        
        # 添加分类操作按钮
        category_buttons = QHBoxLayout()
        
        self.add_category_button = QPushButton("添加分类")
        self.add_category_button.clicked.connect(self._add_category)
        
        self.rename_category_button = QPushButton("重命名")
        self.rename_category_button.clicked.connect(self._rename_category)
        
        self.delete_category_button = QPushButton("删除")
        self.delete_category_button.clicked.connect(self._delete_category)
        
        category_buttons.addWidget(self.add_category_button)
        category_buttons.addWidget(self.rename_category_button)
        category_buttons.addWidget(self.delete_category_button)
        
        left_layout.addLayout(category_buttons)
        
        # 右侧模板列表
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加模板列表标题和搜索框
        template_header = QHBoxLayout()
        
        template_label = QLabel("模板列表")
        template_header.addWidget(template_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索模板...")
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        template_header.addWidget(self.search_edit)
        
        right_layout.addLayout(template_header)
        
        # 添加模板表格
        self.template_table = TemplateTableWidget()
        self.template_table.doubleClicked.connect(self._on_template_double_clicked)
        right_layout.addWidget(self.template_table)
        
        # 添加模板操作按钮
        template_buttons = QHBoxLayout()
        
        self.import_button = QPushButton("导入模板")
        self.import_button.clicked.connect(self._import_template)
        
        self.export_button = QPushButton("导出模板")
        self.export_button.clicked.connect(self._export_template)
        
        self.apply_button = QPushButton("应用模板")
        self.apply_button.clicked.connect(self._apply_template)
        self.apply_button.setEnabled(False)  # 初始禁用
        
        template_buttons.addWidget(self.import_button)
        template_buttons.addWidget(self.export_button)
        template_buttons.addStretch()
        template_buttons.addWidget(self.apply_button)
        
        right_layout.addLayout(template_buttons)
        
        # 添加左右部件到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # 设置初始分割比例
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        
        # 底部按钮
        bottom_buttons = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self._refresh_all)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        
        bottom_buttons.addWidget(self.refresh_button)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.close_button)
        
        main_layout.addLayout(bottom_buttons)
    
    def _refresh_categories(self) -> None:
        """刷新分类列表"""
        categories = self._template_manager.get_categories()
        self.category_tree.populate_categories(categories)
    
    def _refresh_templates(self, category_id: Optional[str] = None) -> None:
        """
        刷新模板列表
        
        Args:
            category_id: 分类ID，如果为None则使用当前选中的分类
        """
        if category_id is None:
            category_id = self.category_tree.get_selected_category_id()
        
        if category_id:
            templates = self._template_manager.get_templates_in_category(category_id)
            self.template_table.populate_templates(templates)
        else:
            # 清空模板列表
            self.template_table.setRowCount(0)
    
    def _refresh_all(self) -> None:
        """刷新所有数据"""
        self._refresh_categories()
        self._refresh_templates()
    
    def _on_category_selected(self) -> None:
        """当分类被选中时"""
        category_id = self.category_tree.get_selected_category_id()
        if category_id:
            self._refresh_templates(category_id)
    
    def _on_search_text_changed(self, text: str) -> None:
        """当搜索文本变化时"""
        # 实现搜索逻辑
        pass
    
    def _on_template_double_clicked(self, index) -> None:
        """当模板被双击时"""
        template_info = self.template_table.get_selected_template_info()
        if template_info:
            # 触发应用模板操作
            self._apply_template()
    
    def _add_category(self) -> None:
        """添加分类"""
        category_id, ok = QInputDialog.getText(
            self, "添加分类", "请输入分类ID (仅英文字母和数字):"
        )
        
        if ok and category_id:
            # 检查ID格式
            if not all(c.isalnum() or c == '_' for c in category_id):
                QMessageBox.warning(self, "格式错误", "分类ID只能包含英文字母、数字和下划线")
                return
            
            display_name, ok = QInputDialog.getText(
                self, "添加分类", "请输入分类显示名称:"
            )
            
            if ok and display_name:
                success, message = self._template_manager.add_category(category_id, display_name)
                
                if success:
                    self._refresh_categories()
                    QMessageBox.information(self, "操作成功", message)
                else:
                    QMessageBox.warning(self, "操作失败", message)
    
    def _rename_category(self) -> None:
        """重命名分类"""
        category_id = self.category_tree.get_selected_category_id()
        if not category_id:
            QMessageBox.warning(self, "未选择", "请先选择要重命名的分类")
            return
        
        display_name, ok = QInputDialog.getText(
            self, "重命名分类", "请输入新的分类显示名称:",
            text=self.category_tree.selectedItems()[0].text(0)
        )
        
        if ok and display_name:
            success, message = self._template_manager.rename_category(category_id, display_name)
            
            if success:
                self._refresh_categories()
                QMessageBox.information(self, "操作成功", message)
            else:
                QMessageBox.warning(self, "操作失败", message)
    
    def _delete_category(self) -> None:
        """删除分类"""
        category_id = self.category_tree.get_selected_category_id()
        if not category_id:
            QMessageBox.warning(self, "未选择", "请先选择要删除的分类")
            return
        
        # 确认删除
        category_name = self.category_tree.selectedItems()[0].text(0)
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除分类 '{category_name}' 吗？\n注意：如果分类中包含模板，将无法删除。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self._template_manager.delete_category(category_id)
            
            if success:
                self._refresh_categories()
                QMessageBox.information(self, "操作成功", message)
            else:
                QMessageBox.warning(self, "操作失败", message)
    
    def _import_template(self) -> None:
        """导入模板"""
        category_id = self.category_tree.get_selected_category_id()
        if not category_id:
            QMessageBox.warning(self, "未选择", "请先选择要导入到的分类")
            return
        
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模板文件", "", TEMPLATE_FILE_FILTER
        )
        
        if file_path:
            success, result = self._template_manager.import_template(file_path, category_id)
            
            if success:
                self._refresh_templates(category_id)
                QMessageBox.information(self, "导入成功", f"模板已导入，ID: {result}")
            else:
                QMessageBox.warning(self, "导入失败", result)
    
    def _export_template(self) -> None:
        """导出模板"""
        template_info = self.template_table.get_selected_template_info()
        if not template_info:
            QMessageBox.warning(self, "未选择", "请先选择要导出的模板")
            return
        
        # 获取模板ID和分类
        template_id = template_info.get("id")
        category_id = template_info.get("category")
        
        if not template_id or not category_id:
            QMessageBox.warning(self, "数据错误", "模板数据不完整")
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存模板文件", 
            f"{template_info.get('name', template_id)}{TEMPLATE_FILE_EXTENSION}",
            TEMPLATE_FILE_FILTER
        )
        
        if file_path:
            success, message = self._template_manager.export_template(
                template_id, category_id, file_path
            )
            
            if success:
                QMessageBox.information(self, "导出成功", message)
            else:
                QMessageBox.warning(self, "导出失败", message)
    
    def _apply_template(self) -> None:
        """应用模板"""
        template_info = self.template_table.get_selected_template_info()
        if not template_info:
            QMessageBox.warning(self, "未选择", "请先选择要应用的模板")
            return
            
        # 这里应该实现应用模板的逻辑
        # 由于需要和外部控制器交互，这里只返回模板数据
        self.template_to_apply = template_info
        self.accept()
    
    def get_selected_template(self) -> Optional[Dict[str, Any]]:
        """
        获取选择的模板信息
        
        Returns:
            选中的模板信息，如果没有选中则返回None
        """
        return getattr(self, "template_to_apply", None)
    
    def get_template_manager(self) -> TemplateManager:
        """获取模板管理器实例"""
        return self._template_manager
    
    def refresh_templates(self) -> None:
        """刷新模板列表"""
        current_category = self.category_tree.get_selected_category_id()
        self._refresh_templates(current_category) 