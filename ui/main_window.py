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
    QComboBox,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette
from core.config_manager import get_config, update_config
from .home_page import HomePage
from features.chat.chat_page import ChatPage
from features.game.game_page import GamePage
from features.interactive_novel.interactive_novel_page import InteractiveNovelPage
from features.creative_writing.creative_writing_page import CreativeWritingPage
from features.settings.settings_page import SettingsPage
from features.character.character_editor import CharacterEditor
from features.interactive_novel.fiction_page import InteractiveFictionPage
from .styles import *

# 具体页面导入
from features.game.idiom_solitaire_page import IdiomSolitairePage
from features.creative_writing.zero_point_page import ZeroPointPage


class MainWindow(QMainWindow):
    """主窗口，包含主页和功能页面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("天语阁")
        self.setGeometry(100, 80, 1720, 1720)

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

        # 只创建主页
        self.home_page = HomePage(self)
        self.stacked_widget.addWidget(self.home_page)

        # 其他页面设为None，需要时再创建
        self.chat_page = None
        self.game_page = None
        self.interactive_page = None
        self.creative_page = None
        self.settings_page = None
        self.character_editor = None  # 新增角色编辑器页面
        self.game_pages = {}
        self.writing_pages = {}

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

        # 添加模型选择下拉框
        self.model_combobox = QComboBox()
        self.model_combobox.addItems(
            [
                "DeepSeek-R1",
                "DeepSeek-V3",
                "Doubao-Seed-1.6-thinking",
                "Doubao-Seed-1.6",
            ]
        )
        self.model_combobox.setMaximumWidth(388)
        current_model = get_config("model")
        if current_model == "deepseek-reasoner":
            self.model_combobox.setCurrentText("DeepSeek-R1")
        elif current_model == "deepseek-chat":
            self.model_combobox.setCurrentText("DeepSeek-V3")
        elif current_model == "doubao-seed-1-6-thinking-250715":
            self.model_combobox.setCurrentText("Doubao-Seed-1.6-thinking")
        elif current_model == "doubao-seed-1-6-250615":
            self.model_combobox.setCurrentText("Doubao-Seed-1.6")
        self.model_combobox.currentIndexChanged.connect(self.change_model)
        left_layout.addWidget(self.model_combobox)

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

    def change_model(self, index):
        new_config = get_config()
        model_text = self.model_combobox.currentText()
        if model_text == "DeepSeek-R1":
            new_config["model"] = "deepseek-reasoner"
        elif model_text == "DeepSeek-V3":
            new_config["model"] = "deepseek-chat"
        elif model_text == "Doubao-Seed-1.6-thinking":
            new_config["model"] = "doubao-seed-1-6-thinking-250715"
        elif model_text == "Doubao-Seed-1.6":
            new_config["model"] = "doubao-seed-1-6-250615"
        update_config(new_config)
        self.update_status()

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
        """切换功能页面，按需创建页面"""
        if index == 0:  # 主页
            if not hasattr(self, "home_page") or not self.home_page:
                self.home_page = HomePage(self)
                self.stacked_widget.addWidget(self.home_page)
            self.stacked_widget.setCurrentWidget(self.home_page)
        elif index == 1:  # 聊天页面
            if not self.chat_page:
                self.chat_page = ChatPage(self)
                self.stacked_widget.addWidget(self.chat_page)
            self.stacked_widget.setCurrentWidget(self.chat_page)
        elif index == 2:  # 游戏列表
            if not self.game_page:
                self.game_page = GamePage(self)
                self.stacked_widget.addWidget(self.game_page)
            self.stacked_widget.setCurrentWidget(self.game_page)
        elif index == 3:  # 交互小说
            if not self.interactive_page:
                self.interactive_page = InteractiveNovelPage(self)
                self.stacked_widget.addWidget(self.interactive_page)
            self.stacked_widget.setCurrentWidget(self.interactive_page)
        elif index == 4:  # 创意写作
            if not self.creative_page:
                self.creative_page = CreativeWritingPage(self)
                self.stacked_widget.addWidget(self.creative_page)
            self.stacked_widget.setCurrentWidget(self.creative_page)
        elif index == 5:  # 设置页面
            if not self.settings_page:
                self.settings_page = SettingsPage(self)
                self.stacked_widget.addWidget(self.settings_page)
            self.stacked_widget.setCurrentWidget(self.settings_page)
        elif index == 6:  # 角色编辑器页面
            if not self.character_editor:
                self.character_editor = CharacterEditor(self)
                self.stacked_widget.addWidget(self.character_editor)
            self.stacked_widget.setCurrentWidget(self.character_editor)

    def set_status(self, message):
        """设置状态栏消息"""
        self.status_label.setText(message)

    def get_scroll_button(self):
        """获取滚动到底部按钮"""
        return self.scroll_button

    def update_status(self, message=None):
        """更新状态栏"""
        config = get_config()
        self.btn_tavily.setChecked(config["enable_tavily"])
        self.btn_tavily.setStyleSheet(self.get_button_style(config["enable_tavily"]))
        if message:
            if not isinstance(message, str):
                message = "就绪"
            self.set_status(message)

    def closeEvent(self, event):
        """窗口关闭时清理所有页面资源"""
        # 清理聊天页面资源
        if self.chat_page:
            self.chat_page.cleanup()

        super().closeEvent(event)

    def open_game_page(self, game_name):
        """打开指定的游戏页面"""
        if game_name not in self.game_pages:
            # 根据游戏名称创建对应的游戏页面
            if game_name == "成语接龙":
                self.game_pages[game_name] = IdiomSolitairePage(self)
                # 将新游戏页面添加到堆栈中
                self.stacked_widget.addWidget(self.game_pages[game_name])
            # 未来可以添加其他游戏页面
            # elif game_name == "数学挑战":
            #     self.game_pages[game_name] = MathChallengePage(self)
            #     self.stacked_widget.addWidget(self.game_pages[game_name])

        if game_name in self.game_pages:
            # 切换到游戏页面
            self.stacked_widget.setCurrentWidget(self.game_pages[game_name])

    def switch_to_game_list(self):
        """切换到游戏列表页面"""
        self.stacked_widget.setCurrentWidget(self.game_page)

    def open_writing_page(self, writing_name):
        """打开指定的写作页面"""
        if writing_name not in self.writing_pages:
            # 根据创意写作名称创建对应的写作页面
            if writing_name == "零分作文":
                self.writing_pages[writing_name] = ZeroPointPage(self)
                # 将新写作页面添加到堆栈中
                self.stacked_widget.addWidget(self.writing_pages[writing_name])

        if writing_name in self.writing_pages:
            # 切换到写作页面
            self.stacked_widget.setCurrentWidget(self.writing_pages[writing_name])

    def switch_to_writing_list(self):
        """切换到写作列表页面"""
        self.stacked_widget.setCurrentWidget(self.creative_page)

    def add_page(self, page):
        """添加一个新页面到堆栈"""
        self.stacked_widget.addWidget(page)

    def switch_to_page(self, page):
        """切换到指定页面"""
        self.stacked_widget.setCurrentWidget(page)

    def remove_page(self, page):
        """从堆栈中移除指定页面并清理资源"""
        # 确保页面存在
        if page is None:
            return

        # 清理页面资源
        if hasattr(page, "cleanup") and callable(page.cleanup):
            page.cleanup()

        # 从堆栈中移除页面
        self.stacked_widget.removeWidget(page)

        # 删除页面对象
        page.deleteLater()
