#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程图连线组件
实现节点之间的连接线
"""

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QMenu, QAction
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QPainterPath, QColor, QPolygonF, QPainterPathStroker

from typing import Dict, Any, List, Optional, Tuple

class FlowGraphEdge(QGraphicsPathItem):
    """流程图连线"""
    
    # 连线类型
    TYPE_BEZIER = "bezier"  # 贝塞尔曲线
    TYPE_STRAIGHT = "straight"  # 直线
    TYPE_STEPPED = "stepped"  # 直角折线
    
    def __init__(self, edge_id: str, source_node: str, source_port: str, 
                 target_node: str, target_port: str, edge_type: str = TYPE_BEZIER, parent=None):
        """
        初始化连线
        
        Args:
            edge_id: 连线唯一标识
            source_node: 源节点ID
            source_port: 源节点端口ID
            target_node: 目标节点ID
            target_port: 目标节点端口ID
            edge_type: 连线类型
            parent: 父项
        """
        super().__init__(parent)
        
        self._id = edge_id
        self._source_node = source_node
        self._source_port = source_port
        self._target_node = target_node
        self._target_port = target_port
        self._type = edge_type
        
        # 端点坐标
        self._source_point = QPointF(0, 0)
        self._target_point = QPointF(100, 100)
        
        # 外观设置
        self._color = QColor(80, 80, 80)
        self._width = 2.0
        self._selected_color = QColor(0, 120, 215)
        self._selected_width = 3.0
        self._arrow_size = 10.0
        
        # 设置连线可选
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # 设置Z值，确保连线在节点下方
        self.setZValue(-1.0)
    
    def set_source_point(self, point: QPointF):
        """设置源点坐标"""
        self._source_point = point
        self.update_path()
    
    def set_target_point(self, point: QPointF):
        """设置目标点坐标"""
        self._target_point = point
        self.update_path()
    
    def update_path(self):
        """更新连线路径"""
        path = QPainterPath()
        
        # 如果点重合，不绘制
        if (self._source_point - self._target_point).manhattanLength() < 1.0:
            self.setPath(path)
            return
        
        # 计算连线路径
        if self._type == self.TYPE_STRAIGHT:
            # 直线
            path.moveTo(self._source_point)
            path.lineTo(self._target_point)
        elif self._type == self.TYPE_STEPPED:
            # 直角折线
            path.moveTo(self._source_point)
            
            # 计算中间点
            mid_x = (self._source_point.x() + self._target_point.x()) / 2.0
            
            path.lineTo(mid_x, self._source_point.y())
            path.lineTo(mid_x, self._target_point.y())
            path.lineTo(self._target_point)
        else:
            # 贝塞尔曲线
            path.moveTo(self._source_point)
            
            # 计算控制点
            dx = self._target_point.x() - self._source_point.x()
            dy = self._target_point.y() - self._source_point.y()
            
            ctrl1 = QPointF(self._source_point.x() + dx * 0.5, self._source_point.y())
            ctrl2 = QPointF(self._target_point.x() - dx * 0.5, self._target_point.y())
            
            path.cubicTo(ctrl1, ctrl2, self._target_point)
        
        # 计算箭头
        self._add_arrow(path)
        
        # 设置路径
        self.setPath(path)
    
    def _add_arrow(self, path: QPainterPath):
        """添加箭头"""
        # 获取线段结束前的位置作为箭头起点
        # 使用路径的百分比来估算
        delta = 0.02  # 2%的距离偏移
        t = 1.0 - delta
        
        # 对于不同类型的曲线，使用不同的计算方法
        if self._type == self.TYPE_STRAIGHT:
            # 直线，简单计算
            direction = self._target_point - self._source_point
            length = direction.manhattanLength()
            if length > 0:
                direction /= length
                arrow_base = self._target_point - direction * self._arrow_size
            else:
                arrow_base = self._target_point
        elif self._type == self.TYPE_STEPPED:
            # 直角折线，取最后一段直线
            mid_x = (self._source_point.x() + self._target_point.x()) / 2.0
            if abs(mid_x - self._target_point.x()) > 1.0:
                # 箭头在水平线上
                arrow_base = QPointF(self._target_point.x() - self._arrow_size, self._target_point.y())
            else:
                # 箭头在垂直线上
                arrow_base = QPointF(self._target_point.x(), self._target_point.y() - self._arrow_size)
        else:
            # 贝塞尔曲线，近似计算
            # 为简化，使用直线逼近
            # 修复：QPointF没有normalized方法，手动实现向量归一化
            direction = self._target_point - self._source_point
            length = direction.manhattanLength()
            if length > 0:
                normalized_direction = QPointF(direction.x() / length, direction.y() / length)
                arrow_base = self._target_point - normalized_direction * self._arrow_size
            else:
                arrow_base = self._target_point
        
        # 计算箭头的两个侧点
        line = self._target_point - arrow_base
        line_length = line.manhattanLength()
        if line_length > 0:
            line = QPointF(line.x() * self._arrow_size / line_length, 
                          line.y() * self._arrow_size / line_length)
        else:
            line = QPointF(0, self._arrow_size)
        
        normal = QPointF(-line.y(), line.x()) * 0.35
        
        arrow_p1 = self._target_point - line + normal
        arrow_p2 = self._target_point - line - normal
        
        # 添加箭头路径
        arrow_path = QPainterPath()
        arrow_path.moveTo(self._target_point)
        arrow_path.lineTo(arrow_p1)
        arrow_path.lineTo(arrow_p2)
        arrow_path.lineTo(self._target_point)
        
        # 合并路径
        path.addPath(arrow_path)
    
    def paint(self, painter, option, widget=None):
        """绘制连线"""
        # 设置连线样式
        if self.isSelected():
            pen = QPen(self._selected_color, self._selected_width)
        else:
            pen = QPen(self._color, self._width)
        
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        
        # 绘制路径
        painter.drawPath(self.path())
    
    def boundingRect(self) -> QRectF:
        """获取连线的包围矩形"""
        return self.path().boundingRect().adjusted(-5, -5, 5, 5)
    
    def shape(self) -> QPainterPath:
        """获取用于碰撞检测的形状"""
        # 创建一个较粗的路径用于碰撞检测
        path = QPainterPath(self.path())
        stroker = QPainterPathStroker()
        stroker.setWidth(self._width + 8.0)  # 加宽以便更容易选中
        return stroker.createStroke(path)
    
    def contextMenuEvent(self, event):
        """处理右键菜单事件"""
        menu = QMenu()
        
        # 添加菜单项
        delete_action = QAction("删除连线", menu)
        delete_action.triggered.connect(self._on_delete)
        
        change_type_menu = QMenu("更改连线类型", menu)
        
        bezier_action = QAction("贝塞尔曲线", change_type_menu)
        bezier_action.triggered.connect(lambda: self._change_type(self.TYPE_BEZIER))
        
        straight_action = QAction("直线", change_type_menu)
        straight_action.triggered.connect(lambda: self._change_type(self.TYPE_STRAIGHT))
        
        stepped_action = QAction("折线", change_type_menu)
        stepped_action.triggered.connect(lambda: self._change_type(self.TYPE_STEPPED))
        
        change_type_menu.addAction(bezier_action)
        change_type_menu.addAction(straight_action)
        change_type_menu.addAction(stepped_action)
        
        menu.addAction(delete_action)
        menu.addMenu(change_type_menu)
        
        menu.exec_(event.screenPos())
    
    def _on_delete(self):
        """删除连线"""
        if self.scene():
            self.scene().removeItem(self)
    
    def _change_type(self, edge_type: str):
        """更改连线类型"""
        self._type = edge_type
        self.update_path()
    
    def hoverEnterEvent(self, event):
        """鼠标进入事件"""
        # 加粗连线
        self.setPen(QPen(self._color, self._width + 1.0))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标离开事件"""
        # 恢复连线粗细
        self.setPen(QPen(self._color, self._width))
        super().hoverLeaveEvent(event)
    
    def get_id(self) -> str:
        """获取连线ID"""
        return self._id
    
    def get_source(self) -> Tuple[str, str]:
        """获取源节点和端口"""
        return self._source_node, self._source_port
    
    def get_target(self) -> Tuple[str, str]:
        """获取目标节点和端口"""
        return self._target_node, self._target_port
    
    def to_dict(self) -> Dict[str, Any]:
        """将连线转换为字典格式"""
        return {
            "id": self._id,
            "source_node": self._source_node,
            "source_port": self._source_port,
            "target_node": self._target_node,
            "target_port": self._target_port,
            "type": self._type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowGraphEdge':
        """从字典创建连线"""
        return cls(
            edge_id=data["id"],
            source_node=data["source_node"],
            source_port=data["source_port"],
            target_node=data["target_node"],
            target_port=data["target_port"],
            edge_type=data.get("type", cls.TYPE_BEZIER)
        ) 