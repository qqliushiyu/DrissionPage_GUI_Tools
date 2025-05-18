#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据导入对话框模块
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QComboBox, QFileDialog,
    QCheckBox, QGroupBox, QFormLayout, QSpinBox, QMessageBox,
    QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from typing import Dict, Any, List, Optional

from core.data_handler import DataHandler
from common.constants import DATA_FILE_FILTER

class DataImportDialog(QDialog):
    """数据导入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入数据")
        self.resize(800, 600)
        
        # 数据存储
        self._imported_data = None
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 创建导入选项卡
        import_tab = QWidget()
        import_layout = QVBoxLayout(import_tab)
        
        # 导入按钮
        import_buttons_layout = QHBoxLayout()
        
        self.import_csv_button = QPushButton("导入CSV文件")
        self.import_csv_button.clicked.connect(self._handle_import_csv)
        import_buttons_layout.addWidget(self.import_csv_button)
        
        self.import_excel_button = QPushButton("导入Excel文件")
        self.import_excel_button.clicked.connect(self._handle_import_excel)
        import_buttons_layout.addWidget(self.import_excel_button)
        
        import_buttons_layout.addStretch()
        import_layout.addLayout(import_buttons_layout)
        
        # 导入信息
        self.import_info_label = QLabel("尚未导入数据")
        import_layout.addWidget(self.import_info_label)
        
        # Excel工作表选择（默认隐藏）
        self.sheet_selection_group = QGroupBox("工作表选择")
        self.sheet_selection_group.setVisible(False)
        sheet_selection_layout = QHBoxLayout(self.sheet_selection_group)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentIndexChanged.connect(self._handle_sheet_changed)
        sheet_selection_layout.addWidget(QLabel("选择工作表:"))
        sheet_selection_layout.addWidget(self.sheet_combo)
        sheet_selection_layout.addStretch()
        
        import_layout.addWidget(self.sheet_selection_group)
        
        # 数据预览表格
        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        preview_layout.addWidget(self.preview_table)
        
        import_layout.addWidget(preview_group)
        
        # 添加导入选项卡
        self.tab_widget.addTab(import_tab, "导入数据")
        
        # 创建设置选项卡
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # 数据使用选项
        data_usage_group = QGroupBox("数据使用方式")
        data_usage_layout = QFormLayout(data_usage_group)
        
        self.data_usage_combo = QComboBox()
        self.data_usage_combo.addItems(["用于单个步骤", "创建循环遍历数据"])
        data_usage_layout.addRow("使用方式:", self.data_usage_combo)
        
        settings_layout.addWidget(data_usage_group)
        
        # 列映射设置
        mapping_group = QGroupBox("列映射")
        mapping_layout = QVBoxLayout(mapping_group)
        self.mapping_layout = mapping_layout  # 保存引用以便后续动态添加内容
        
        mapping_layout.addWidget(QLabel("导入数据后可在此设置字段映射"))
        
        settings_layout.addWidget(mapping_group)
        
        # 添加设置选项卡
        self.tab_widget.addTab(settings_tab, "设置")
        
        # 添加选项卡到主布局
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setEnabled(False)  # 初始禁用
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _handle_import_csv(self):
        """处理导入CSV文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入CSV文件", "", "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        success, result = DataHandler.import_csv(file_path)
        if success:
            self._imported_data = result
            self._update_preview_table()
            self._update_import_info()
            self._update_mapping_settings()
            self.ok_button.setEnabled(True)
            
            # 隐藏工作表选择
            self.sheet_selection_group.setVisible(False)
        else:
            QMessageBox.critical(self, "导入错误", str(result))
    
    def _handle_import_excel(self):
        """处理导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if not file_path:
            return
        
        success, result = DataHandler.import_excel(file_path)
        if success:
            self._imported_data = result
            self._update_preview_table()
            self._update_import_info()
            self._update_mapping_settings()
            self.ok_button.setEnabled(True)
            
            # 显示并更新工作表选择
            self.sheet_selection_group.setVisible(True)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(result.get("available_sheets", []))
            
            # 选中当前工作表
            current_sheet = result.get("sheet_name")
            if current_sheet in result.get("available_sheets", []):
                self.sheet_combo.setCurrentText(current_sheet)
        else:
            QMessageBox.critical(self, "导入错误", str(result))
    
    def _handle_sheet_changed(self, index):
        """处理Excel工作表变更"""
        if not self._imported_data or self._imported_data.get("source") != "excel":
            return
        
        if index < 0 or not self._imported_data.get("available_sheets"):
            return
        
        sheet_name = self.sheet_combo.currentText()
        file_path = self._imported_data.get("file_path")
        
        if not file_path or not sheet_name:
            return
        
        # 重新加载选中的工作表
        success, result = DataHandler.import_excel(file_path, sheet_name=sheet_name)
        if success:
            self._imported_data = result
            self._update_preview_table()
            self._update_import_info()
            self._update_mapping_settings()
        else:
            QMessageBox.critical(self, "工作表切换错误", str(result))
    
    def _update_preview_table(self):
        """更新预览表格"""
        if not self._imported_data:
            return
        
        headers = self._imported_data.get("headers", [])
        data = self._imported_data.get("data", [])
        
        # 最多显示10行预览
        preview_data = data[:10]
        
        # 设置表格列数和表头
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(headers)
        
        # 设置行数并填充数据
        self.preview_table.setRowCount(len(preview_data))
        for row_idx, row_data in enumerate(preview_data):
            for col_idx, header in enumerate(headers):
                value = row_data.get(header, "")
                item = QTableWidgetItem(str(value))
                self.preview_table.setItem(row_idx, col_idx, item)
        
        # 调整列宽以适应内容
        self.preview_table.resizeColumnsToContents()
    
    def _update_import_info(self):
        """更新导入信息标签"""
        if not self._imported_data:
            self.import_info_label.setText("尚未导入数据")
            return
        
        source = self._imported_data.get("source", "未知")
        source_text = "CSV文件" if source == "csv" else "Excel文件"
        file_path = self._imported_data.get("file_path", "")
        total_rows = len(self._imported_data.get("data", []))
        sheet_info = ""
        
        if source == "excel":
            sheet_name = self._imported_data.get("sheet_name", "")
            sheet_info = f"，工作表: {sheet_name}"
        
        self.import_info_label.setText(
            f"已导入 {source_text}: {file_path}{sheet_info}\n"
            f"共 {total_rows} 行数据，{len(self._imported_data.get('headers', []))} 列"
        )
    
    def _update_mapping_settings(self):
        """更新列映射设置"""
        # 清除现有映射控件
        while self.mapping_layout.count():
            item = self.mapping_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._imported_data or not self._imported_data.get("headers"):
            self.mapping_layout.addWidget(QLabel("导入数据后可在此设置字段映射"))
            return
        
        headers = self._imported_data.get("headers", [])
        
        # 添加使用说明
        self.mapping_layout.addWidget(QLabel("选择要使用的数据列并设置映射名称:"))
        
        # 为每个列添加映射控件
        for header in headers:
            row_layout = QHBoxLayout()
            
            # 列选择复选框
            checkbox = QCheckBox(header)
            checkbox.setChecked(True)  # 默认选中
            row_layout.addWidget(checkbox)
            
            # 映射名称输入框
            mapping_combo = QComboBox()
            mapping_combo.setEditable(True)
            mapping_combo.addItem(header)  # 默认映射名与原列名相同
            # 这里可以添加一些常用的映射名称
            mapping_combo.addItems(["username", "password", "email", "phone", "address", "name"])
            row_layout.addWidget(mapping_combo)
            
            self.mapping_layout.addLayout(row_layout)
        
        # 添加一些空间
        self.mapping_layout.addStretch()
    
    def get_imported_data(self) -> Optional[Dict[str, Any]]:
        """获取导入的数据"""
        return self._imported_data
    
    def get_data_usage_settings(self) -> Dict[str, Any]:
        """获取数据使用设置"""
        if not self._imported_data:
            return {}
        
        settings = {
            "usage_type": self.data_usage_combo.currentText(),
            "mappings": {}
        }
        
        # 获取列映射设置
        for i in range(self.mapping_layout.count()):
            item = self.mapping_layout.itemAt(i)
            if item and item.layout():
                row_layout = item.layout()
                if row_layout.count() >= 2:
                    checkbox_item = row_layout.itemAt(0)
                    combo_item = row_layout.itemAt(1)
                    
                    if (checkbox_item and checkbox_item.widget() and 
                        isinstance(checkbox_item.widget(), QCheckBox) and
                        combo_item and combo_item.widget() and
                        isinstance(combo_item.widget(), QComboBox)):
                        
                        checkbox = checkbox_item.widget()
                        combo = combo_item.widget()
                        
                        if checkbox.isChecked():
                            original_name = checkbox.text()
                            mapping_name = combo.currentText()
                            settings["mappings"][original_name] = mapping_name
        
        return settings 