#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试面板组件，提供断点管理、变量监视、执行控制等功能。
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, 
    QLabel, QTreeWidget, QTreeWidgetItem, QComboBox, QCheckBox,
    QLineEdit, QGroupBox, QFormLayout, QSpinBox, QToolBar, 
    QAction, QFrame, QMenu, QToolButton, QTextEdit, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QColor, QFont, QTextCursor

from typing import Dict, List, Any, Optional

from ...core.debug_manager import BreakpointType, Breakpoint, ExecutionMode

class BreakpointTableWidget(QTableWidget):
    """断点列表表格组件"""
    
    breakpoint_toggled = pyqtSignal(str, bool)  # breakpoint_id, enabled
    breakpoint_removed = pyqtSignal(str)  # breakpoint_id
    breakpoint_edited = pyqtSignal(str)  # breakpoint_id
    breakpoint_condition_changed = pyqtSignal(str, str)  # breakpoint_id, condition
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["启用", "步骤", "类型", "条件", "命中", "操作"])
        
        # 设置列宽
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # 其他设置
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 添加右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        breakpoint_id = self.item(row, 1).data(Qt.UserRole)
        if not breakpoint_id:
            return
            
        menu = QMenu(self)
        
        # 添加菜单项
        edit_condition_action = menu.addAction("编辑条件")
        menu.addSeparator()
        remove_action = menu.addAction("删除断点")
        
        # 执行菜单
        action = menu.exec_(self.viewport().mapToGlobal(pos))
        
        if action == edit_condition_action:
            self._edit_breakpoint_condition(breakpoint_id)
        elif action == remove_action:
            self.breakpoint_removed.emit(breakpoint_id)
    
    def _edit_breakpoint_condition(self, breakpoint_id):
        """编辑断点条件"""
        # 找到对应的行
        for row in range(self.rowCount()):
            if self.item(row, 1).data(Qt.UserRole) == breakpoint_id:
                # 获取当前条件
                current_condition = self.item(row, 3).text()
                
                # 弹出输入对话框
                condition, ok = QInputDialog.getText(
                    self,
                    "编辑断点条件",
                    "请输入条件表达式:",
                    text=current_condition
                )
                
                if ok:
                    # 更新条件
                    self.item(row, 3).setText(condition)
                    self.breakpoint_condition_changed.emit(breakpoint_id, condition)
                break
    
    def update_breakpoints(self, breakpoints: List[Dict[str, Any]]):
        """更新断点列表"""
        # 保存当前选择的行
        selected_row = -1
        if self.selectedItems():
            selected_row = self.selectedItems()[0].row()
        
        # 清空表格
        self.setRowCount(0)
        
        # 添加断点
        for i, bp in enumerate(breakpoints):
            self.insertRow(i)
            
            # 启用复选框
            enabled_check = QCheckBox()
            enabled_check.setChecked(bp.get("enabled", True))
            enabled_check.stateChanged.connect(lambda state, bp_id=bp.get("id"): 
                                             self.breakpoint_toggled.emit(bp_id, state == Qt.Checked))
            self.setCellWidget(i, 0, enabled_check)
            
            # 步骤索引
            step_item = QTableWidgetItem(str(bp.get("step_index", 0)))
            step_item.setData(Qt.UserRole, bp.get("id"))
            self.setItem(i, 1, step_item)
            
            # 断点类型
            bp_type = bp.get("type", BreakpointType.LINE)
            type_names = {
                BreakpointType.LINE: "行",
                BreakpointType.CONDITION: "条件",
                BreakpointType.ERROR: "错误",
                BreakpointType.VARIABLE: "变量"
            }
            type_item = QTableWidgetItem(type_names.get(bp_type, bp_type))
            self.setItem(i, 2, type_item)
            
            # 条件或变量
            condition_text = ""
            if bp_type == BreakpointType.CONDITION:
                condition_text = bp.get("condition", "")
            elif bp_type == BreakpointType.VARIABLE:
                var_name = bp.get("variable_name", "")
                var_value = bp.get("variable_value", "")
                operator = bp.get("comparison_operator", "==")
                condition_text = f"{var_name} {operator} {var_value}"
            
            condition_item = QTableWidgetItem(condition_text)
            self.setItem(i, 3, condition_item)
            
            # 命中次数
            hit_item = QTableWidgetItem(str(bp.get("hit_count", 0)))
            self.setItem(i, 4, hit_item)
            
            # 操作按钮
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)
            
            edit_btn = QPushButton("编辑")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda _, bp_id=bp.get("id"): 
                                    self.breakpoint_edited.emit(bp_id))
            
            remove_btn = QPushButton("删除")
            remove_btn.setMaximumWidth(40)
            remove_btn.clicked.connect(lambda _, bp_id=bp.get("id"): 
                                      self.breakpoint_removed.emit(bp_id))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(remove_btn)
            
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.setCellWidget(i, 5, btn_widget)
        
        # 恢复选择
        if 0 <= selected_row < self.rowCount():
            self.selectRow(selected_row)


