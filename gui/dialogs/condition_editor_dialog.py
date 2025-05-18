#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
条件编辑器对话框模块，用于可视化构建复杂的条件表达式。
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QLineEdit, QFormLayout, QGroupBox, QWidget,
    QTabWidget, QRadioButton, QCheckBox, QSpinBox, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QSplitter, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon

from typing import Dict, Any, List, Optional, Union, Tuple

from drission_gui_tool.core.condition_evaluator import ConditionType


class ConditionEditorDialog(QDialog):
    """条件表达式编辑对话框"""
    
    def __init__(self, parent=None, initial_condition: Optional[Dict[str, Any]] = None):
        """
        初始化条件编辑器对话框
        
        Args:
            parent: 父窗口
            initial_condition: 初始条件数据
        """
        super().__init__(parent)
        
        self.setWindowTitle("条件编辑器")
        self.resize(900, 600)
        
        self._condition_data = initial_condition or {"condition_type": "always_true"}
        
        # 条件类型分组
        self._condition_groups = {
            "元素条件": [
                (ConditionType.ELEMENT_EXISTS.value, "元素存在"),
                (ConditionType.ELEMENT_NOT_EXISTS.value, "元素不存在"),
                (ConditionType.ELEMENT_VISIBLE.value, "元素可见"),
                (ConditionType.ELEMENT_NOT_VISIBLE.value, "元素不可见"),
                (ConditionType.ELEMENT_ENABLED.value, "元素已启用"),
                (ConditionType.ELEMENT_DISABLED.value, "元素已禁用"),
                (ConditionType.ELEMENT_TEXT_EQUALS.value, "元素文本等于"),
                (ConditionType.ELEMENT_TEXT_CONTAINS.value, "元素文本包含"),
                (ConditionType.ELEMENT_TEXT_MATCHES.value, "元素文本匹配正则"),
                (ConditionType.ELEMENT_ATTR_EQUALS.value, "元素属性等于"),
                (ConditionType.ELEMENT_ATTR_CONTAINS.value, "元素属性包含"),
                (ConditionType.ELEMENT_ATTR_MATCHES.value, "元素属性匹配正则")
            ],
            "变量条件": [
                (ConditionType.VARIABLE_EQUALS.value, "变量等于"),
                (ConditionType.VARIABLE_NOT_EQUALS.value, "变量不等于"),
                (ConditionType.VARIABLE_GREATER_THAN.value, "变量大于"),
                (ConditionType.VARIABLE_LESS_THAN.value, "变量小于"),
                (ConditionType.VARIABLE_GREATER_EQUALS.value, "变量大于等于"),
                (ConditionType.VARIABLE_LESS_EQUALS.value, "变量小于等于"),
                (ConditionType.VARIABLE_CONTAINS.value, "变量包含"),
                (ConditionType.VARIABLE_MATCHES.value, "变量匹配正则"),
                (ConditionType.VARIABLE_IS_EMPTY.value, "变量为空"),
                (ConditionType.VARIABLE_IS_NOT_EMPTY.value, "变量不为空")
            ],
            "复合条件": [
                (ConditionType.AND.value, "AND (所有条件都为真)"),
                (ConditionType.OR.value, "OR (任一条件为真)"),
                (ConditionType.NOT.value, "NOT (条件取反)")
            ],
            "JavaScript": [
                (ConditionType.JAVASCRIPT.value, "JavaScript表达式")
            ],
            "其他": [
                (ConditionType.ALWAYS_TRUE.value, "始终为真"),
                (ConditionType.ALWAYS_FALSE.value, "始终为假")
            ]
        }
        
        self._init_ui()
        self._load_condition(self._condition_data)
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 条件类型选择
        type_group = QGroupBox("条件类型")
        type_layout = QVBoxLayout(type_group)
        
        type_tabs = QTabWidget()
        
        # 为每个分组创建标签页
        for group_name, conditions in self._condition_groups.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            for condition_value, condition_label in conditions:
                radio_button = QRadioButton(condition_label)
                radio_button.setProperty("condition_type", condition_value)
                radio_button.toggled.connect(self._on_condition_type_changed)
                tab_layout.addWidget(radio_button)
                
                # 如果是当前选中的条件类型，则选中对应单选按钮
                if condition_value == self._condition_data.get("condition_type"):
                    radio_button.setChecked(True)
            
            tab_layout.addStretch()
            type_tabs.addTab(tab, group_name)
        
        type_layout.addWidget(type_tabs)
        
        # 条件参数配置区域
        params_group = QGroupBox("条件参数")
        params_layout = QVBoxLayout(params_group)
        
        self._params_stack = QStackedWidget()
        
        # 元素条件参数配置
        element_params = QWidget()
        element_layout = QFormLayout(element_params)
        
        self._element_locator_strategy = QComboBox()
        self._element_locator_strategy.addItems(["css", "xpath", "id", "name", "tag", "class", "link_text"])
        element_layout.addRow("定位方式:", self._element_locator_strategy)
        
        self._element_locator_value = QLineEdit()
        element_layout.addRow("定位值:", self._element_locator_value)
        
        self._element_attribute_name = QLineEdit()
        element_layout.addRow("属性名称:", self._element_attribute_name)
        
        self._element_expected_text = QLineEdit()
        element_layout.addRow("期望文本:", self._element_expected_text)
        
        self._element_regex_pattern = QLineEdit()
        element_layout.addRow("正则表达式:", self._element_regex_pattern)
        
        self._element_timeout = QSpinBox()
        self._element_timeout.setRange(0, 60)
        self._element_timeout.setValue(3)
        element_layout.addRow("超时时间(秒):", self._element_timeout)
        
        # 变量条件参数配置
        variable_params = QWidget()
        variable_layout = QFormLayout(variable_params)
        
        self._variable_name = QLineEdit()
        variable_layout.addRow("变量名:", self._variable_name)
        
        self._variable_expected_value = QLineEdit()
        variable_layout.addRow("期望值:", self._variable_expected_value)
        
        self._variable_compare_value = QLineEdit()
        variable_layout.addRow("比较值:", self._variable_compare_value)
        
        self._variable_search_value = QLineEdit()
        variable_layout.addRow("搜索值:", self._variable_search_value)
        
        self._variable_regex_pattern = QLineEdit()
        variable_layout.addRow("正则表达式:", self._variable_regex_pattern)
        
        # 复合条件参数配置
        compound_params = QWidget()
        compound_layout = QVBoxLayout(compound_params)
        
        self._subconditions_tree = QTreeWidget()
        self._subconditions_tree.setHeaderLabels(["条件"])
        self._subconditions_tree.setSelectionMode(QTreeWidget.SingleSelection)
        compound_layout.addWidget(self._subconditions_tree)
        
        compound_buttons = QHBoxLayout()
        
        self._add_condition_button = QPushButton("添加条件")
        self._add_condition_button.clicked.connect(self._add_subcondition)
        
        self._edit_condition_button = QPushButton("编辑条件")
        self._edit_condition_button.clicked.connect(self._edit_subcondition)
        
        self._remove_condition_button = QPushButton("删除条件")
        self._remove_condition_button.clicked.connect(self._remove_subcondition)
        
        compound_buttons.addWidget(self._add_condition_button)
        compound_buttons.addWidget(self._edit_condition_button)
        compound_buttons.addWidget(self._remove_condition_button)
        
        compound_layout.addLayout(compound_buttons)
        
        # JavaScript条件参数配置
        js_params = QWidget()
        js_layout = QVBoxLayout(js_params)
        
        js_label = QLabel("输入JavaScript表达式，表达式应当返回布尔值:")
        self._js_code = QLineEdit()
        
        variables_label = QLabel("提示: 可使用 variables.name 引用变量，如 variables.count > 10")
        
        js_layout.addWidget(js_label)
        js_layout.addWidget(self._js_code)
        js_layout.addWidget(variables_label)
        js_layout.addStretch()
        
        # 其他条件参数配置
        other_params = QWidget()
        other_layout = QVBoxLayout(other_params)
        other_layout.addWidget(QLabel("此条件类型无需额外参数"))
        other_layout.addStretch()
        
        # 添加所有参数页面到堆叠部件
        self._params_stack.addWidget(element_params)  # 索引0: 元素条件
        self._params_stack.addWidget(variable_params)  # 索引1: 变量条件
        self._params_stack.addWidget(compound_params)  # 索引2: 复合条件
        self._params_stack.addWidget(js_params)  # 索引3: JavaScript条件
        self._params_stack.addWidget(other_params)  # 索引4: 其他条件
        
        params_layout.addWidget(self._params_stack)
        
        # 将条件类型和参数区域添加到布局
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.addWidget(type_group)
        content_splitter.addWidget(params_group)
        content_splitter.setSizes([300, 600])
        
        layout.addWidget(content_splitter)
        
        # 底部按钮区域
        buttons_layout = QHBoxLayout()
        
        self._cancel_button = QPushButton("取消")
        self._cancel_button.clicked.connect(self.reject)
        
        self._ok_button = QPushButton("确定")
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._cancel_button)
        buttons_layout.addWidget(self._ok_button)
        
        layout.addLayout(buttons_layout)
    
    def _on_condition_type_changed(self, checked: bool) -> None:
        """
        条件类型更改处理
        
        Args:
            checked: 单选按钮是否被选中
        """
        if not checked:
            return
        
        sender = self.sender()
        if not sender:
            return
        
        condition_type = sender.property("condition_type")
        if not condition_type:
            return
        
        # 根据条件类型切换参数面板
        if condition_type.startswith("element_"):
            self._params_stack.setCurrentIndex(0)
            # 根据具体元素条件类型显示/隐藏相关输入
            if "text_equals" in condition_type or "text_contains" in condition_type:
                self._element_expected_text.setEnabled(True)
                self._element_attribute_name.setEnabled(False)
                self._element_regex_pattern.setEnabled(False)
            elif "text_matches" in condition_type:
                self._element_expected_text.setEnabled(False)
                self._element_attribute_name.setEnabled(False)
                self._element_regex_pattern.setEnabled(True)
            elif "attr_equals" in condition_type or "attr_contains" in condition_type:
                self._element_expected_text.setEnabled(True)
                self._element_attribute_name.setEnabled(True)
                self._element_regex_pattern.setEnabled(False)
            elif "attr_matches" in condition_type:
                self._element_expected_text.setEnabled(False)
                self._element_attribute_name.setEnabled(True)
                self._element_regex_pattern.setEnabled(True)
            else:
                self._element_expected_text.setEnabled(False)
                self._element_attribute_name.setEnabled(False)
                self._element_regex_pattern.setEnabled(False)
        
        elif condition_type.startswith("variable_"):
            self._params_stack.setCurrentIndex(1)
            # 根据具体变量条件类型显示/隐藏相关输入
            if "equals" in condition_type or "not_equals" in condition_type:
                self._variable_expected_value.setEnabled(True)
                self._variable_compare_value.setEnabled(False)
                self._variable_search_value.setEnabled(False)
                self._variable_regex_pattern.setEnabled(False)
            elif "greater" in condition_type or "less" in condition_type:
                self._variable_expected_value.setEnabled(False)
                self._variable_compare_value.setEnabled(True)
                self._variable_search_value.setEnabled(False)
                self._variable_regex_pattern.setEnabled(False)
            elif "contains" in condition_type:
                self._variable_expected_value.setEnabled(False)
                self._variable_compare_value.setEnabled(False)
                self._variable_search_value.setEnabled(True)
                self._variable_regex_pattern.setEnabled(False)
            elif "matches" in condition_type:
                self._variable_expected_value.setEnabled(False)
                self._variable_compare_value.setEnabled(False)
                self._variable_search_value.setEnabled(False)
                self._variable_regex_pattern.setEnabled(True)
            else:  # is_empty, is_not_empty
                self._variable_expected_value.setEnabled(False)
                self._variable_compare_value.setEnabled(False)
                self._variable_search_value.setEnabled(False)
                self._variable_regex_pattern.setEnabled(False)
        
        elif condition_type in ("and", "or"):
            self._params_stack.setCurrentIndex(2)
            # 子条件适用于AND/OR
            self._subconditions_tree.setEnabled(True)
            self._add_condition_button.setEnabled(True)
            self._edit_condition_button.setEnabled(True)
            self._remove_condition_button.setEnabled(True)
        
        elif condition_type == "not":
            self._params_stack.setCurrentIndex(2)
            # NOT只需要一个子条件
            self._subconditions_tree.setEnabled(True)
            self._add_condition_button.setEnabled(self._subconditions_tree.topLevelItemCount() == 0)
            self._edit_condition_button.setEnabled(True)
            self._remove_condition_button.setEnabled(True)
        
        elif condition_type == "javascript":
            self._params_stack.setCurrentIndex(3)
        
        else:  # always_true, always_false
            self._params_stack.setCurrentIndex(4) 
    
    def _load_condition(self, condition_data: Dict[str, Any]) -> None:
        """
        加载现有条件数据
        
        Args:
            condition_data: 条件数据字典
        """
        condition_type = condition_data.get("condition_type")
        if not condition_type:
            return
        
        # 选中对应的条件类型
        for i in range(self.findChildren(QRadioButton).count()):
            tab = self.findChildren(QRadioButton)[i]
            for j in range(tab.layout().count()):
                widget = tab.layout().itemAt(j).widget()
                if isinstance(widget, QRadioButton) and widget.property("condition_type") == condition_type:
                    widget.setChecked(True)
                    break
        
        # 填充条件参数
        if condition_type.startswith("element_"):
            self._element_locator_strategy.setCurrentText(condition_data.get("locator_strategy", "css"))
            self._element_locator_value.setText(condition_data.get("locator_value", ""))
            self._element_attribute_name.setText(condition_data.get("attribute_name", ""))
            self._element_expected_text.setText(condition_data.get("expected_text", ""))
            self._element_regex_pattern.setText(condition_data.get("regex_pattern", ""))
            self._element_timeout.setValue(condition_data.get("timeout", 3))
        
        elif condition_type.startswith("variable_"):
            self._variable_name.setText(condition_data.get("variable_name", ""))
            self._variable_expected_value.setText(str(condition_data.get("expected_value", "")))
            self._variable_compare_value.setText(str(condition_data.get("compare_value", "")))
            self._variable_search_value.setText(str(condition_data.get("search_value", "")))
            self._variable_regex_pattern.setText(condition_data.get("regex_pattern", ""))
        
        elif condition_type in ("and", "or", "not"):
            subconditions = condition_data.get("conditions", [])
            if condition_type == "not" and subconditions:
                subconditions = [subconditions]
            
            self._subconditions_tree.clear()
            for subcondition in subconditions:
                self._add_condition_to_tree(subcondition)
            
            # 更新按钮状态
            if condition_type == "not":
                self._add_condition_button.setEnabled(self._subconditions_tree.topLevelItemCount() == 0)
        
        elif condition_type == "javascript":
            self._js_code.setText(condition_data.get("js_code", ""))
    
    def _add_condition_to_tree(self, condition_data: Dict[str, Any]) -> QTreeWidgetItem:
        """
        向条件树中添加条件项
        
        Args:
            condition_data: 条件数据
            
        Returns:
            创建的树项
        """
        condition_type = condition_data.get("condition_type", "")
        
        # 获取条件类型的显示名称
        display_name = condition_type
        for group in self._condition_groups.values():
            for value, label in group:
                if value == condition_type:
                    display_name = label
                    break
        
        item = QTreeWidgetItem([display_name])
        item.setData(0, Qt.UserRole, condition_data)
        
        self._subconditions_tree.addTopLevelItem(item)
        
        # 如果是复合条件，添加子条件
        if condition_type in ("and", "or"):
            subconditions = condition_data.get("conditions", [])
            for subcondition in subconditions:
                subitem = QTreeWidgetItem([self._get_condition_display_name(subcondition)])
                subitem.setData(0, Qt.UserRole, subcondition)
                item.addChild(subitem)
        
        elif condition_type == "not":
            not_condition = condition_data.get("condition", {})
            if not_condition:
                subitem = QTreeWidgetItem([self._get_condition_display_name(not_condition)])
                subitem.setData(0, Qt.UserRole, not_condition)
                item.addChild(subitem)
        
        return item
    
    def _get_condition_display_name(self, condition_data: Dict[str, Any]) -> str:
        """
        获取条件的显示名称
        
        Args:
            condition_data: 条件数据
            
        Returns:
            显示名称
        """
        condition_type = condition_data.get("condition_type", "")
        
        # 获取条件类型的显示名称
        display_name = condition_type
        for group in self._condition_groups.values():
            for value, label in group:
                if value == condition_type:
                    display_name = label
                    break
        
        # 添加一些详细信息
        if condition_type.startswith("element_"):
            locator = f"{condition_data.get('locator_strategy', '')}='{condition_data.get('locator_value', '')}'"
            display_name = f"{display_name}: {locator}"
        
        elif condition_type.startswith("variable_"):
            variable_name = condition_data.get("variable_name", "")
            display_name = f"{display_name}: {variable_name}"
        
        return display_name
    
    def _add_subcondition(self) -> None:
        """添加子条件"""
        selected_items = self._subconditions_tree.selectedItems()
        parent_item = None
        
        # 如果当前选择的是一个复合条件，将新条件添加为其子条件
        if selected_items:
            item = selected_items[0]
            item_data = item.data(0, Qt.UserRole)
            
            if isinstance(item_data, dict) and item_data.get("condition_type") in ("and", "or"):
                parent_item = item
        
        # 创建新条件
        dialog = ConditionEditorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_condition = dialog.get_condition()
            
            if parent_item:
                # 添加为子条件
                parent_data = parent_item.data(0, Qt.UserRole)
                parent_data.setdefault("conditions", []).append(new_condition)
                
                subitem = QTreeWidgetItem([self._get_condition_display_name(new_condition)])
                subitem.setData(0, Qt.UserRole, new_condition)
                parent_item.addChild(subitem)
                parent_item.setExpanded(True)
            else:
                # 添加为顶级条件
                self._add_condition_to_tree(new_condition)
            
            # 如果是NOT条件，只允许添加一个子条件
            condition_type = self._get_selected_condition_type()
            if condition_type == "not":
                self._add_condition_button.setEnabled(False)
    
    def _edit_subcondition(self) -> None:
        """编辑子条件"""
        selected_items = self._subconditions_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要编辑的条件")
            return
        
        item = selected_items[0]
        condition_data = item.data(0, Qt.UserRole)
        
        if not isinstance(condition_data, dict):
            return
        
        dialog = ConditionEditorDialog(self, condition_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_condition = dialog.get_condition()
            
            # 更新条件数据
            for key in list(condition_data.keys()):
                condition_data.pop(key)
            condition_data.update(updated_condition)
            
            # 更新显示
            item.setText(0, self._get_condition_display_name(condition_data))
            
            # 清除并重新添加子条件
            item.takeChildren()
            
            if condition_data.get("condition_type") in ("and", "or"):
                subconditions = condition_data.get("conditions", [])
                for subcondition in subconditions:
                    subitem = QTreeWidgetItem([self._get_condition_display_name(subcondition)])
                    subitem.setData(0, Qt.UserRole, subcondition)
                    item.addChild(subitem)
            
            elif condition_data.get("condition_type") == "not":
                not_condition = condition_data.get("condition", {})
                if not_condition:
                    subitem = QTreeWidgetItem([self._get_condition_display_name(not_condition)])
                    subitem.setData(0, Qt.UserRole, not_condition)
                    item.addChild(subitem)
    
    def _remove_subcondition(self) -> None:
        """删除子条件"""
        selected_items = self._subconditions_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要删除的条件")
            return
        
        item = selected_items[0]
        parent = item.parent()
        
        if parent:
            # 是子条件，从父条件的条件列表中移除
            parent_data = parent.data(0, Qt.UserRole)
            if not isinstance(parent_data, dict):
                return
            
            condition_type = parent_data.get("condition_type")
            if condition_type in ("and", "or"):
                # 从条件列表中移除
                conditions = parent_data.get("conditions", [])
                index = parent.indexOfChild(item)
                if 0 <= index < len(conditions):
                    conditions.pop(index)
            
            elif condition_type == "not":
                # NOT条件只有一个子条件，直接清空
                parent_data["condition"] = {}
            
            # 从树中移除
            parent.removeChild(item)
            
            # 如果是NOT条件并且没有子条件，启用添加按钮
            if condition_type == "not" and parent.childCount() == 0:
                self._add_condition_button.setEnabled(True)
        else:
            # 是顶级条件，直接从树中移除
            index = self._subconditions_tree.indexOfTopLevelItem(item)
            self._subconditions_tree.takeTopLevelItem(index)
    
    def _get_selected_condition_type(self) -> str:
        """
        获取当前选择的条件类型
        
        Returns:
            条件类型字符串
        """
        for radio_button in self.findChildren(QRadioButton):
            if radio_button.isChecked():
                return radio_button.property("condition_type")
        return ""
    
    def get_condition(self) -> Dict[str, Any]:
        """
        获取编辑后的条件数据
        
        Returns:
            条件数据字典
        """
        condition_type = self._get_selected_condition_type()
        if not condition_type:
            return {"condition_type": "always_true"}
        
        condition_data = {"condition_type": condition_type}
        
        # 根据条件类型收集参数
        if condition_type.startswith("element_"):
            condition_data["locator_strategy"] = self._element_locator_strategy.currentText()
            condition_data["locator_value"] = self._element_locator_value.text()
            condition_data["timeout"] = self._element_timeout.value()
            
            if "text_equals" in condition_type or "text_contains" in condition_type:
                condition_data["expected_text"] = self._element_expected_text.text()
            elif "text_matches" in condition_type:
                condition_data["regex_pattern"] = self._element_regex_pattern.text()
            elif "attr" in condition_type:
                condition_data["attribute_name"] = self._element_attribute_name.text()
                if "equals" in condition_type or "contains" in condition_type:
                    condition_data["expected_value"] = self._element_expected_text.text()
                elif "matches" in condition_type:
                    condition_data["regex_pattern"] = self._element_regex_pattern.text()
        
        elif condition_type.startswith("variable_"):
            condition_data["variable_name"] = self._variable_name.text()
            
            if "equals" in condition_type or "not_equals" in condition_type:
                value_str = self._variable_expected_value.text()
                # 尝试转换为合适的类型
                try:
                    if value_str.lower() in ("true", "false"):
                        condition_data["expected_value"] = value_str.lower() == "true"
                    elif value_str.isdigit():
                        condition_data["expected_value"] = int(value_str)
                    elif value_str.replace(".", "", 1).isdigit():
                        condition_data["expected_value"] = float(value_str)
                    else:
                        condition_data["expected_value"] = value_str
                except:
                    condition_data["expected_value"] = value_str
            
            elif "greater" in condition_type or "less" in condition_type:
                value_str = self._variable_compare_value.text()
                try:
                    if value_str.isdigit():
                        condition_data["compare_value"] = int(value_str)
                    elif value_str.replace(".", "", 1).isdigit():
                        condition_data["compare_value"] = float(value_str)
                    else:
                        condition_data["compare_value"] = value_str
                except:
                    condition_data["compare_value"] = value_str
            
            elif "contains" in condition_type:
                condition_data["search_value"] = self._variable_search_value.text()
            
            elif "matches" in condition_type:
                condition_data["regex_pattern"] = self._variable_regex_pattern.text()
        
        elif condition_type in ("and", "or"):
            # 收集子条件
            conditions = []
            root = self._subconditions_tree.invisibleRootItem()
            for i in range(root.childCount()):
                item = root.child(i)
                condition = item.data(0, Qt.UserRole)
                if condition:
                    conditions.append(condition)
            
            condition_data["conditions"] = conditions
        
        elif condition_type == "not":
            # NOT只有一个子条件
            root = self._subconditions_tree.invisibleRootItem()
            if root.childCount() > 0:
                item = root.child(0)
                subcondition = item.data(0, Qt.UserRole)
                if subcondition:
                    condition_data["condition"] = subcondition
        
        elif condition_type == "javascript":
            condition_data["js_code"] = self._js_code.text()
        
        return condition_data 