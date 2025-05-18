from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime

class LogDisplayWidget(QTextEdit):
    """
    A widget to display log messages and execution status.
    """
    # 信号：当添加日志消息时发射
    log_message_added = pyqtSignal(str, str)  # 消息内容, 级别
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("日志和状态信息将显示在这里...")
        self.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, Menlo, monospace;
                font-size: 9pt;
            }
        """)
    
    def add_message(self, message, level="INFO"):
        """
        Add a message to the log with timestamp and level.
        
        Args:
            message: The message text
            level: Message level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Define colors for different message levels
        color = "black"
        if level == "ERROR":
            color = "#FF0000"  # Red
        elif level == "WARNING":
            color = "#FF8C00"  # Orange
        elif level == "SUCCESS":
            color = "#008000"  # Green
        
        # Format and append the message
        formatted_message = f"<span style='color:gray;'>[{timestamp}]</span> " \
                          + f"<span style='color:{color};font-weight:bold;'>[{level}]</span> " \
                          + f"<span style='color:{color};'>{message}</span>"
        
        self.append(formatted_message)
        
        # 发射信号
        self.log_message_added.emit(message, level)
        
        # Auto-scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def add_error(self, message):
        """Add an error message."""
        self.add_message(message, level="ERROR")
    
    def add_warning(self, message):
        """Add a warning message."""
        self.add_message(message, level="WARNING")
    
    def add_success(self, message):
        """Add a success message."""
        self.add_message(message, level="SUCCESS")
    
    def clear(self):
        """Clear all log messages."""
        super().clear()
        self.add_message("日志已清空", level="INFO")


if __name__ == "__main__":
    """Test the LogDisplayWidget directly."""
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
    
    app = QApplication(sys.argv)
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    
    log_widget = LogDisplayWidget()
    layout.addWidget(log_widget)
    
    # Add test buttons
    btn_info = QPushButton("添加信息")
    btn_warning = QPushButton("添加警告")
    btn_error = QPushButton("添加错误")
    btn_success = QPushButton("添加成功")
    btn_clear = QPushButton("清空日志")
    
    btn_info.clicked.connect(lambda: log_widget.add_message("这是一条普通信息"))
    btn_warning.clicked.connect(lambda: log_widget.add_warning("这是一条警告信息"))
    btn_error.clicked.connect(lambda: log_widget.add_error("这是一条错误信息"))
    btn_success.clicked.connect(lambda: log_widget.add_success("这是一条成功信息"))
    btn_clear.clicked.connect(log_widget.clear)
    
    layout.addWidget(btn_info)
    layout.addWidget(btn_warning)
    layout.addWidget(btn_error)
    layout.addWidget(btn_success)
    layout.addWidget(btn_clear)
    
    main_widget.setWindowTitle("日志显示控件测试")
    main_widget.resize(600, 400)
    main_widget.show()
    
    # Add initial messages
    log_widget.add_message("日志控件已初始化")
    log_widget.add_warning("这是一个测试警告")
    log_widget.add_error("这是一个测试错误")
    log_widget.add_success("这是一个测试成功消息")
    
    sys.exit(app.exec_())
