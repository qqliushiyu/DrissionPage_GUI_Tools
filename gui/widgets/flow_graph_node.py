#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程图节点组件
实现可拖拽、可连接的流程图节点
"""

from PyQt5.QtWidgets import (
    QGraphicsItem, QGraphicsObject, QGraphicsTextItem,
    QGraphicsRectItem, QMenu, QAction, QInputDialog, QGraphicsSceneMouseEvent
)
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSizeF
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath, QFont, QCursor, QFontMetrics

from typing import Dict, Any, List, Optional, Tuple, Set

class FlowGraphNode(QGraphicsObject):
    """流程图节点"""
    
    # 节点状态信号
    node_moved = pyqtSignal(str, QPointF)  # node_id, new_position
    node_selected = pyqtSignal(str)  # node_id
    node_double_clicked = pyqtSignal(str)  # node_id
    node_context_menu = pyqtSignal(str, QPointF)  # node_id, global_pos
    
    # 连接点信号
    port_connected = pyqtSignal(str, str, str, str)  # source_node_id, source_port, target_node_id, target_port
    
    # 节点类型
    TYPE_NORMAL = "normal"  # 普通步骤节点
    TYPE_CONDITION = "condition"  # 条件节点
    TYPE_LOOP = "loop"  # 循环节点
    TYPE_START = "start"  # 开始节点
    TYPE_END = "end"  # 结束节点
    
    # 端口位置
    PORT_TOP = "top"
    PORT_RIGHT = "right"
    PORT_BOTTOM = "bottom"
    PORT_LEFT = "left"
    
    def __init__(self, node_id: str, title: str, node_type: str = TYPE_NORMAL, parent=None):
        """
        初始化节点
        
        Args:
            node_id: 节点唯一标识
            title: 节点标题
            node_type: 节点类型
            parent: 父项
        """
        super().__init__(parent)
        
        self._id = node_id
        self._title = title
        self._type = node_type
        self._data = {}  # 节点数据
        
        # 节点尺寸
        self._width = 160
        self._height = 80
        
        # 节点状态
        self._selected = False
        self._hovered = False
        self._dragging = False
        
        # 端口信息
        self._input_ports = {}  # 输入端口: {port_id: {name, position, connected}}
        self._output_ports = {}  # 输出端口: {port_id: {name, position, connected}}
        self._port_radius = 6
        
        # 外观设置
        self._title_height = 24
        self._title_color = self._get_title_color()
        self._body_color = QColor(240, 240, 240)
        self._border_color = QColor(180, 180, 180)
        self._border_width = 1.5
        self._selected_border_color = QColor(0, 120, 215)
        self._selected_border_width = 2.5
        self._corner_radius = 6
        
        # 设置节点可选、可移动
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setAcceptHoverEvents(True)
        
        # 添加默认端口
        self._setup_default_ports()
    
    def _get_title_color(self) -> QColor:
        """根据节点类型获取标题栏颜色"""
        if self._type == self.TYPE_CONDITION:
            return QColor(237, 125, 49)  # 橙色
        elif self._type == self.TYPE_LOOP:
            return QColor(112, 173, 71)  # 绿色
        elif self._type == self.TYPE_START:
            return QColor(91, 155, 213)  # 蓝色
        elif self._type == self.TYPE_END:
            return QColor(192, 80, 77)  # 红色
        else:
            return QColor(68, 114, 196)  # 蓝紫色
    
    def _setup_default_ports(self):
        """设置默认端口"""
        if self._type == self.TYPE_START:
            # 开始节点只有输出端口
            self.add_output_port("out", "下一步", self.PORT_BOTTOM)
        elif self._type == self.TYPE_END:
            # 结束节点只有输入端口
            self.add_input_port("in", "上一步", self.PORT_TOP)
        elif self._type == self.TYPE_CONDITION:
            # 条件节点有一个输入和两个输出
            self.add_input_port("in", "上一步", self.PORT_TOP)
            self.add_output_port("true", "是", self.PORT_RIGHT)
            self.add_output_port("false", "否", self.PORT_BOTTOM)
        elif self._type == self.TYPE_LOOP:
            # 循环节点有两个输入和两个输出
            self.add_input_port("in", "上一步", self.PORT_TOP)
            self.add_input_port("loop_back", "循环回", self.PORT_LEFT)
            self.add_output_port("loop_body", "循环体", self.PORT_RIGHT)
            self.add_output_port("out", "跳出循环", self.PORT_BOTTOM)
        else:
            # 普通节点有一个输入和一个输出
            self.add_input_port("in", "上一步", self.PORT_TOP)
            self.add_output_port("out", "下一步", self.PORT_BOTTOM)
    
    def boundingRect(self) -> QRectF:
        """获取节点的包围矩形"""
        return QRectF(0, 0, self._width, self._height)
    
    def paint(self, painter, option, widget=None):
        """绘制节点"""
        # 绘制节点主体
        path = QPainterPath()
        path.addRoundedRect(0, 0, self._width, self._height, self._corner_radius, self._corner_radius)
        
        # 填充主体
        painter.setBrush(QBrush(self._body_color))
        
        # 设置边框
        if self._selected:
            painter.setPen(QPen(self._selected_border_color, self._selected_border_width))
        else:
            painter.setPen(QPen(self._border_color, self._border_width))
        
        # 绘制主体
        painter.drawPath(path)
        
        # 绘制标题栏
        title_path = QPainterPath()
        title_path.addRoundedRect(0, 0, self._width, self._title_height, 
                                 self._corner_radius, self._corner_radius)
        title_path.addRect(0, self._title_height / 2, self._width, self._title_height / 2)
        
        painter.setBrush(QBrush(self._title_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(title_path)
        
        # 绘制标题文本
        painter.setPen(Qt.white)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        
        # 计算标题文本位置，居中显示
        metrics = QFontMetrics(font)
        title_width = metrics.horizontalAdvance(self._title)
        title_x = (self._width - title_width) / 2
        title_y = self._title_height / 2 + metrics.height() / 4
        
        painter.drawText(QPointF(title_x, title_y), self._title)
        
        # 绘制端口
        self._paint_ports(painter)
    
    def _paint_ports(self, painter):
        """绘制端口"""
        # 设置端口样式
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(self._border_color, 1.5))
        
        # 绘制输入端口
        for port_id, port_info in self._input_ports.items():
            position = self._get_port_position(port_info["position"])
            painter.drawEllipse(position, self._port_radius, self._port_radius)
        
        # 绘制输出端口
        for port_id, port_info in self._output_ports.items():
            position = self._get_port_position(port_info["position"])
            painter.drawEllipse(position, self._port_radius, self._port_radius)
    
    def _get_port_position(self, position_type: str) -> QPointF:
        """获取端口位置"""
        if position_type == self.PORT_TOP:
            return QPointF(self._width / 2, 0)
        elif position_type == self.PORT_RIGHT:
            return QPointF(self._width, self._height / 2)
        elif position_type == self.PORT_BOTTOM:
            return QPointF(self._width / 2, self._height)
        elif position_type == self.PORT_LEFT:
            return QPointF(0, self._height / 2)
        else:
            return QPointF(0, 0)
    
    def add_input_port(self, port_id: str, name: str, position: str):
        """添加输入端口"""
        self._input_ports[port_id] = {
            "name": name,
            "position": position,
            "connected": False
        }
        self.update()
    
    def add_output_port(self, port_id: str, name: str, position: str):
        """添加输出端口"""
        self._output_ports[port_id] = {
            "name": name,
            "position": position,
            "connected": False
        }
        self.update()
    
    def set_port_connected(self, port_id: str, is_input: bool, connected: bool):
        """设置端口连接状态"""
        port_dict = self._input_ports if is_input else self._output_ports
        if port_id in port_dict:
            port_dict[port_id]["connected"] = connected
            self.update()
    
    def get_port_position(self, port_id: str, is_input: bool) -> QPointF:
        """获取端口的场景坐标"""
        port_dict = self._input_ports if is_input else self._output_ports
        if port_id in port_dict:
            port_pos = self._get_port_position(port_dict[port_id]["position"])
            return self.mapToScene(port_pos)
        return QPointF(0, 0)
    
    def get_port_at_pos(self, pos: QPointF) -> Tuple[Optional[str], bool]:
        """
        获取指定位置的端口
        
        Args:
            pos: 场景坐标位置
            
        Returns:
            (port_id, is_input) 端口ID和是否为输入端口的元组，如果没有端口则为(None, False)
        """
        # 转换为节点坐标
        local_pos = self.mapFromScene(pos)
        
        # 检查输入端口
        for port_id, port_info in self._input_ports.items():
            port_pos = self._get_port_position(port_info["position"])
            if (local_pos - port_pos).manhattanLength() <= self._port_radius * 2:
                return port_id, True
        
        # 检查输出端口
        for port_id, port_info in self._output_ports.items():
            port_pos = self._get_port_position(port_info["position"])
            if (local_pos - port_pos).manhattanLength() <= self._port_radius * 2:
                return port_id, False
        
        return None, False
    
    def get_id(self) -> str:
        """获取节点ID"""
        return self._id
    
    def get_title(self) -> str:
        """获取节点标题"""
        return self._title
    
    def set_title(self, title: str):
        """设置节点标题"""
        self._title = title
        self.update()
    
    def get_type(self) -> str:
        """获取节点类型"""
        return self._type
    
    def get_data(self) -> Dict[str, Any]:
        """获取节点数据"""
        return self._data.copy()
    
    def set_data(self, data: Dict[str, Any]):
        """设置节点数据"""
        self._data = data.copy()
    
    def itemChange(self, change, value):
        """处理项更改事件"""
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            # 发射节点移动信号
            self.node_moved.emit(self._id, self.pos())
        
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self._selected = bool(value)
            if self._selected:
                self.node_selected.emit(self._id)
            self.update()
        
        return super().itemChange(change, value)
    
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        """处理双击事件"""
        self.node_double_clicked.emit(self._id)
        super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        """处理右键菜单事件"""
        self.node_context_menu.emit(self._id, event.screenPos())
        
    def hoverEnterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True
        self.setCursor(Qt.OpenHandCursor)
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self._dragging:
            self._dragging = False
            self.setCursor(Qt.OpenHandCursor if self._hovered else Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def to_dict(self) -> Dict[str, Any]:
        """将节点转换为字典格式"""
        return {
            "id": self._id,
            "title": self._title,
            "type": self._type,
            "position": {"x": self.pos().x(), "y": self.pos().y()},
            "data": self._data,
            "input_ports": self._input_ports,
            "output_ports": self._output_ports
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowGraphNode':
        """从字典创建节点"""
        node = cls(
            node_id=data["id"],
            title=data["title"],
            node_type=data["type"]
        )
        
        # 设置位置
        pos = data.get("position", {"x": 0, "y": 0})
        node.setPos(QPointF(pos["x"], pos["y"]))
        
        # 设置数据
        node.set_data(data.get("data", {}))
        
        # 清除并重新添加端口
        node._input_ports.clear()
        node._output_ports.clear()
        
        # 添加输入端口
        for port_id, port_info in data.get("input_ports", {}).items():
            node.add_input_port(port_id, port_info["name"], port_info["position"])
            node.set_port_connected(port_id, True, port_info.get("connected", False))
        
        # 添加输出端口
        for port_id, port_info in data.get("output_ports", {}).items():
            node.add_output_port(port_id, port_info["name"], port_info["position"])
            node.set_port_connected(port_id, False, port_info.get("connected", False))
        
        return node 