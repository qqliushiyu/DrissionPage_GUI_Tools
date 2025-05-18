#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程图场景组件
管理节点和边的交互
"""

from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsItem,
    QMenu, QAction, QInputDialog, QDialog, QVBoxLayout,
    QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel,
    QMessageBox
)
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QObject
from PyQt5.QtGui import QPen, QBrush, QColor, QCursor

from typing import Dict, Any, List, Optional, Tuple, Set
import uuid
import json

from .flow_graph_node import FlowGraphNode
from .flow_graph_edge import FlowGraphEdge


class NodeEditDialog(QDialog):
    """节点编辑对话框"""
    
    def __init__(self, node_data: Dict[str, Any] = None, parent=None):
        """
        初始化节点编辑对话框
        
        Args:
            node_data: 节点数据
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.setWindowTitle("编辑节点")
        self.resize(400, 300)
        
        # 初始数据
        self._node_data = node_data or {}
        
        # 初始化UI
        self._init_ui()
        
        # 填充数据
        self._fill_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建表单
        form_layout = QFormLayout()
        
        # 节点标题
        self.title_edit = QLineEdit()
        form_layout.addRow("节点标题:", self.title_edit)
        
        # 节点类型
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            FlowGraphNode.TYPE_NORMAL,
            FlowGraphNode.TYPE_CONDITION,
            FlowGraphNode.TYPE_LOOP,
            FlowGraphNode.TYPE_START,
            FlowGraphNode.TYPE_END
        ])
        form_layout.addRow("节点类型:", self.type_combo)
        
        # 数据编辑
        self.data_edit = QLineEdit()
        form_layout.addRow("节点数据:", self.data_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_layout = QVBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _fill_data(self):
        """填充数据"""
        self.title_edit.setText(self._node_data.get("title", ""))
        
        node_type = self._node_data.get("type", FlowGraphNode.TYPE_NORMAL)
        index = self.type_combo.findText(node_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # 数据转为JSON字符串
        data_str = json.dumps(self._node_data.get("data", {}), ensure_ascii=False)
        self.data_edit.setText(data_str)
    
    def get_node_data(self) -> Dict[str, Any]:
        """获取节点数据"""
        # 处理数据JSON
        try:
            data = json.loads(self.data_edit.text())
        except:
            data = {}
        
        return {
            "title": self.title_edit.text(),
            "type": self.type_combo.currentText(),
            "data": data
        }


class FlowGraphScene(QGraphicsScene):
    """流程图场景"""
    
    # 信号
    node_selected = pyqtSignal(str)  # node_id
    node_moved = pyqtSignal(str, QPointF)  # node_id, new_position
    node_double_clicked = pyqtSignal(str)  # node_id
    edge_selected = pyqtSignal(str)  # edge_id
    graph_changed = pyqtSignal()  # 图形变化信号
    
    def __init__(self, parent=None):
        """
        初始化流程图场景
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        # 节点和边的存储
        self._nodes = {}  # {node_id: FlowGraphNode}
        self._edges = {}  # {edge_id: FlowGraphEdge}
        
        # 临时连线状态
        self._temp_edge = None
        self._source_node = None
        self._source_port = None
        self._is_connecting = False
        
        # 网格设置
        self._grid_size = 20
        self._draw_grid = True
        
        # 外观设置
        self._bg_color = QColor(250, 250, 250)
        self._grid_color = QColor(200, 200, 200)
        
        # 设置场景矩形
        self.setSceneRect(QRectF(0, 0, 3000, 2000))
        
        # 初始化场景
        self._setup_scene()
    
    def _setup_scene(self):
        """初始化场景"""
        # 设置背景色
        self.setBackgroundBrush(QBrush(self._bg_color))
    
    def drawBackground(self, painter, rect):
        """绘制场景背景"""
        super().drawBackground(painter, rect)
        
        # 绘制网格
        if self._draw_grid:
            # 设置网格样式
            painter.setPen(QPen(self._grid_color, 0.5))
            
            # 计算可见区域的网格线
            left = int(rect.left()) - (int(rect.left()) % self._grid_size)
            top = int(rect.top()) - (int(rect.top()) % self._grid_size)
            
            # 绘制垂直线
            lines = []
            for x in range(left, int(rect.right()), self._grid_size):
                lines.append(QPointF(x, rect.top()))
                lines.append(QPointF(x, rect.bottom()))
            
            # 绘制水平线
            for y in range(top, int(rect.bottom()), self._grid_size):
                lines.append(QPointF(rect.left(), y))
                lines.append(QPointF(rect.right(), y))
            
            # 批量绘制
            painter.drawLines(lines)
    
    def add_node(self, node_type: str, pos: QPointF = None, title: str = None, node_data: Dict[str, Any] = None) -> str:
        """
        添加节点
        
        Args:
            node_type: 节点类型
            pos: 节点位置，如果为None则使用当前鼠标位置
            title: 节点标题，如果为None则使用节点类型
            node_data: 节点数据
            
        Returns:
            节点ID
        """
        # 生成唯一ID
        node_id = str(uuid.uuid4())
        
        # 设置标题
        if title is None:
            title = node_type.capitalize()
        
        # 创建节点
        node = FlowGraphNode(node_id, title, node_type)
        
        # 设置位置
        if pos is None:
            view = self.views()[0] if self.views() else None
            if view:
                pos = view.mapToScene(view.mapFromGlobal(QCursor.pos()))
            else:
                pos = QPointF(0, 0)
        
        # 设置位置并对齐到网格
        grid_pos = self._snap_to_grid(pos)
        node.setPos(grid_pos)
        
        # 设置节点数据
        if node_data:
            node.set_data(node_data)
        
        # 连接信号
        node.node_moved.connect(self._on_node_moved)
        node.node_selected.connect(self._on_node_selected)
        node.node_double_clicked.connect(self._on_node_double_clicked)
        node.node_context_menu.connect(self._on_node_context_menu)
        
        # 添加到场景和内部存储
        self.addItem(node)
        self._nodes[node_id] = node
        
        # 发射图形变化信号
        self.graph_changed.emit()
        
        return node_id
    
    def add_edge(self, source_node: str, source_port: str, target_node: str, target_port: str, edge_type: str = FlowGraphEdge.TYPE_BEZIER) -> str:
        """
        添加连线
        
        Args:
            source_node: 源节点ID
            source_port: 源节点端口ID
            target_node: 目标节点ID
            target_port: 目标节点端口ID
            edge_type: 连线类型
            
        Returns:
            连线ID
        """
        # 检查节点是否存在
        if source_node not in self._nodes or target_node not in self._nodes:
            return None
        
        # 生成唯一ID
        edge_id = str(uuid.uuid4())
        
        # 创建连线
        edge = FlowGraphEdge(edge_id, source_node, source_port, target_node, target_port, edge_type)
        
        # 设置端点坐标
        source_pos = self._nodes[source_node].get_port_position(source_port, False)
        target_pos = self._nodes[target_node].get_port_position(target_port, True)
        
        edge.set_source_point(source_pos)
        edge.set_target_point(target_pos)
        
        # 添加到场景和内部存储
        self.addItem(edge)
        self._edges[edge_id] = edge
        
        # 更新端口连接状态
        self._nodes[source_node].set_port_connected(source_port, False, True)
        self._nodes[target_node].set_port_connected(target_port, True, True)
        
        # 发射图形变化信号
        self.graph_changed.emit()
        
        return edge_id
    
    def _on_node_moved(self, node_id: str, new_pos: QPointF):
        """处理节点移动事件"""
        node = self._nodes.get(node_id)
        if not node:
            return
        
        # 更新连接到此节点的所有边的端点位置
        for edge_id, edge in self._edges.items():
            source_node, source_port = edge.get_source()
            target_node, target_port = edge.get_target()
            
            if source_node == node_id:
                source_pos = node.get_port_position(source_port, False)
                edge.set_source_point(source_pos)
            
            if target_node == node_id:
                target_pos = node.get_port_position(target_port, True)
                edge.set_target_point(target_pos)
        
        # 发射节点移动信号
        self.node_moved.emit(node_id, new_pos)
        
        # 发射图形变化信号
        self.graph_changed.emit()
    
    def _on_node_selected(self, node_id: str):
        """处理节点选择事件"""
        # 清除其他选择
        for item in self.selectedItems():
            if item != self._nodes.get(node_id):
                item.setSelected(False)
        
        # 发射节点选择信号
        self.node_selected.emit(node_id)
    
    def _on_node_double_clicked(self, node_id: str):
        """处理节点双击事件"""
        # 打开节点编辑对话框
        node = self._nodes.get(node_id)
        if not node:
            return
        
        node_data = {
            "title": node.get_title(),
            "type": node.get_type(),
            "data": node.get_data()
        }
        
        dialog = NodeEditDialog(node_data, self.views()[0] if self.views() else None)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_node_data()
            
            # 更新节点
            node.set_title(new_data["title"])
            # 类型已设置时不能更改（会影响端口等）
            # node.set_type(new_data["type"])
            node.set_data(new_data["data"])
            
            # 发射图形变化信号
            self.graph_changed.emit()
        
        # 发射节点双击信号
        self.node_double_clicked.emit(node_id)
    
    def _on_node_context_menu(self, node_id: str, pos: QPointF):
        """处理节点右键菜单事件"""
        node = self._nodes.get(node_id)
        if not node:
            return
        
        menu = QMenu()
        
        # 编辑节点
        edit_action = QAction("编辑节点", menu)
        edit_action.triggered.connect(lambda: self._on_node_double_clicked(node_id))
        
        # 删除节点
        delete_action = QAction("删除节点", menu)
        delete_action.triggered.connect(lambda: self.delete_node(node_id))
        
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        
        menu.exec_(pos.toPoint())
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标按下事件"""
        # 检查是否点击在端口上
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, FlowGraphNode):
                port_id, is_input = item.get_port_at_pos(event.scenePos())
                if port_id is not None and not is_input:  # 只能从输出端口开始连线
                    # 开始连线
                    self._is_connecting = True
                    self._source_node = item.get_id()
                    self._source_port = port_id
                    
                    # 创建临时连线
                    self._temp_edge = FlowGraphEdge("temp", self._source_node, self._source_port, "", "")
                    self._temp_edge.set_source_point(item.get_port_position(port_id, False))
                    self._temp_edge.set_target_point(event.scenePos())
                    self.addItem(self._temp_edge)
                    
                    # 阻止事件传递
                    return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标移动事件"""
        # 更新临时连线
        if self._is_connecting and self._temp_edge:
            self._temp_edge.set_target_point(event.scenePos())
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标释放事件"""
        # 完成连线
        if self._is_connecting and self._temp_edge and event.button() == Qt.LeftButton:
            # 检查释放位置是否在输入端口上
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, FlowGraphNode):
                port_id, is_input = item.get_port_at_pos(event.scenePos())
                if port_id is not None and is_input:
                    # 确认目标节点和端口
                    target_node = item.get_id()
                    target_port = port_id
                    
                    # 不允许连接到自己
                    if target_node != self._source_node:
                        # 添加正式连线
                        self.add_edge(self._source_node, self._source_port, target_node, target_port)
            
            # 移除临时连线
            if self._temp_edge:
                self.removeItem(self._temp_edge)
                self._temp_edge = None
            
            # 重置连线状态
            self._is_connecting = False
            self._source_node = None
            self._source_port = None
        
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event: QGraphicsSceneMouseEvent):
        """处理右键菜单事件"""
        # 如果点击在项上，则使用项的菜单
        if self.itemAt(event.scenePos(), self.views()[0].transform()):
            super().contextMenuEvent(event)
            return
        
        # 场景菜单
        menu = QMenu()
        
        # 添加节点子菜单
        add_node_menu = QMenu("添加节点", menu)
        
        # 常规节点
        add_normal_action = QAction("普通步骤", add_node_menu)
        add_normal_action.triggered.connect(lambda: self.add_node(FlowGraphNode.TYPE_NORMAL, event.scenePos()))
        
        # 条件节点
        add_condition_action = QAction("条件判断", add_node_menu)
        add_condition_action.triggered.connect(lambda: self.add_node(FlowGraphNode.TYPE_CONDITION, event.scenePos()))
        
        # 循环节点
        add_loop_action = QAction("循环", add_node_menu)
        add_loop_action.triggered.connect(lambda: self.add_node(FlowGraphNode.TYPE_LOOP, event.scenePos()))
        
        # 开始节点
        add_start_action = QAction("开始", add_node_menu)
        add_start_action.triggered.connect(lambda: self.add_node(FlowGraphNode.TYPE_START, event.scenePos()))
        
        # 结束节点
        add_end_action = QAction("结束", add_node_menu)
        add_end_action.triggered.connect(lambda: self.add_node(FlowGraphNode.TYPE_END, event.scenePos()))
        
        add_node_menu.addAction(add_normal_action)
        add_node_menu.addAction(add_condition_action)
        add_node_menu.addAction(add_loop_action)
        add_node_menu.addAction(add_start_action)
        add_node_menu.addAction(add_end_action)
        
        # 粘贴节点
        paste_action = QAction("粘贴", menu)
        paste_action.triggered.connect(lambda: self._paste_node(event.scenePos()))
        
        # 导出/导入
        export_action = QAction("导出流程图", menu)
        export_action.triggered.connect(self._export_graph)
        
        import_action = QAction("导入流程图", menu)
        import_action.triggered.connect(self._import_graph)
        
        # 网格设置
        toggle_grid_action = QAction("显示/隐藏网格", menu)
        toggle_grid_action.triggered.connect(self._toggle_grid)
        
        # 添加菜单项
        menu.addMenu(add_node_menu)
        menu.addAction(paste_action)
        menu.addSeparator()
        menu.addAction(export_action)
        menu.addAction(import_action)
        menu.addSeparator()
        menu.addAction(toggle_grid_action)
        
        # 显示菜单
        menu.exec_(event.screenPos().toPoint())
    
    def _snap_to_grid(self, pos: QPointF) -> QPointF:
        """将位置吸附到网格"""
        x = round(pos.x() / self._grid_size) * self._grid_size
        y = round(pos.y() / self._grid_size) * self._grid_size
        return QPointF(x, y)
    
    def _toggle_grid(self):
        """切换网格显示状态"""
        self._draw_grid = not self._draw_grid
        self.update()
    
    def delete_node(self, node_id: str):
        """删除节点"""
        node = self._nodes.get(node_id)
        if not node:
            return
        
        # 找出与此节点相连的所有边
        edges_to_remove = []
        for edge_id, edge in self._edges.items():
            source_node, _ = edge.get_source()
            target_node, _ = edge.get_target()
            
            if source_node == node_id or target_node == node_id:
                edges_to_remove.append(edge_id)
        
        # 删除相关边
        for edge_id in edges_to_remove:
            edge = self._edges.pop(edge_id, None)
            if edge:
                self.removeItem(edge)
        
        # 删除节点
        self.removeItem(node)
        self._nodes.pop(node_id, None)
        
        # 发射图形变化信号
        self.graph_changed.emit()
    
    def delete_edge(self, edge_id: str):
        """删除连线"""
        edge = self._edges.get(edge_id)
        if not edge:
            return
        
        # 更新端口连接状态
        source_node, source_port = edge.get_source()
        target_node, target_port = edge.get_target()
        
        if source_node in self._nodes:
            self._nodes[source_node].set_port_connected(source_port, False, False)
        
        if target_node in self._nodes:
            self._nodes[target_node].set_port_connected(target_port, True, False)
        
        # 删除连线
        self.removeItem(edge)
        self._edges.pop(edge_id, None)
        
        # 发射图形变化信号
        self.graph_changed.emit()
    
    def _paste_node(self, pos: QPointF):
        """在指定位置粘贴节点"""
        # 这里可以实现剪贴板功能，暂不实现
        pass
    
    def _export_graph(self):
        """导出流程图"""
        # 这里可以实现导出功能，暂不实现
        graph_data = self.to_dict()
        print(json.dumps(graph_data, indent=2, ensure_ascii=False))
    
    def _import_graph(self):
        """导入流程图"""
        # 这里可以实现导入功能，暂不实现
        pass
    
    def clear_graph(self):
        """清空流程图"""
        # 清空所有项
        self.clear()
        
        # 清空内部存储
        self._nodes.clear()
        self._edges.clear()
        
        # 重置临时状态
        self._temp_edge = None
        self._source_node = None
        self._source_port = None
        self._is_connecting = False
        
        # 发射图形变化信号
        self.graph_changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        """将流程图转换为字典格式"""
        nodes = {}
        for node_id, node in self._nodes.items():
            nodes[node_id] = node.to_dict()
        
        edges = {}
        for edge_id, edge in self._edges.items():
            edges[edge_id] = edge.to_dict()
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载流程图"""
        # 清空当前流程图
        self.clear_graph()
        
        # 加载节点
        for node_id, node_data in data.get("nodes", {}).items():
            node = FlowGraphNode.from_dict(node_data)
            self.addItem(node)
            self._nodes[node_id] = node
            
            # 连接信号
            node.node_moved.connect(self._on_node_moved)
            node.node_selected.connect(self._on_node_selected)
            node.node_double_clicked.connect(self._on_node_double_clicked)
            node.node_context_menu.connect(self._on_node_context_menu)
        
        # 加载边
        for edge_id, edge_data in data.get("edges", {}).items():
            edge = FlowGraphEdge.from_dict(edge_data)
            
            # 设置端点坐标
            source_node = edge_data["source_node"]
            source_port = edge_data["source_port"]
            target_node = edge_data["target_node"]
            target_port = edge_data["target_port"]
            
            if source_node in self._nodes and target_node in self._nodes:
                source_pos = self._nodes[source_node].get_port_position(source_port, False)
                target_pos = self._nodes[target_node].get_port_position(target_port, True)
                
                edge.set_source_point(source_pos)
                edge.set_target_point(target_pos)
                
                self.addItem(edge)
                self._edges[edge_id] = edge
                
                # 更新端口连接状态
                self._nodes[source_node].set_port_connected(source_port, False, True)
                self._nodes[target_node].set_port_connected(target_port, True, True)
        
        # 发射图形变化信号
        self.graph_changed.emit() 