class VariableWatchWidget(QTreeWidget):
    """变量监视树组件"""
    
    variable_added = pyqtSignal(str)  # variable_name
    variable_removed = pyqtSignal(str)  # variable_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setColumnCount(3)
        self.setHeaderLabels(["变量名", "值", "类型"])
        
        # 设置列宽
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # 添加右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        add_action = menu.addAction("添加监视变量")
        remove_action = menu.addAction("移除监视变量")
        
        selected_item = self.itemAt(pos)
        
        if not selected_item:
            remove_action.setEnabled(False)
        
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == add_action:
            # 实现添加变量的逻辑
            variable_name, ok = QInputDialog.getText(self, "添加监视变量", "变量名:")
            if ok and variable_name:
                self.variable_added.emit(variable_name)
        
        elif action == remove_action and selected_item:
            # 实现移除变量的逻辑
            variable_name = selected_item.text(0)
            self.variable_removed.emit(variable_name)
    
    def update_variables(self, variables: Dict[str, Any]):
        """更新变量列表"""
        # 清空表格但保持当前展开状态
        expanded_items = []
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.isExpanded():
                expanded_items.append(item.text(0))
        
        self.clear()
        
        # 添加变量
        for name, value in variables.items():
            self._add_variable_item(name, value)
        
        # 恢复展开状态
        for i in range(root.childCount()):
            item = root.child(i)
            if item.text(0) in expanded_items:
                item.setExpanded(True)
    
    def _add_variable_item(self, name, value, parent_item=None):
        """添加变量项"""
        if parent_item is None:
            parent_item = self.invisibleRootItem()
        
        item = QTreeWidgetItem(parent_item)
        item.setText(0, str(name))
        
        # 设置值和类型
        value_str = str(value)
        if len(value_str) > 100:
            value_str = value_str[:100] + "..."
        
        item.setText(1, value_str)
        item.setText(2, type(value).__name__)
        
        # 递归处理字典和列表
        if isinstance(value, dict) and value:
            for k, v in value.items():
                self._add_variable_item(k, v, item)
        
        elif isinstance(value, (list, tuple)) and value:
            for i, v in enumerate(value):
                self._add_variable_item(f"[{i}]", v, item)
        
        return item


