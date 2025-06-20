from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QStatusBar,
    QGridLayout,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette
from config_manager import get_config, update_config
from .home_page import HomePage
from .chat_page import ChatPage
from .novel_page import NovelPage
from .interactive_novel_page import InteractiveNovelPage
from .settings_page import SettingsPage
from .styles import *


class MainWindow(QMainWindow):
    """主窗口，包含主页和功能页面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepSeek 多功能小应用")
        self.setGeometry(100, 100, 1920, 1600)  # 设置与原始聊天窗口相同的大小

        # 主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 页面堆栈
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # 创建全局状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Arial", 10))
        self.status_bar.setMinimumHeight(50)
        self.setStatusBar(self.status_bar)
        self.scroll_button = None

        # 初始化状态栏控件
        self.init_status_bar()

        # 创建页面
        self.home_page = HomePage(self)
        self.chat_page = ChatPage(self)
        self.novel_page = NovelPage(self)
        self.interactive_page = InteractiveNovelPage(self)
        self.settings_page = SettingsPage(self)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.chat_page)
        self.stacked_widget.addWidget(self.novel_page)
        self.stacked_widget.addWidget(self.interactive_page)
        self.stacked_widget.addWidget(self.settings_page)

        # 默认显示主页
        self.switch_page(0)

    def init_status_bar(self):
        """初始化状态栏控件，保持原始字体样式"""
        # 创建左侧容器
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # 添加状态消息标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(
            "color: #555; min-width: 100px; font-family: Microsoft YaHei !important;"
        )
        left_layout.addWidget(self.status_label)

        # 添加分隔符
        separator = QLabel("|")
        separator.setStyleSheet("color: #999; margin: 0 5px;")
        left_layout.addWidget(separator)

        # 添加新按钮
        self.btn_r1 = QPushButton("深度思考(R1)")
        self.btn_r1.setCheckable(True)
        self.btn_r1.setChecked(get_config("enable_r1"))
        self.btn_r1.setStyleSheet(self.get_button_style(get_config("enable_r1")))
        self.btn_r1.setMaximumWidth(180)
        self.btn_r1.clicked.connect(self.toggle_r1)
        left_layout.addWidget(self.btn_r1)

        self.btn_tavily = QPushButton("Tavily")
        self.btn_tavily.setCheckable(True)
        self.btn_tavily.setChecked(get_config("enable_tavily"))
        self.btn_tavily.setStyleSheet(
            self.get_button_style(get_config("enable_tavily"))
        )
        self.btn_tavily.setMaximumWidth(90)
        self.btn_tavily.setFont(QFont("Microsoft YaHei", 10))  # 明确设置字体
        self.btn_tavily.clicked.connect(self.toggle_tavily)
        left_layout.addWidget(self.btn_tavily)

        # 添加到状态栏左侧
        self.status_bar.addPermanentWidget(left_container, 1)

        # 添加滚动到底部按钮到右侧
        self.scroll_button = QPushButton("↓ 滚动到底")
        self.scroll_button.setFixedHeight(45)
        self.scroll_button.setFont(QFont("Microsoft YaHei", 10))  # 明确设置字体
        self.scroll_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                font-family: Microsoft YaHei !important;
                font-size: 10pt !important;
            }
            QPushButton:hover {
                background-color: #3A7BC8;
            }
            """
        )
        self.status_bar.addPermanentWidget(self.scroll_button)

        # 强制设置状态栏字体
        self.status_bar.setFont(QFont("Microsoft YaHei", 10))

        # # 在init_status_bar方法末尾添加调试信息
        # print(f"状态栏字体: {self.status_bar.font().family()}")
        # print(f"滚动按钮字体: {self.scroll_button.font().family()}")
        # print(f"R1按钮字体: {self.btn_r1.font().family()}")
        # print(f"Tavily按钮字体: {self.btn_tavily.font().family()}")

    def get_button_style(self, enabled):
        """根据状态返回按钮样式"""
        if enabled:
            return """
                QPushButton {
                    background-color: #DBEAFE;
                    color: #4D6BFE;
                    border: 1px solid #007AFF;
                    padding: 4px 8px;
                    border-radius: 4px;
                    min-width: 0;
                    font-family: Microsoft YaHei !important;
                    font-size: 10pt !important;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: white;
                    color: #4C4C4C;
                    border: 1px solid #000000;
                    padding: 4px 8px;
                    border-radius: 4px;
                    min-width: 0;
                    font-family: Microsoft YaHei !important;
                    font-size: 10pt !important;
                }
            """

    def toggle_r1(self):
        """切换 R1 深度思考状态"""
        new_config = get_config()
        new_config["enable_r1"] = not new_config["enable_r1"]
        update_config(new_config)
        self.btn_r1.setChecked(new_config["enable_r1"])
        self.btn_r1.setStyleSheet(self.get_button_style(new_config["enable_r1"]))

    def toggle_tavily(self):
        """切换 Tavily 搜索状态"""
        new_config = get_config()
        new_config["enable_tavily"] = not new_config["enable_tavily"]
        update_config(new_config)
        self.btn_tavily.setChecked(new_config["enable_tavily"])
        self.btn_tavily.setStyleSheet(
            self.get_button_style(new_config["enable_tavily"])
        )

    def switch_page(self, index):
        """切换功能页面"""
        self.stacked_widget.setCurrentIndex(index)

    def set_status(self, message):
        """设置状态栏消息"""
        self.status_label.setText(message)

    def get_scroll_button(self):
        """获取滚动到底部按钮"""
        return self.scroll_button

    def closeEvent(self, event):
        """窗口关闭时清理所有页面资源"""
        # 清理聊天页面资源
        self.chat_page.cleanup()

        super().closeEvent(event)
