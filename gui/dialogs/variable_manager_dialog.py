#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
变量管理器对话框模块，提供变量的创建、编辑、删除等管理功能。
"""

from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QComboBox, QLineEdit, QLabel, QFormLayout,
    QGroupBox, QWidget, QHeaderView, QFileDialog, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon

from typing import Dict, Any, List, Optional, Union

from drission_gui_tool.core.variable_manager import VariableManager, VariableScope


class VariableTableWidget(QTableWidget):
    """变量表格控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置列
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["变量名", "值", "类型", "描述"])
        
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
        header.setSectionResizeMode(3, QHeaderView.Stretch)
    
    def populate_variables(self, variables: Dict[str, Dict[str, Any]]) -> None:
        """
        填充变量数据到表格
        
        Args:
            variables: 变量数据字典
        """
        self.setRowCount(0)  # 清空表格
        
        row = 0
        for name, var_data in variables.items():
            self.insertRow(row)
            
            # 设置变量名
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, var_data)  # 存储完整变量数据
            self.setItem(row, 0, name_item)
            
            # 设置值
            value = var_data.get("value")
            
            # 正确处理值的显示，特别是对列表和字典使用ensure_ascii=False
            if isinstance(value, (list, dict)):
                import json
                value_str = json.dumps(value, ensure_ascii=False)
                if len(value_str) > 50:
                    value_str = value_str[:50] + "..."
            else:
                value_str = str(value)
                
            self.setItem(row, 1, QTableWidgetItem(value_str))
            
            # 设置类型
            self.setItem(row, 2, QTableWidgetItem(var_data.get("type", "")))
            
            # 设置描述
            self.setItem(row, 3, QTableWidgetItem(var_data.get("description", "")))
            
            row += 1
    
    def get_selected_variable(self) -> Optional[Dict[str, Any]]:
        """
        获取当前选中的变量数据
        
        Returns:
            变量数据字典或None
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        # 获取选中行的第一个单元格（变量名）
        row = selected_items[0].row()
        name_item = self.item(row, 0)
        
        return name_item.data(Qt.UserRole)


class VariableEditorDialog(QDialog):
    """变量编辑对话框"""
    
    def __init__(self, parent=None, variable_data: Optional[Dict[str, Any]] = None):
        """
        初始化变量编辑对话框
        
        Args:
            parent: 父窗口
            variable_data: 要编辑的变量数据，如果为None则为创建新变量
        """
        super().__init__(parent)
        
        self.is_new_variable = variable_data is None
        self.variable_data = variable_data or {}
        
        self.setWindowTitle("创建变量" if self.is_new_variable else "编辑变量")
        self.resize(400, 300)
        
        self._init_ui()
        self._populate_data()
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 变量名
        self.name_edit = QLineEdit()
        form_layout.addRow("变量名:", self.name_edit)
        
        # 变量类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["string", "integer", "number", "boolean", "list", "dict"])
        form_layout.addRow("类型:", self.type_combo)
        
        # 作用域
        self.scope_combo = QComboBox()
        self.scope_combo.addItems([
            VariableScope.GLOBAL,
            VariableScope.LOCAL,
            VariableScope.TEMPORARY
        ])
        form_layout.addRow("作用域:", self.scope_combo)
        
        # 变量值
        self.value_edit = QLineEdit()
        form_layout.addRow("值:", self.value_edit)
        
        # 描述
        self.description_edit = QLineEdit()
        form_layout.addRow("描述:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def _populate_data(self) -> None:
        """填充现有数据（编辑模式）"""
        if not self.is_new_variable:
            self.name_edit.setText(self.variable_data.get("name", ""))
            self.name_edit.setReadOnly(True)  # 不允许修改变量名
            
            # 设置类型
            var_type = self.variable_data.get("type", "string")
            index = self.type_combo.findText(var_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            # 设置作用域
            scope = self.variable_data.get("scope", VariableScope.GLOBAL)
            index = self.scope_combo.findText(scope)
            if index >= 0:
                self.scope_combo.setCurrentIndex(index)
            
            # 设置值
            value = self.variable_data.get("value")
            if value is not None:
                if isinstance(value, (list, dict)):
                    import json
                    self.value_edit.setText(json.dumps(value, ensure_ascii=False))
                else:
                    self.value_edit.setText(str(value))
            
            # 设置描述
            self.description_edit.setText(self.variable_data.get("description", ""))
    
    def get_variable_data(self) -> Dict[str, Any]:
        """
        获取表单中的变量数据
        
        Returns:
            变量数据字典
        """
        data = {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "scope": self.scope_combo.currentText(),
            "description": self.description_edit.text().strip()
        }
        
        # 根据选择的类型转换值
        value_str = self.value_edit.text().strip()
        var_type = data["type"]
        
        if var_type == "string":
            data["value"] = value_str
        elif var_type == "integer":
            try:
                data["value"] = int(value_str)
            except ValueError:
                data["value"] = 0
        elif var_type == "number":
            try:
                data["value"] = float(value_str)
            except ValueError:
                data["value"] = 0.0
        elif var_type == "boolean":
            lower_value = value_str.lower()
            data["value"] = lower_value in ("true", "yes", "1", "on")
        elif var_type in ("list", "dict"):
            try:
                import json
                # 确保能正确解析中文字符
                data["value"] = json.loads(value_str)
            except json.JSONDecodeError:
                data["value"] = [] if var_type == "list" else {}
        
        return data


class VariableManagerDialog(QDialog):
    """变量管理器对话框"""
    
    def __init__(self, parent=None, variable_manager: VariableManager = None):
        """
        初始化变量管理器对话框
        
        Args:
            parent: 父窗口
            variable_manager: 变量管理器实例
        """
        super().__init__(parent)
        
        self._variable_manager = variable_manager or VariableManager()
        
        self.setWindowTitle("变量管理器")
        self.resize(800, 600)
        
        self._init_ui()
        self._refresh_variables()
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 全局变量标签页
        global_tab = QWidget()
        global_layout = QVBoxLayout(global_tab)
        
        # 全局变量表格
        self.global_table = VariableTableWidget()
        global_layout.addWidget(self.global_table)
        
        # 全局变量操作按钮
        global_buttons = QHBoxLayout()
        
        self.add_global_button = QPushButton("添加变量")
        self.add_global_button.clicked.connect(lambda: self._add_variable(VariableScope.GLOBAL))
        
        self.edit_global_button = QPushButton("编辑变量")
        self.edit_global_button.clicked.connect(lambda: self._edit_variable(self.global_table))
        
        self.delete_global_button = QPushButton("删除变量")
        self.delete_global_button.clicked.connect(lambda: self._delete_variable(self.global_table, VariableScope.GLOBAL))
        
        global_buttons.addWidget(self.add_global_button)
        global_buttons.addWidget(self.edit_global_button)
        global_buttons.addWidget(self.delete_global_button)
        global_buttons.addStretch()
        
        global_layout.addLayout(global_buttons)
        
        # 局部变量标签页
        local_tab = QWidget()
        local_layout = QVBoxLayout(local_tab)
        
        # 局部变量表格
        self.local_table = VariableTableWidget()
        local_layout.addWidget(self.local_table)
        
        # 局部变量操作按钮
        local_buttons = QHBoxLayout()
        
        self.add_local_button = QPushButton("添加变量")
        self.add_local_button.clicked.connect(lambda: self._add_variable(VariableScope.LOCAL))
        
        self.edit_local_button = QPushButton("编辑变量")
        self.edit_local_button.clicked.connect(lambda: self._edit_variable(self.local_table))
        
        self.delete_local_button = QPushButton("删除变量")
        self.delete_local_button.clicked.connect(lambda: self._delete_variable(self.local_table, VariableScope.LOCAL))
        
        self.clear_local_button = QPushButton("清空所有")
        self.clear_local_button.clicked.connect(lambda: self._clear_variables(VariableScope.LOCAL))
        
        local_buttons.addWidget(self.add_local_button)
        local_buttons.addWidget(self.edit_local_button)
        local_buttons.addWidget(self.delete_local_button)
        local_buttons.addWidget(self.clear_local_button)
        local_buttons.addStretch()
        
        local_layout.addLayout(local_buttons)
        
        # 临时变量标签页
        temp_tab = QWidget()
        temp_layout = QVBoxLayout(temp_tab)
        
        # 临时变量表格
        self.temp_table = VariableTableWidget()
        temp_layout.addWidget(self.temp_table)
        
        # 临时变量操作按钮
        temp_buttons = QHBoxLayout()
        
        self.add_temp_button = QPushButton("添加变量")
        self.add_temp_button.clicked.connect(lambda: self._add_variable(VariableScope.TEMPORARY))
        
        self.edit_temp_button = QPushButton("编辑变量")
        self.edit_temp_button.clicked.connect(lambda: self._edit_variable(self.temp_table))
        
        self.delete_temp_button = QPushButton("删除变量")
        self.delete_temp_button.clicked.connect(lambda: self._delete_variable(self.temp_table, VariableScope.TEMPORARY))
        
        self.clear_temp_button = QPushButton("清空所有")
        self.clear_temp_button.clicked.connect(lambda: self._clear_variables(VariableScope.TEMPORARY))
        
        temp_buttons.addWidget(self.add_temp_button)
        temp_buttons.addWidget(self.edit_temp_button)
        temp_buttons.addWidget(self.delete_temp_button)
        temp_buttons.addWidget(self.clear_temp_button)
        temp_buttons.addStretch()
        
        temp_layout.addLayout(temp_buttons)
        
        # 添加标签页
        tab_widget.addTab(global_tab, "全局变量")
        tab_widget.addTab(local_tab, "局部变量")
        tab_widget.addTab(temp_tab, "临时变量")
        
        layout.addWidget(tab_widget)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        
        # 导入/导出按钮
        self.import_button = QPushButton("导入变量")
        self.import_button.clicked.connect(self._import_variables)
        
        self.export_button = QPushButton("导出变量")
        self.export_button.clicked.connect(self._export_variables)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _refresh_variables(self) -> None:
        """刷新所有变量数据"""
        # 获取各作用域的变量
        global_vars = self._variable_manager.get_all_variables(VariableScope.GLOBAL)
        local_vars = self._variable_manager.get_all_variables(VariableScope.LOCAL)
        temp_vars = self._variable_manager.get_all_variables(VariableScope.TEMPORARY)
        
        # 填充表格
        self.global_table.populate_variables(global_vars)
        self.local_table.populate_variables(local_vars)
        self.temp_table.populate_variables(temp_vars)
    
    def _add_variable(self, scope: str) -> None:
        """
        添加新变量
        
        Args:
            scope: 变量作用域
        """
        dialog = VariableEditorDialog(self)
        dialog.scope_combo.setCurrentText(scope)
        
        if dialog.exec_() == QDialog.Accepted:
            variable_data = dialog.get_variable_data()
            
            name = variable_data["name"]
            value = variable_data["value"]
            var_type = variable_data["type"]
            var_scope = variable_data["scope"]
            description = variable_data["description"]
            
            success, message = self._variable_manager.create_variable(
                name, value, var_type, var_scope, description
            )
            
            if success:
                QMessageBox.information(self, "成功", f"变量 '{name}' 创建成功")
            else:
                QMessageBox.warning(self, "错误", f"创建变量失败: {message}")
            
            # 刷新变量列表
            self._refresh_variables()
    
    def _edit_variable(self, table: VariableTableWidget) -> None:
        """
        编辑选中的变量
        
        Args:
            table: 变量表格控件
        """
        variable_data = table.get_selected_variable()
        if not variable_data:
            QMessageBox.warning(self, "警告", "请先选择要编辑的变量")
            return
        
        dialog = VariableEditorDialog(self, variable_data)
        
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_variable_data()
            
            name = updated_data["name"]
            value = updated_data["value"]
            var_scope = updated_data["scope"]
            
            success, message = self._variable_manager.set_variable(name, value, var_scope)
            
            if success:
                QMessageBox.information(self, "成功", f"变量 '{name}' 更新成功")
            else:
                QMessageBox.warning(self, "错误", f"更新变量失败: {message}")
            
            # 刷新变量列表
            self._refresh_variables()
    
    def _delete_variable(self, table: VariableTableWidget, scope: str) -> None:
        """
        删除选中的变量
        
        Args:
            table: 变量表格控件
            scope: 变量作用域
        """
        variable_data = table.get_selected_variable()
        if not variable_data:
            QMessageBox.warning(self, "警告", "请先选择要删除的变量")
            return
        
        name = variable_data.get("name", "")
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除变量 '{name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self._variable_manager.delete_variable(name, scope)
            
            if success:
                QMessageBox.information(self, "成功", f"变量 '{name}' 已删除")
            else:
                QMessageBox.warning(self, "错误", f"删除变量失败: {message}")
            
            # 刷新变量列表
            self._refresh_variables()
    
    def _clear_variables(self, scope: str) -> None:
        """
        清空指定作用域的所有变量
        
        Args:
            scope: 变量作用域
        """
        scope_names = {
            VariableScope.GLOBAL: "全局",
            VariableScope.LOCAL: "局部",
            VariableScope.TEMPORARY: "临时"
        }
        
        scope_name = scope_names.get(scope, scope)
        
        reply = QMessageBox.question(
            self, "确认清空", 
            f"确定要清空所有{scope_name}变量吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._variable_manager.clear_scope(scope)
            QMessageBox.information(self, "成功", f"所有{scope_name}变量已清空")
            
            # 刷新变量列表
            self._refresh_variables()
    
    def _import_variables(self) -> None:
        """导入变量"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择变量文件", "", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            
            # 选择导入的作用域
            scope, ok = QMessageBox.question(
                self, "选择作用域",
                "请选择要导入到的作用域",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            selected_scope = VariableScope.GLOBAL
            if scope == QMessageBox.No:
                selected_scope = VariableScope.LOCAL
            
            success, message = self._variable_manager.import_variables(json_str, selected_scope)
            
            if success:
                QMessageBox.information(self, "成功", f"变量导入成功: {message}")
            else:
                QMessageBox.warning(self, "错误", f"变量导入失败: {message}")
            
            # 刷新变量列表
            self._refresh_variables()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入变量失败: {str(e)}")
    
    def _export_variables(self) -> None:
        """导出变量"""
        options = ["全局变量", "局部变量", "临时变量", "所有变量"]
        selected, ok = QMessageBox.information(
            self, "选择导出范围",
            "请选择要导出的变量范围",
            *options
        )
        
        if not ok:
            return
        
        scope = None
        if selected == 0:
            scope = VariableScope.GLOBAL
        elif selected == 1:
            scope = VariableScope.LOCAL
        elif selected == 2:
            scope = VariableScope.TEMPORARY
        
        json_str = self._variable_manager.export_variables(scope)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存变量文件", "", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            QMessageBox.information(self, "成功", f"变量已导出到: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出变量失败: {str(e)}")
    
    def get_variable_manager(self) -> VariableManager:
        """
        获取变量管理器实例
        
        Returns:
            变量管理器实例
        """
        return self._variable_manager 