class PerformanceWidget(QWidget):
    """性能监控组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 执行时间
        time_group = QGroupBox("执行时间")
        time_layout = QFormLayout(time_group)
        
        self.total_time_label = QLabel("0.00 秒")
        self.avg_step_time_label = QLabel("0.00 秒")
        self.max_step_time_label = QLabel("0.00 秒")
        
        time_layout.addRow("总执行时间:", self.total_time_label)
        time_layout.addRow("平均步骤时间:", self.avg_step_time_label)
        time_layout.addRow("最长步骤时间:", self.max_step_time_label)
        
        # 内存使用
        memory_group = QGroupBox("内存使用")
        memory_layout = QFormLayout(memory_group)
        
        self.current_memory_label = QLabel("0.00 MB")
        self.peak_memory_label = QLabel("0.00 MB")
        
        memory_layout.addRow("当前内存:", self.current_memory_label)
        memory_layout.addRow("峰值内存:", self.peak_memory_label)
        
        # CPU使用
        cpu_group = QGroupBox("CPU使用")
        cpu_layout = QFormLayout(cpu_group)
        
        self.current_cpu_label = QLabel("0.0%")
        self.avg_cpu_label = QLabel("0.0%")
        
        cpu_layout.addRow("当前CPU:", self.current_cpu_label)
        cpu_layout.addRow("平均CPU:", self.avg_cpu_label)
        
        # 添加到主布局
        layout.addWidget(time_group)
        layout.addWidget(memory_group)
        layout.addWidget(cpu_group)
        layout.addStretch()
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """更新性能指标"""
        # 更新时间信息
        total_time = metrics.get("total_time", 0)
        self.total_time_label.setText(f"{total_time:.2f} 秒")
        
        # 计算步骤时间统计
        step_times = metrics.get("step_times", {})
        if step_times:
            durations = [step_info.get("duration", 0) for step_info in step_times.values()]
            if durations:
                avg_time = sum(durations) / len(durations)
                max_time = max(durations)
                self.avg_step_time_label.setText(f"{avg_time:.2f} 秒")
                self.max_step_time_label.setText(f"{max_time:.2f} 秒")
        
        # 更新内存信息
        memory_usage = metrics.get("avg_memory_usage", {})
        current_memory = memory_usage.get("rss", 0)
        self.current_memory_label.setText(f"{current_memory:.2f} MB")
        
        # 查找峰值内存
        memory_samples = metrics.get("memory_usage", [])
        if memory_samples:
            peak_memory = max(sample.get("rss", 0) for sample in memory_samples) / (1024 * 1024)
            self.peak_memory_label.setText(f"{peak_memory:.2f} MB")
        
        # 更新CPU信息
        cpu_usage = metrics.get("avg_cpu_usage", 0)
        self.avg_cpu_label.setText(f"{cpu_usage:.1f}%")
        
        cpu_samples = metrics.get("cpu_usage", [])
        if cpu_samples:
            current_cpu = cpu_samples[-1].get("percent", 0) if cpu_samples else 0
            self.current_cpu_label.setText(f"{current_cpu:.1f}%")


class DebugLogWidget(QWidget):
    """调试日志组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QToolBar()
        
        # 日志级别筛选
        self.level_combo = QComboBox()
        self.level_combo.addItems(["全部", "INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG"])
        self.level_combo.currentTextChanged.connect(self._filter_logs)
        
        toolbar.addWidget(QLabel("级别筛选:"))
        toolbar.addWidget(self.level_combo)
        toolbar.addSeparator()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        self.search_input.textChanged.connect(self._filter_logs)
        
        toolbar.addWidget(QLabel("搜索:"))
        toolbar.addWidget(self.search_input)
        toolbar.addSeparator()
        
        # 清空按钮
        clear_action = QAction("清空", self)
        clear_action.triggered.connect(self._clear_logs)
        toolbar.addAction(clear_action)
        
        # 导出按钮
        export_action = QAction("导出", self)
        export_action.triggered.connect(self._export_logs)
        toolbar.addAction(export_action)
        
        # 日志文本编辑器
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # 设置字体
        font = QFont("Monospace")
        font.setFixedPitch(True)
        self.log_text.setFont(font)
        
        # 添加到布局
        layout.addWidget(toolbar)
        layout.addWidget(self.log_text)
        
        # 存储完整日志
        self._logs = []
    
    def _filter_logs(self):
        """筛选日志"""
        level_filter = self.level_combo.currentText()
        search_text = self.search_input.text().lower()
        
        # 重置文本
        self.log_text.clear()
        
        for log in self._logs:
            level = log.get("level", "")
            message = log.get("message", "")
            timestamp = log.get("formatted_time", "")
            
            # 应用级别筛选
            if level_filter != "全部" and level != level_filter:
                continue
            
            # 应用搜索筛选
            if search_text and search_text not in message.lower():
                continue
            
            # 设置颜色
            color = self._get_level_color(level)
            
            # 添加带颜色的文本
            self.log_text.setTextColor(color)
            self.log_text.append(f"[{timestamp}] [{level}] {message}")
    
    def _get_level_color(self, level: str) -> QColor:
        """获取日志级别对应的颜色"""
        colors = {
            "INFO": QColor(0, 0, 0),  # 黑色
            "SUCCESS": QColor(0, 128, 0),  # 绿色
            "WARNING": QColor(255, 165, 0),  # 橙色
            "ERROR": QColor(255, 0, 0),  # 红色
            "DEBUG": QColor(128, 128, 128)  # 灰色
        }
        return colors.get(level, QColor(0, 0, 0))
    
    def _clear_logs(self):
        """清空日志"""
        self._logs = []
        self.log_text.clear()
    
    def _export_logs(self):
        """导出日志"""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出日志", "", "文本文件 (*.txt);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        # 根据扩展名选择导出格式
        if file_path.endswith(".json"):
            self._export_logs_json(file_path)
        else:
            self._export_logs_text(file_path)
    
    def _export_logs_text(self, file_path: str):
        """导出为文本格式"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for log in self._logs:
                    timestamp = log.get("formatted_time", "")
                    level = log.get("level", "")
                    message = log.get("message", "")
                    f.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception as e:
            print(f"导出日志失败: {str(e)}")
    
    def _export_logs_json(self, file_path: str):
        """导出为JSON格式"""
        try:
            import json
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"导出日志失败: {str(e)}")
    
    def add_log(self, log_entry: Dict[str, Any]):
        """添加日志条目"""
        # 转换时间戳为可读格式
        import time
        timestamp = log_entry.get("timestamp", time.time())
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        
        log_entry["formatted_time"] = formatted_time
        
        # 添加到日志列表
        self._logs.append(log_entry)
        
        # 应用筛选
        self._filter_logs()
        
        # 滚动到底部
        self.log_text.moveCursor(QTextCursor.End)


class DebugPanelWidget(QWidget):
    """调试面板组件"""
    
    # 断点相关信号
    breakpoint_toggled = pyqtSignal(int)  # step_index
    breakpoint_added = pyqtSignal(int, str, str)  # step_index, type, condition
    breakpoint_removed = pyqtSignal(str)  # breakpoint_id
    breakpoint_enabled = pyqtSignal(str, bool)  # breakpoint_id, enabled
    breakpoint_condition_changed = pyqtSignal(str, str)  # breakpoint_id, condition
    
    # 执行控制信号
    debug_started = pyqtSignal(str)  # mode
    debug_stopped = pyqtSignal()
    debug_paused = pyqtSignal()
    debug_resumed = pyqtSignal()
    debug_step_over = pyqtSignal()
    debug_step_into = pyqtSignal()
    debug_step_out = pyqtSignal()
    debug_run_to_cursor = pyqtSignal(int)  # step_index
    
    # 变量监视信号
    variable_watch_added = pyqtSignal(str)  # variable_name
    variable_watch_removed = pyqtSignal(str)  # variable_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        
        # 调试工具栏
        self.debug_toolbar = self._create_debug_toolbar()
        main_layout.addWidget(self.debug_toolbar)
        
        # 主分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 上部选项卡
        top_tabs = QTabWidget()
        
        # 断点选项卡
        self.breakpoint_widget = BreakpointTableWidget()
        self.breakpoint_widget.breakpoint_toggled.connect(
            lambda bp_id, enabled: self.breakpoint_enabled.emit(bp_id, enabled)
        )
        self.breakpoint_widget.breakpoint_removed.connect(
            lambda bp_id: self.breakpoint_removed.emit(bp_id)
        )
        self.breakpoint_widget.breakpoint_condition_changed.connect(
            lambda bp_id, condition: self.breakpoint_condition_changed.emit(bp_id, condition)
        )
        
        top_tabs.addTab(self.breakpoint_widget, "断点")
        
        # 变量监视选项卡
        self.variable_watch_widget = VariableWatchWidget()
        self.variable_watch_widget.variable_added.connect(
            lambda var_name: self.variable_watch_added.emit(var_name)
        )
        self.variable_watch_widget.variable_removed.connect(
            lambda var_name: self.variable_watch_removed.emit(var_name)
        )
        
        top_tabs.addTab(self.variable_watch_widget, "变量监视")
        
        # 性能监控选项卡
        self.performance_widget = PerformanceWidget()
        top_tabs.addTab(self.performance_widget, "性能监控")
        
        # 下部选项卡
        bottom_tabs = QTabWidget()
        
        # 调试日志选项卡
        self.debug_log_widget = DebugLogWidget()
        bottom_tabs.addTab(self.debug_log_widget, "调试日志")
        
        # 添加到分割器
        splitter.addWidget(top_tabs)
        splitter.addWidget(bottom_tabs)
        
        # 设置初始大小
        splitter.setSizes([200, 300])
        
        main_layout.addWidget(splitter)
    
    def _create_debug_toolbar(self) -> QToolBar:
        """创建调试工具栏"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # 开始调试按钮
        self.start_debug_button = QToolButton()
        self.start_debug_button.setText("开始调试")
        self.start_debug_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        debug_menu = QMenu(self)
        normal_debug_action = debug_menu.addAction("调试模式")
        step_debug_action = debug_menu.addAction("单步模式")
        
        normal_debug_action.triggered.connect(
            lambda: self.debug_started.emit(ExecutionMode.DEBUG)
        )
        step_debug_action.triggered.connect(
            lambda: self.debug_started.emit(ExecutionMode.STEP)
        )
        
        self.start_debug_button.setMenu(debug_menu)
        self.start_debug_button.clicked.connect(
            lambda: self.debug_started.emit(ExecutionMode.DEBUG)
        )
        
        # 停止调试按钮
        self.stop_debug_button = QPushButton("停止调试")
        self.stop_debug_button.clicked.connect(self.debug_stopped.emit)
        
        # 暂停按钮
        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.debug_paused.emit)
        
        # 继续按钮
        self.resume_button = QPushButton("继续")
        self.resume_button.clicked.connect(self.debug_resumed.emit)
        
        # 单步执行按钮
        self.step_over_button = QPushButton("单步跳过")
        self.step_over_button.clicked.connect(self.debug_step_over.emit)
        
        self.step_into_button = QPushButton("单步进入")
        self.step_into_button.clicked.connect(self.debug_step_into.emit)
        
        self.step_out_button = QPushButton("单步跳出")
        self.step_out_button.clicked.connect(self.debug_step_out.emit)
        
        # 添加到工具栏
        toolbar.addWidget(self.start_debug_button)
        toolbar.addWidget(self.stop_debug_button)
        toolbar.addSeparator()
        toolbar.addWidget(self.pause_button)
        toolbar.addWidget(self.resume_button)
        toolbar.addSeparator()
        toolbar.addWidget(self.step_over_button)
        toolbar.addWidget(self.step_into_button)
        toolbar.addWidget(self.step_out_button)
        
        return toolbar
    
    def update_ui_state(self, is_debugging: bool, is_paused: bool):
        """更新UI状态"""
        self.start_debug_button.setEnabled(not is_debugging)
        self.stop_debug_button.setEnabled(is_debugging)
        self.pause_button.setEnabled(is_debugging and not is_paused)
        self.resume_button.setEnabled(is_debugging and is_paused)
        self.step_over_button.setEnabled(is_debugging and is_paused)
        self.step_into_button.setEnabled(is_debugging and is_paused)
        self.step_out_button.setEnabled(is_debugging and is_paused)
    
    def update_breakpoints(self, breakpoints: List[Dict[str, Any]]):
        """更新断点列表"""
        self.breakpoint_widget.update_breakpoints(breakpoints)
    
    def update_variables(self, variables: Dict[str, Any]):
        """更新变量列表"""
        self.variable_watch_widget.update_variables(variables)
    
    def update_performance_metrics(self, metrics: Dict[str, Any]):
        """更新性能指标"""
        self.performance_widget.update_metrics(metrics)
    
    def add_debug_log(self, log_entry: Dict[str, Any]):
        """添加调试日志"""
        self.debug_log_widget.add_log(log_entry)
    
    def clear_debug_logs(self):
        """清空调试日志"""
        self.debug_log_widget.clear_logs()
    
    def highlight_breakpoint(self, breakpoint_id: str):
        """高亮显示断点"""
        # 实现高亮显示断点的逻辑
        pass 