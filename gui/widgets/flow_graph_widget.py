#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程图编辑器主组件
集成视图和工具栏
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QAction, QComboBox,
    QLabel, QPushButton, QSplitter, QMenu, QSpinBox, QToolButton,
    QColorDialog, QSlider, QInputDialog, QFileDialog, QMessageBox, QDockWidget,
    QTabWidget, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QSize, QSettings, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor, QKeySequence

from typing import Dict, Any, List, Optional
import json
import os

from .flow_graph_view import FlowGraphView
from .flow_graph_node import FlowGraphNode
from .flow_graph_edge import FlowGraphEdge

class FlowGraphToolBar(QToolBar):
    """流程图工具栏"""
    
    def __init__(self, parent=None):
        """
        初始化工具栏
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # 初始化工具栏项
        self._init_toolbar_items()
    
    def _init_toolbar_items(self):
        """初始化工具栏项"""
        # 文件操作
        self.new_action = QAction("新建", self)
        self.new_action.setToolTip("新建流程图")
        
        self.open_action = QAction("打开", self)
        self.open_action.setToolTip("打开流程图文件")
        
        self.save_action = QAction("保存", self)
        self.save_action.setToolTip("保存流程图")
        
        self.save_as_action = QAction("另存为", self)
        self.save_as_action.setToolTip("将流程图保存为新文件")
        
        # 编辑操作
        self.delete_action = QAction("删除", self)
        self.delete_action.setToolTip("删除选中的项")
        
        # 节点操作
        self.add_node_normal_action = QAction("普通步骤", self)
        self.add_node_normal_action.setToolTip("添加普通步骤节点")
        
        self.add_node_condition_action = QAction("条件判断", self)
        self.add_node_condition_action.setToolTip("添加条件判断节点")
        
        self.add_node_loop_action = QAction("循环", self)
        self.add_node_loop_action.setToolTip("添加循环节点")
        
        self.add_node_start_action = QAction("开始", self)
        self.add_node_start_action.setToolTip("添加开始节点")
        
        self.add_node_end_action = QAction("结束", self)
        self.add_node_end_action.setToolTip("添加结束节点")
        
        # 视图操作
        self.zoom_in_action = QAction("放大", self)
        self.zoom_in_action.setToolTip("放大视图")
        
        self.zoom_out_action = QAction("缩小", self)
        self.zoom_out_action.setToolTip("缩小视图")
        
        self.fit_action = QAction("适应窗口", self)
        self.fit_action.setToolTip("适应窗口显示所有内容")
        
        # 添加到工具栏
        self.addAction(self.new_action)
        self.addAction(self.open_action)
        self.addAction(self.save_action)
        self.addAction(self.save_as_action)
        
        self.addSeparator()
        
        self.addAction(self.delete_action)
        
        self.addSeparator()
        
        # 添加节点的下拉菜单
        add_node_button = QToolButton()
        add_node_button.setText("添加节点")
        add_node_button.setToolTip("添加新节点")
        add_node_button.setPopupMode(QToolButton.InstantPopup)
        
        add_node_menu = QMenu(add_node_button)
        add_node_menu.addAction(self.add_node_normal_action)
        add_node_menu.addAction(self.add_node_condition_action)
        add_node_menu.addAction(self.add_node_loop_action)
        add_node_menu.addAction(self.add_node_start_action)
        add_node_menu.addAction(self.add_node_end_action)
        
        add_node_button.setMenu(add_node_menu)
        self.addWidget(add_node_button)
        
        self.addSeparator()
        
        self.addAction(self.zoom_in_action)
        self.addAction(self.zoom_out_action)
        self.addAction(self.fit_action)

class FlowGraphOutliner(QTreeWidget):
    """流程图大纲视图"""
    
    node_selected = pyqtSignal(str)  # node_id
    
    def __init__(self, parent=None):
        """
        初始化大纲视图
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置列
        self.setColumnCount(3)
        self.setHeaderLabels(["节点", "类型", "ID"])
        
        # 调整列宽
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 80)
        
        # 允许选择
        self.setSelectionMode(QTreeWidget.SingleSelection)
        
        # 连接信号
        self.itemSelectionChanged.connect(self._on_selection_changed)
    
    def update_nodes(self, nodes: Dict[str, Any]):
        """
        更新节点列表
        
        Args:
            nodes: 节点字典 {node_id: node_data}
        """
        # 清空当前项
        self.clear()
        
        # 添加节点
        for node_id, node_data in nodes.items():
            item = QTreeWidgetItem()
            item.setText(0, node_data.get("title", "未命名"))
            item.setText(1, node_data.get("type", ""))
            item.setText(2, node_id)
            
            # 设置图标
            node_type = node_data.get("type", "")
            if node_type == FlowGraphNode.TYPE_START:
                # 开始节点
                pass
            elif node_type == FlowGraphNode.TYPE_END:
                # 结束节点
                pass
            elif node_type == FlowGraphNode.TYPE_CONDITION:
                # 条件节点
                pass
            elif node_type == FlowGraphNode.TYPE_LOOP:
                # 循环节点
                pass
            
            # 添加到树
            self.addTopLevelItem(item)
    
    def _on_selection_changed(self):
        """处理选择变更事件"""
        # 获取选中项
        items = self.selectedItems()
        if not items:
            return
        
        # 获取节点ID
        node_id = items[0].text(2)
        if node_id:
            self.node_selected.emit(node_id)

