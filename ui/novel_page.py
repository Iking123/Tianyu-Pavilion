from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


class NovelPage(QWidget):
    """写小说功能页面"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F0F2F5; padding: 10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 返回按钮
        self.back_button = QPushButton("← 返回主页")
        self.back_button.setIcon(QIcon.fromTheme("go-previous"))
        self.back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )
        self.back_button.clicked.connect(self.go_back)

        # 页面标题
        title_label = QLabel("写小说功能")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        toolbar_layout.addWidget(self.back_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_label)
        toolbar_layout.addStretch()

        layout.addWidget(toolbar)

        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(50, 50, 50, 50)

        # 添加内容
        content_label = QLabel("小说创作功能正在开发中...")
        content_label.setFont(QFont("Arial", 24))
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setStyleSheet("color: #555;")
        content_layout.addWidget(content_label)

        layout.addWidget(content_widget)

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)
