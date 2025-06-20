from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QSize


class HomePage(QWidget):
    """主页面，显示四个功能方块"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # 标题
        title_label = QLabel("DeepSeek 多功能小应用")
        title_label.setFont(QFont("Microsoft YaHei", 32, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 30px;")
        layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("Created by Iking")
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #555; margin-bottom: 50px;")
        layout.addWidget(subtitle_label)

        # 功能方块网格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(40)
        grid_layout.setContentsMargins(100, 0, 100, 0)

        # 创建四个功能方块
        self.chat_btn = self.create_function_button("聊天", "#4A90E2")
        self.novel_btn = self.create_function_button("写小说", "#34A853")
        self.interactive_btn = self.create_function_button("交互小说", "#FBBC05")
        self.settings_btn = self.create_function_button("设置", "#EA4335")

        # 添加到网格
        grid_layout.addWidget(self.chat_btn, 0, 0)
        grid_layout.addWidget(self.novel_btn, 0, 1)
        grid_layout.addWidget(self.interactive_btn, 1, 0)
        grid_layout.addWidget(self.settings_btn, 1, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

        # 连接信号
        self.chat_btn.clicked.connect(lambda: self.switch_to_page(1))
        self.novel_btn.clicked.connect(lambda: self.switch_to_page(2))
        self.interactive_btn.clicked.connect(lambda: self.switch_to_page(3))
        self.settings_btn.clicked.connect(lambda: self.switch_to_page(4))

    def create_function_button(self, text, color):
        """创建功能方块按钮"""
        button = QPushButton(text)
        button.setMinimumSize(400, 600)  # 设置最小大小
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 设置样式
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 15px;
                font-size: 16pt;
                font-weight: bold;
                font-family: Microsoft YaHei;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """
        )

        return button

    def darken_color(self, hex_color, factor=0.8):
        """使颜色变暗"""
        color = QColor(hex_color)
        return color.darker(int(100 / factor)).name()

    def switch_to_page(self, index):
        """切换到指定页面"""
        if self.main_window:
            self.main_window.switch_page(index)
