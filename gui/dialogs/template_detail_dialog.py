#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模板详情对话框模块，用于显示模板详细信息和参数配置。
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFormLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QTextEdit, QWidget, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon

from typing import Dict, List, Tuple, Any, Optional, Union
import json
import datetime

from drission_gui_tool.core.template_manager import TemplateManager


class ParameterEditorWidget(QWidget):
    """参数编辑器控件"""
    
    # 参数值变化信号
    value_changed = pyqtSignal(str, object)  # param_name, value
    
    def __init__(self, param_data: Dict[str, Any], parent=None):
        """
        初始化参数编辑器控件
        
        Args:
            param_data: 参数数据
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.param_data = param_data
        self.param_name = param_data.get("name", "")
        self.param_type = param_data.get("type", "string")
        self.param_default = param_data.get("default_value", "")
        self.param_description = param_data.get("description", "")
        self.param_required = param_data.get("required", False)
        
        self._init_ui()
        self._populate_data()
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 根据参数类型创建不同的编辑控件
        if self.param_type == "string":
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self._on_value_changed)
        
        elif self.param_type == "integer":
            self.editor = QSpinBox()
            self.editor.setRange(-999999, 999999)
            self.editor.valueChanged.connect(self._on_value_changed)
        
        elif self.param_type == "number":
            from PyQt5.QtWidgets import QDoubleSpinBox
            self.editor = QDoubleSpinBox()
            self.editor.setRange(-999999.0, 999999.0)
            self.editor.setDecimals(4)
            self.editor.valueChanged.connect(self._on_value_changed)
        
        elif self.param_type == "boolean":
            self.editor = QCheckBox()
            self.editor.stateChanged.connect(self._on_value_changed)
        
        elif self.param_type == "select":
            self.editor = QComboBox()
            options = self.param_data.get("options", [])
            for option in options:
                self.editor.addItem(option.get("label", ""), option.get("value", ""))
            self.editor.currentIndexChanged.connect(self._on_value_changed)
        
        elif self.param_type == "textarea":
            self.editor = QTextEdit()
            self.editor.setMaximumHeight(100)
            self.editor.textChanged.connect(self._on_value_changed)
        
        else:
            # 默认使用文本输入框
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self._on_value_changed)
        
        # 添加到布局
        required_label = "* " if self.param_required else ""
        layout.addRow(f"{required_label}{self.param_name}:", self.editor)
        
        # 添加描述标签（如果有）
        if self.param_description:
            description_label = QLabel(self.param_description)
            description_label.setStyleSheet("color: gray; font-size: 10px;")
            description_label.setWordWrap(True)
            layout.addRow("", description_label)
    
    def _populate_data(self) -> None:
        """填充参数数据"""
        # 设置默认值
        if self.param_type == "string":
            self.editor.setText(str(self.param_default) if self.param_default is not None else "")
        
        elif self.param_type == "integer":
            try:
                self.editor.setValue(int(self.param_default) if self.param_default is not None else 0)
            except (ValueError, TypeError):
                self.editor.setValue(0)
        
        elif self.param_type == "number":
            try:
                self.editor.setValue(float(self.param_default) if self.param_default is not None else 0.0)
            except (ValueError, TypeError):
                self.editor.setValue(0.0)
        
        elif self.param_type == "boolean":
            self.editor.setChecked(bool(self.param_default))
        
        elif self.param_type == "select":
            # 根据默认值设置下拉框选中项
            default_value = self.param_default
            for i in range(self.editor.count()):
                if self.editor.itemData(i) == default_value:
                    self.editor.setCurrentIndex(i)
                    break
        
        elif self.param_type == "textarea":
            self.editor.setText(str(self.param_default) if self.param_default is not None else "")
    
    def _on_value_changed(self, *args) -> None:
        """当参数值变化时"""
        value = self.get_value()
        self.value_changed.emit(self.param_name, value)
    
    def get_value(self) -> Any:
        """
        获取参数值
        
        Returns:
            参数值
        """
        if self.param_type == "string":
            return self.editor.text()
        
        elif self.param_type == "integer":
            return self.editor.value()
        
        elif self.param_type == "number":
            return self.editor.value()
        
        elif self.param_type == "boolean":
            return self.editor.isChecked()
        
        elif self.param_type == "select":
            return self.editor.currentData()
        
        elif self.param_type == "textarea":
            return self.editor.toPlainText()
        
        return None


class TemplateDetailDialog(QDialog):
    """模板详情对话框"""
    
    def __init__(self, template_data: Dict[str, Any], parent=None, 
                template_manager: Optional[TemplateManager] = None):
        """
        初始化模板详情对话框
        
        Args:
            template_data: 模板数据
            parent: 父窗口
            template_manager: 模板管理器实例，用于加载完整模板内容
        """
        super().__init__(parent)
        
        self.template_data = template_data
        self._template_manager = template_manager or TemplateManager()
        
        # 加载完整的模板数据
        self.load_complete_template()
        
        # 参数值字典
        self.parameter_values = {}
        
        self.setWindowTitle(f"模板详情: {self.template_data.get('name', '未命名模板')}")
        self.resize(600, 600)
        
        self._init_ui()
        self._populate_template_info()
    
    def load_complete_template(self) -> None:
        """加载完整的模板数据"""
        template_id = self.template_data.get("id")
        category_id = self.template_data.get("category")
        
        if template_id and category_id:
            success, result = self._template_manager.load_template(template_id, category_id)
            if success and isinstance(result, dict):
                # 保留ID和分类信息
                result["id"] = template_id
                result["category"] = category_id
                self.template_data = result
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 模板信息区域
        info_group = QGroupBox("模板信息")
        info_layout = QFormLayout(info_group)
        
        self.name_label = QLabel()
        info_layout.addRow("名称:", self.name_label)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        info_layout.addRow("描述:", self.description_label)
        
        self.created_at_label = QLabel()
        info_layout.addRow("创建时间:", self.created_at_label)
        
        self.updated_at_label = QLabel()
        info_layout.addRow("更新时间:", self.updated_at_label)
        
        layout.addWidget(info_group)
        
        # 参数区域
        params_group = QGroupBox("模板参数")
        params_layout = QVBoxLayout(params_group)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 参数表单容器
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        
        scroll_area.setWidget(self.params_container)
        params_layout.addWidget(scroll_area)
        
        layout.addWidget(params_group)
        
        # 步骤预览区域
        steps_group = QGroupBox("步骤预览")
        steps_layout = QVBoxLayout(steps_group)
        
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(2)
        self.steps_table.setHorizontalHeaderLabels(["序号", "操作"])
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.steps_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        steps_layout.addWidget(self.steps_table)
        
        layout.addWidget(steps_group)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("应用模板")
        self.apply_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _populate_template_info(self) -> None:
        """填充模板信息"""
        # 基本信息
        self.name_label.setText(self.template_data.get("template_name", "未命名模板"))
        self.description_label.setText(self.template_data.get("description", ""))
        
        # 时间信息
        created_at = self.template_data.get("created_at", 0)
        if created_at:
            created_time_str = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
            self.created_at_label.setText(created_time_str)
        
        updated_at = self.template_data.get("updated_at", 0)
        if updated_at:
            updated_time_str = datetime.datetime.fromtimestamp(updated_at).strftime("%Y-%m-%d %H:%M:%S")
            self.updated_at_label.setText(updated_time_str)
        
        # 参数
        self._populate_parameters()
        
        # 步骤预览
        self._populate_steps()
    
    def _populate_parameters(self) -> None:
        """填充参数信息"""
        # 清空参数容器
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 获取参数列表
        parameters = self.template_data.get("parameters", [])
        
        if not parameters:
            # 显示无参数提示
            no_params_label = QLabel("此模板没有参数")
            no_params_label.setAlignment(Qt.AlignCenter)
            self.params_layout.addWidget(no_params_label)
            return
        
        # 添加参数编辑器
        for param in parameters:
            editor = ParameterEditorWidget(param)
            editor.value_changed.connect(self._on_parameter_value_changed)
            
            # 初始化参数值
            param_name = param.get("name", "")
            if param_name:
                self.parameter_values[param_name] = editor.get_value()
            
            self.params_layout.addWidget(editor)
        
        # 添加伸缩项
        self.params_layout.addStretch()
    
    def _populate_steps(self) -> None:
        """填充步骤信息"""
        # 清空表格
        self.steps_table.setRowCount(0)
        
        # 获取步骤列表
        steps = self.template_data.get("steps", [])
        
        # 添加步骤
        for i, step in enumerate(steps):
            self.steps_table.insertRow(i)
            
            # 步骤序号
            self.steps_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            # 步骤操作
            action_id = step.get("action_id", "")
            step_name = step.get("parameters", {}).get("__custom_step_name__", action_id)
            self.steps_table.setItem(i, 1, QTableWidgetItem(step_name))
    
    def _on_parameter_value_changed(self, param_name: str, value: Any) -> None:
        """
        当参数值变化时
        
        Args:
            param_name: 参数名
            value: 参数值
        """
        self.parameter_values[param_name] = value
    
    def get_template_data(self) -> Dict[str, Any]:
        """
        获取模板数据
        
        Returns:
            带有参数值的模板数据
        """
        return self.template_data
    
    def get_parameter_values(self) -> Dict[str, Any]:
        """
        获取参数值
        
        Returns:
            参数值字典
        """
        return self.parameter_values 