class FlowGraphWidget(QWidget):
    """流程图编辑器主组件"""
    
    # 信号
    graph_changed = pyqtSignal()  # 图形变化信号
    node_selected = pyqtSignal(str, dict)  # node_id, node_data
    edge_selected = pyqtSignal(str, dict)  # edge_id, edge_data
    
    def __init__(self, parent=None):
        """
        初始化流程图编辑器
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 文件路径
        self._current_file_path = None
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 初始化视图
        self._view.add_default_nodes()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        self._splitter = QSplitter(Qt.Horizontal)
        
        # 创建工具栏
        self._toolbar = FlowGraphToolBar(self)
        main_layout.addWidget(self._toolbar)
        
        # 创建大纲视图
        self._outliner = FlowGraphOutliner(self)
        self._splitter.addWidget(self._outliner)
        
        # 创建流程图视图
        self._view = FlowGraphView(self)
        self._splitter.addWidget(self._view)
        
        # 设置分割器初始大小
        self._splitter.setSizes([200, 800])
        
        # 添加分割器到主布局
        main_layout.addWidget(self._splitter)
        
        # 设置布局
        self.setLayout(main_layout)
    
    def _connect_signals(self):
        """连接信号"""
        # 工具栏信号
        self._toolbar.new_action.triggered.connect(self._on_new)
        self._toolbar.open_action.triggered.connect(self._on_open)
        self._toolbar.save_action.triggered.connect(self._on_save)
        self._toolbar.save_as_action.triggered.connect(self._on_save_as)
        self._toolbar.delete_action.triggered.connect(self._on_delete)
        
        self._toolbar.add_node_normal_action.triggered.connect(
            lambda: self._view.get_scene().add_node(FlowGraphNode.TYPE_NORMAL))
        self._toolbar.add_node_condition_action.triggered.connect(
            lambda: self._view.get_scene().add_node(FlowGraphNode.TYPE_CONDITION))
        self._toolbar.add_node_loop_action.triggered.connect(
            lambda: self._view.get_scene().add_node(FlowGraphNode.TYPE_LOOP))
        self._toolbar.add_node_start_action.triggered.connect(
            lambda: self._view.get_scene().add_node(FlowGraphNode.TYPE_START))
        self._toolbar.add_node_end_action.triggered.connect(
            lambda: self._view.get_scene().add_node(FlowGraphNode.TYPE_END))
        
        self._toolbar.zoom_in_action.triggered.connect(
            lambda: self._view.scale_view(self._view._zoom_in_factor))
        self._toolbar.zoom_out_action.triggered.connect(
            lambda: self._view.scale_view(self._view._zoom_out_factor))
        self._toolbar.fit_action.triggered.connect(self._view.fit_all)
        
        # 视图信号
        self._view.graph_changed.connect(self._on_graph_changed)
        self._view.node_selected.connect(self._on_node_selected)
        
        # 大纲视图信号
        self._outliner.node_selected.connect(self._on_outliner_node_selected)
    
    def _on_new(self):
        """新建流程图"""
        # 提示保存当前文件
        if self._current_file_path or self._view.get_scene().to_dict()["nodes"]:
            reply = QMessageBox.question(
                self, "新建流程图", "是否保存当前流程图?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self._on_save()
            elif reply == QMessageBox.Cancel:
                return
        
        # 清空流程图
        self._view.clear_graph()
        self._view.add_default_nodes()
        
        # 重置文件路径
        self._current_file_path = None
    
    def _on_open(self):
        """打开流程图"""
        # 提示保存当前文件
        if self._current_file_path or self._view.get_scene().to_dict()["nodes"]:
            reply = QMessageBox.question(
                self, "打开流程图", "是否保存当前流程图?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self._on_save()
            elif reply == QMessageBox.Cancel:
                return
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开流程图", "", "流程图文件 (*.flow);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # 加载图形数据
            self._view.get_scene().from_dict(graph_data)
            
            # 更新文件路径
            self._current_file_path = file_path
            
            # 适应视图
            self._view.fit_all()
            
            # 更新大纲视图
            self._update_outliner()
            
            QMessageBox.information(self, "打开成功", f"流程图已从{file_path}加载")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", f"无法打开流程图: {str(e)}")
    
    def _on_save(self):
        """保存流程图"""
        if not self._current_file_path:
            self._on_save_as()
            return
        
        try:
            # 获取图形数据
            graph_data = self._view.get_scene().to_dict()
            
            # 写入文件
            with open(self._current_file_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "保存成功", f"流程图已保存到: {self._current_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存流程图: {str(e)}")
    
    def _on_save_as(self):
        """另存为流程图"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存流程图", "", "流程图文件 (*.flow);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        # 添加扩展名
        if not file_path.lower().endswith('.flow'):
            file_path += '.flow'
        
        try:
            # 获取图形数据
            graph_data = self._view.get_scene().to_dict()
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            # 更新文件路径
            self._current_file_path = file_path
            
            QMessageBox.information(self, "保存成功", f"流程图已保存到: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存流程图: {str(e)}")
    
    def _on_delete(self):
        """删除选中的项"""
        self._view._delete_selected_items()
    
    def _on_graph_changed(self):
        """处理图形变化事件"""
        # 更新大纲视图
        self._update_outliner()
        
        # 发射信号
        self.graph_changed.emit()
    
    def _on_node_selected(self, node_id: str):
        """处理节点选择事件"""
        # 在大纲视图中选中节点
        for i in range(self._outliner.topLevelItemCount()):
            item = self._outliner.topLevelItem(i)
            if item.text(2) == node_id:
                self._outliner.setCurrentItem(item)
                break
        
        # 获取节点数据
        node = self._view.get_scene()._nodes.get(node_id)
        if node:
            node_data = node.to_dict()
            self.node_selected.emit(node_id, node_data)
    
    def _on_outliner_node_selected(self, node_id: str):
        """处理大纲视图节点选择事件"""
        # 获取节点对象
        node = self._view.get_scene()._nodes.get(node_id)
        if node:
            # 选中节点
            node.setSelected(True)
            
            # 视图居中到节点
            self._view.centerOn(node)
            
            # 发射信号
            node_data = node.to_dict()
            self.node_selected.emit(node_id, node_data)
    
    def _update_outliner(self):
        """更新大纲视图"""
        # 获取节点数据
        nodes = {}
        for node_id, node in self._view.get_scene()._nodes.items():
            nodes[node_id] = node.to_dict()
        
        # 更新大纲视图
        self._outliner.update_nodes(nodes)
    
    def save_state(self, settings: QSettings, group: str = "FlowGraphWidget"):
        """
        保存组件状态
        
        Args:
            settings: QSettings对象
            group: 设置组名
        """
        settings.beginGroup(group)
        
        # 保存分割器状态
        settings.setValue("splitter_state", self._splitter.saveState())
        
        # 保存视图状态
        self._view.save_view_state(settings, "view")
        
        # 保存当前文件路径
        if self._current_file_path:
            settings.setValue("current_file_path", self._current_file_path)
        
        settings.endGroup()
    
    def restore_state(self, settings: QSettings, group: str = "FlowGraphWidget"):
        """
        恢复组件状态
        
        Args:
            settings: QSettings对象
            group: 设置组名
        """
        settings.beginGroup(group)
        
        # 恢复分割器状态
        splitter_state = settings.value("splitter_state")
        if splitter_state:
            self._splitter.restoreState(splitter_state)
        
        # 恢复视图状态
        self._view.restore_view_state(settings, "view")
        
        # 恢复当前文件
        file_path = settings.value("current_file_path")
        if file_path and os.path.exists(file_path):
            self._current_file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                
                self._view.get_scene().from_dict(graph_data)
                self._view.fit_all()
                self._update_outliner()
            except:
                # 文件加载失败，忽略
                pass
        
        settings.endGroup()
    
    def export_flow_data(self) -> Dict[str, Any]:
        """
        导出流程数据，用于转换为DrissionPage自动化流程
        
        Returns:
            流程数据字典
        """
        # 获取图形数据
        graph_data = self._view.get_scene().to_dict()
        
        # 转换为流程数据
        flow_data = {
            "steps": [],
            "connections": []
        }
        
        # 添加节点数据
        for node_id, node_data in graph_data["nodes"].items():
            step_data = {
                "id": node_id,
                "type": node_data["type"],
                "title": node_data["title"],
                "data": node_data["data"],
                "position": node_data["position"]
            }
            flow_data["steps"].append(step_data)
        
        # 添加连接数据
        for edge_id, edge_data in graph_data["edges"].items():
            connection_data = {
                "id": edge_id,
                "source": edge_data["source_node"],
                "source_port": edge_data["source_port"],
                "target": edge_data["target_node"],
                "target_port": edge_data["target_port"],
                "type": edge_data["type"]
            }
            flow_data["connections"].append(connection_data)
        
        return flow_data
    
    def import_flow_data(self, flow_data: Dict[str, Any]):
        """
        导入流程数据，用于从DrissionPage自动化流程转换
        
        Args:
            flow_data: 流程数据字典
        """
        # 转换为图形数据
        graph_data = {
            "nodes": {},
            "edges": {}
        }
        
        # 添加节点数据
        for step_data in flow_data.get("steps", []):
            node_id = step_data.get("id")
            if not node_id:
                continue
            
            node_data = {
                "id": node_id,
                "title": step_data.get("title", "未命名"),
                "type": step_data.get("type", FlowGraphNode.TYPE_NORMAL),
                "data": step_data.get("data", {}),
                "position": step_data.get("position", {"x": 0, "y": 0}),
                "input_ports": {},
                "output_ports": {}
            }
            
            # 根据类型添加默认端口
            node_type = node_data["type"]
            if node_type == FlowGraphNode.TYPE_START:
                node_data["output_ports"] = {"out": {"name": "下一步", "position": "bottom", "connected": False}}
            elif node_type == FlowGraphNode.TYPE_END:
                node_data["input_ports"] = {"in": {"name": "上一步", "position": "top", "connected": False}}
            elif node_type == FlowGraphNode.TYPE_CONDITION:
                node_data["input_ports"] = {"in": {"name": "上一步", "position": "top", "connected": False}}
                node_data["output_ports"] = {
                    "true": {"name": "是", "position": "right", "connected": False},
                    "false": {"name": "否", "position": "bottom", "connected": False}
                }
            elif node_type == FlowGraphNode.TYPE_LOOP:
                node_data["input_ports"] = {
                    "in": {"name": "上一步", "position": "top", "connected": False},
                    "loop_back": {"name": "循环回", "position": "left", "connected": False}
                }
                node_data["output_ports"] = {
                    "loop_body": {"name": "循环体", "position": "right", "connected": False},
                    "out": {"name": "跳出循环", "position": "bottom", "connected": False}
                }
            else:
                node_data["input_ports"] = {"in": {"name": "上一步", "position": "top", "connected": False}}
                node_data["output_ports"] = {"out": {"name": "下一步", "position": "bottom", "connected": False}}
            
            graph_data["nodes"][node_id] = node_data
        
        # 添加边数据
        for connection_data in flow_data.get("connections", []):
            edge_id = connection_data.get("id")
            if not edge_id:
                continue
            
            edge_data = {
                "id": edge_id,
                "source_node": connection_data.get("source", ""),
                "source_port": connection_data.get("source_port", ""),
                "target_node": connection_data.get("target", ""),
                "target_port": connection_data.get("target_port", ""),
                "type": connection_data.get("type", FlowGraphEdge.TYPE_BEZIER)
            }
            
            graph_data["edges"][edge_id] = edge_data
        
        # 加载图形数据
        self._view.get_scene().from_dict(graph_data)
        
        # 适应视图
        self._view.fit_all()
        
        # 更新大纲视图
        self._update_outliner() 