#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程图视图组件
用于显示和交互流程图场景
"""

from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QInputDialog, QFileDialog,
    QMenu, QAction, QMessageBox, QRubberBand, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QRect, pyqtSignal, QSettings
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QWheelEvent, QKeyEvent

from typing import Dict, Any, List, Optional, Tuple, Set
import json
import os

from .flow_graph_scene import FlowGraphScene
from .flow_graph_node import FlowGraphNode
from .flow_graph_edge import FlowGraphEdge


class FlowGraphView(QGraphicsView):
    """流程图视图"""
    
    # 信号
    view_scaled = pyqtSignal(float)  # scale_factor
    view_scrolled = pyqtSignal(int, int)  # x, y
    node_selected = pyqtSignal(str)  # node_id
    node_double_clicked = pyqtSignal(str)  # node_id
    graph_changed = pyqtSignal()  # 图形变化信号
    
    def __init__(self, parent=None):
        """
        初始化流程图视图
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 创建场景
        self._graph_scene = FlowGraphScene(self)
        self.setScene(self._graph_scene)
        
        # 连接信号
        self._graph_scene.node_selected.connect(self.node_selected)
        self._graph_scene.node_double_clicked.connect(self.node_double_clicked)
        self._graph_scene.graph_changed.connect(self.graph_changed)
        
        # 视图设置
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 缩放设置
        self._zoom_factor = 1.0
        self._zoom_in_factor = 1.25
        self._zoom_out_factor = 0.8
        self._min_zoom = 0.1
        self._max_zoom = 5.0
        
        # 平移设置
        self._last_pan_point = None
        self._is_panning = False
        
        # 选择矩形
        self._selection_rect = None
        
        # 初始化缩放
        self.resetTransform()
        self.setup_actions()
    
    def setup_actions(self):
        """设置快捷键和操作"""
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
    
    def contextMenuEvent(self, event):
        """处理右键菜单事件"""
        # 如果有选中项，则不显示视图菜单
        if self.scene().selectedItems():
            super().contextMenuEvent(event)
            return
        
        menu = QMenu(self)
        
        # 添加常用操作
        add_node_menu = QMenu("添加节点", menu)
        
        add_normal_action = QAction("普通步骤", add_node_menu)
        add_normal_action.triggered.connect(self._add_normal_node)
        
        add_condition_action = QAction("条件判断", add_node_menu)
        add_condition_action.triggered.connect(self._add_condition_node)
        
        add_loop_action = QAction("循环", add_node_menu)
        add_loop_action.triggered.connect(self._add_loop_node)
        
        add_start_action = QAction("开始", add_node_menu)
        add_start_action.triggered.connect(self._add_start_node)
        
        add_end_action = QAction("结束", add_node_menu)
        add_end_action.triggered.connect(self._add_end_node)
        
        add_node_menu.addAction(add_normal_action)
        add_node_menu.addAction(add_condition_action)
        add_node_menu.addAction(add_loop_action)
        add_node_menu.addAction(add_start_action)
        add_node_menu.addAction(add_end_action)
        
        # 视图操作
        fit_action = QAction("适应窗口", menu)
        fit_action.triggered.connect(self.fit_all)
        
        reset_zoom_action = QAction("重置缩放", menu)
        reset_zoom_action.triggered.connect(self.reset_zoom)
        
        # 文件操作
        save_action = QAction("保存流程图...", menu)
        save_action.triggered.connect(self._save_graph)
        
        load_action = QAction("加载流程图...", menu)
        load_action.triggered.connect(self._load_graph)
        
        # 添加到菜单
        menu.addMenu(add_node_menu)
        menu.addSeparator()
        menu.addAction(fit_action)
        menu.addAction(reset_zoom_action)
        menu.addSeparator()
        menu.addAction(save_action)
        menu.addAction(load_action)
        
        menu.exec_(event.globalPos())
    
    def wheelEvent(self, event: QWheelEvent):
        """处理鼠标滚轮事件（用于缩放）"""
        # 获取滚轮增量
        delta = event.angleDelta().y()
        
        # 根据滚轮方向设置缩放因子
        if delta > 0:
            zoom_factor = self._zoom_in_factor
        else:
            zoom_factor = self._zoom_out_factor
        
        # 应用缩放
        self.scale_view(zoom_factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标按下事件"""
        # 中键拖动开始
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        
        # 使用按下Ctrl或Alt键加左键拖动也进行平移
        if event.button() == Qt.LeftButton and (event.modifiers() & (Qt.ControlModifier | Qt.AltModifier)):
            self._is_panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """处理鼠标移动事件"""
        # 处理平移
        if self._is_panning and self._last_pan_point:
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            
            # 更新滚动条位置
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            
            # 发送滚动信号
            self.view_scrolled.emit(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
            
            event.accept()
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """处理鼠标释放事件"""
        # 结束平移
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and self._is_panning):
            self._is_panning = False
            self._last_pan_point = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        # 删除键删除选中的项
        if event.key() == Qt.Key_Delete:
            self._delete_selected_items()
            event.accept()
            return
        
        # 空格键适应所有内容
        if event.key() == Qt.Key_Space:
            self.fit_all()
            event.accept()
            return
        
        # Ctrl+Plus 放大
        if event.key() == Qt.Key_Plus and event.modifiers() & Qt.ControlModifier:
            self.scale_view(self._zoom_in_factor)
            event.accept()
            return
        
        # Ctrl+Minus 缩小
        if event.key() == Qt.Key_Minus and event.modifiers() & Qt.ControlModifier:
            self.scale_view(self._zoom_out_factor)
            event.accept()
            return
        
        # Ctrl+0 重置缩放
        if event.key() == Qt.Key_0 and event.modifiers() & Qt.ControlModifier:
            self.reset_zoom()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def scale_view(self, factor: float):
        """缩放视图"""
        # 计算新的缩放因子
        new_zoom = self._zoom_factor * factor
        
        # 检查是否超出限制
        if new_zoom < self._min_zoom or new_zoom > self._max_zoom:
            return
        
        # 应用缩放
        self._zoom_factor = new_zoom
        self.setTransform(self.transform().scale(factor, factor))
        
        # 发送缩放信号
        self.view_scaled.emit(self._zoom_factor)
    
    def reset_zoom(self):
        """重置缩放"""
        self._zoom_factor = 1.0
        self.resetTransform()
        self.view_scaled.emit(self._zoom_factor)
    
    def fit_all(self):
        """适应所有内容"""
        # 获取场景中所有项的包围矩形
        rect = self.scene().itemsBoundingRect()
        
        # 添加一些边距
        rect.adjust(-50, -50, 50, 50)
        
        # 适应矩形
        self.fitInView(rect, Qt.KeepAspectRatio)
        
        # 更新缩放因子
        self._zoom_factor = self.transform().m11()  # 水平缩放因子
        self.view_scaled.emit(self._zoom_factor)
    
    def _delete_selected_items(self):
        """删除选中的项"""
        selected_items = self.scene().selectedItems()
        if not selected_items:
            return
        
        # 先删除选中的边
        for item in selected_items:
            if isinstance(item, FlowGraphEdge):
                self._graph_scene.delete_edge(item.get_id())
        
        # 再删除选中的节点
        for item in selected_items:
            if isinstance(item, FlowGraphNode):
                self._graph_scene.delete_node(item.get_id())
    
    def _add_normal_node(self):
        """添加普通节点"""
        pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
        self._graph_scene.add_node(FlowGraphNode.TYPE_NORMAL, pos)
    
    def _add_condition_node(self):
        """添加条件节点"""
        pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
        self._graph_scene.add_node(FlowGraphNode.TYPE_CONDITION, pos)
    
    def _add_loop_node(self):
        """添加循环节点"""
        pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
        self._graph_scene.add_node(FlowGraphNode.TYPE_LOOP, pos)
    
    def _add_start_node(self):
        """添加开始节点"""
        pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
        self._graph_scene.add_node(FlowGraphNode.TYPE_START, pos)
    
    def _add_end_node(self):
        """添加结束节点"""
        pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
        self._graph_scene.add_node(FlowGraphNode.TYPE_END, pos)
    
    def _save_graph(self):
        """保存流程图到文件"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存流程图", "", "流程图文件 (*.flow);;所有文件 (*)")
        if not file_path:
            return
        
        # 添加扩展名
        if not file_path.lower().endswith('.flow'):
            file_path += '.flow'
        
        try:
            # 获取图形数据
            graph_data = self._graph_scene.to_dict()
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "保存成功", f"流程图已保存到：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存流程图时出错：{str(e)}")
    
    def _load_graph(self):
        """从文件加载流程图"""
        file_path, _ = QFileDialog.getOpenFileName(self, "加载流程图", "", "流程图文件 (*.flow);;所有文件 (*)")
        if not file_path:
            return
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # 加载图形数据
            self._graph_scene.from_dict(graph_data)
            
            # 适应视图
            self.fit_all()
            
            QMessageBox.information(self, "加载成功", f"流程图已从{file_path}加载")
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载流程图时出错：{str(e)}")
    
    def get_scene(self) -> FlowGraphScene:
        """获取流程图场景"""
        return self._graph_scene
    
    def clear_graph(self):
        """清空流程图"""
        self._graph_scene.clear_graph()
    
    def add_default_nodes(self):
        """添加默认节点（开始和结束）"""
        # 添加开始节点
        start_node_id = self._graph_scene.add_node(
            node_type=FlowGraphNode.TYPE_START,
            pos=QPointF(100, 100),
            title="开始"
        )
        
        # 添加结束节点
        end_node_id = self._graph_scene.add_node(
            node_type=FlowGraphNode.TYPE_END,
            pos=QPointF(100, 300),
            title="结束"
        )
        
        # 连接节点
        self._graph_scene.add_edge(start_node_id, "out", end_node_id, "in")
        
        # 适应视图
        self.fit_all()
    
    def save_view_state(self, settings: QSettings, group: str = "FlowGraphView"):
        """保存视图状态"""
        settings.beginGroup(group)
        
        # 保存缩放
        settings.setValue("zoom_factor", self._zoom_factor)
        
        # 保存视图位置
        settings.setValue("scroll_x", self.horizontalScrollBar().value())
        settings.setValue("scroll_y", self.verticalScrollBar().value())
        
        settings.endGroup()
    
    def restore_view_state(self, settings: QSettings, group: str = "FlowGraphView"):
        """恢复视图状态"""
        settings.beginGroup(group)
        
        # 恢复缩放
        zoom = settings.value("zoom_factor", 1.0, type=float)
        if zoom != 1.0:
            # 重置后再设置为保存的缩放比例
            self.resetTransform()
            self.scale(zoom, zoom)
            self._zoom_factor = zoom
        
        # 恢复滚动位置
        scroll_x = settings.value("scroll_x", 0, type=int)
        scroll_y = settings.value("scroll_y", 0, type=int)
        
        self.horizontalScrollBar().setValue(scroll_x)
        self.verticalScrollBar().setValue(scroll_y)
        
        settings.endGroup() 