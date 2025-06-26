import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QPoint
from funcs import resource_path


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
        self.game_btn = self.create_function_button("小游戏", "#34A853")
        self.interactive_btn = self.create_function_button("交互小说", "#FBBC05")
        self.settings_btn = self.create_function_button("设置", "#EA4335")

        # 添加到网格
        grid_layout.addWidget(self.chat_btn, 0, 0)
        grid_layout.addWidget(self.game_btn, 0, 1)
        grid_layout.addWidget(self.interactive_btn, 1, 0)
        grid_layout.addWidget(self.settings_btn, 1, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

        # 连接信号
        self.chat_btn.clicked.connect(lambda: self.switch_to_page(1))
        self.game_btn.clicked.connect(lambda: self.switch_to_page(2))
        self.interactive_btn.clicked.connect(lambda: self.switch_to_page(3))
        self.settings_btn.clicked.connect(lambda: self.switch_to_page(4))

    def create_function_button(self, text, color):
        """创建功能方块按钮"""
        button = QPushButton()
        button.setMinimumSize(400, 600)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 设置图片路径（根据按钮文字映射）
        img_map = {
            "聊天": "chat_bg.png",
            "小游戏": "game_bg.png",
            "交互小说": "interactive_bg.png",
            "设置": "settings_bg.png",
        }
        img_path = resource_path(os.path.join("resources", "images", img_map[text]))

        # 使用绝对路径并转换路径分隔符
        abs_path = os.path.abspath(img_path).replace("\\", "/")

        # 创建渐变色背景
        base_color = QColor(color)
        darker_color = base_color.darker(120)  # 变暗20%
        lighter_color = base_color.lighter(120)  # 变亮20%

        # 设置样式表（添加背景颜色和图片）
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {lighter_color.name()}, stop:1 {darker_color.name()});
                border-radius: 15px;
                color: white;
                font-size: 16pt;
                font-weight: bold;
                font-family: Microsoft YaHei;
                border: 2px solid #FFF;
            }}
            QPushButton:hover {{
                border: 3px solid #FFFF00;
            }}
            QPushButton:pressed {{
                background-color: {darker_color.name()};
            }}
        """
        )

        # 添加背景图片（使用QSS的border-image解决background-size警告）
        button.setStyleSheet(
            button.styleSheet()
            + f"""
            QPushButton {{
                border-image: url({abs_path}) 0 0 0 0 stretch stretch;
            }}
        """
        )

        return button

    def switch_to_page(self, index):
        """切换到指定页面"""
        if self.main_window:
            self.main_window.switch_page(index)
