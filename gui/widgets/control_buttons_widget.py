from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt

class ControlButtonsWidget(QWidget):
    """
    A widget containing control buttons for the flow execution.
    """
    # Define signals
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create buttons
        self.start_button = QPushButton("▶ 开始执行")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.stop_button = QPushButton("⏹ 停止执行")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.stop_button.setEnabled(False)  # Initially disabled
        
        # Add buttons to layout
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        
        # Connect signals
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        
    def _on_start_clicked(self):
        """
        Handle start button click - disable start button, enable stop button,
        and emit start_clicked signal.
        """
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_clicked.emit()
    
    def _on_stop_clicked(self):
        """
        Handle stop button click - disable stop button, enable start button,
        and emit stop_clicked signal.
        """
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.stop_clicked.emit()
    
    def reset_state(self):
        """
        Reset the control buttons to their initial state.
        """
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


if __name__ == "__main__":
    """Test the ControlButtonsWidget directly."""
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget
    
    app = QApplication(sys.argv)
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    
    status_label = QLabel("状态: 就绪")
    layout.addWidget(status_label)
    
    control_buttons = ControlButtonsWidget()
    layout.addWidget(control_buttons)
    
    def on_start():
        status_label.setText("状态: 正在执行...")
    
    def on_stop():
        status_label.setText("状态: 已停止")
        control_buttons.reset_state()
    
    control_buttons.start_clicked.connect(on_start)
    control_buttons.stop_clicked.connect(on_stop)
    
    main_widget.setWindowTitle("控制按钮测试")
    main_widget.resize(300, 100)
    main_widget.show()
    
    sys.exit(app.exec_())
