from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QStatusBar,
    QComboBox,
    QListView,
    QMessageBox,
)
from PyQt6.QtGui import QFont
from core.config_manager import get_config, get_model_name2, update_config
from funcs import get_screen_height
from translate import TRANSLATE
from .home_page import HomePage
from .styles import *


class MainWindow(QMainWindow):
    """主窗口，包含主页和功能页面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("天语阁")

        screen_height = get_screen_height()
        side = int(screen_height * 0.95)
        margin = int(screen_height * 0.05)
        self.setGeometry(margin, margin, side, side)

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
        self.page_index = 0
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

        # 添加按钮、下拉选择框等等
        self.btn_thinking = QPushButton("深度思考")
        self.btn_thinking.setCheckable(True)
        self.btn_thinking.setChecked(get_config("enable_thinking"))
        self.btn_thinking.setStyleSheet(
            self.get_button_style(get_config("enable_thinking"))
        )
        self.btn_thinking.setMaximumWidth(125)
        self.btn_thinking.clicked.connect(self.toggle_thinking)
        left_layout.addWidget(self.btn_thinking)

        self.reasoning_combobox = QComboBox()
        self.reasoning_combobox.setView(QListView())
        self.reasoning_combobox.addItems(
            ["思考程度：无", "思考程度：低", "思考程度：中", "思考程度：高"]
        )
        self.reasoning_combobox.setMaximumWidth(245)
        self.reasoning_combobox.setCurrentText(
            "思考程度：" + TRANSLATE.get(str(get_config("reasoning_effort")), "关闭")
        )
        self.reasoning_combobox.currentIndexChanged.connect(self.change_thinking)
        left_layout.addWidget(self.reasoning_combobox)

        self.model_combobox = QComboBox()
        self.model_combobox.setView(QListView())
        self.model_combobox.addItems(
            [
                "DeepSeek-V3.2",
                "Doubao-Seed-1.8",
                "Gemini 3 Flash",
                "Gemini 2.5 Flash",
                "Gemini 2.5 Flash-Lite",
                "GLM-4.7-Flash",
                "Mistral Large 3",
            ]
        )
        self.model_combobox.setMaximumWidth(385)
        model_name = get_model_name2()
        self.model_combobox.setCurrentText(model_name)
        self.model_combobox.currentIndexChanged.connect(self.change_model)
        left_layout.addWidget(self.model_combobox)

        self.btn_thinking.setVisible(
            model_name
            in [
                "Gemini 3 Flash",
                "Gemini 2.5 Flash",
                "Gemini 2.5 Flash-Lite",
                "DeepSeek-V3.2",
                "GLM-4.7-Flash",
            ]
        )
        self.reasoning_combobox.setVisible(model_name.startswith("Doubao"))

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

        self.baidu_combobox = QComboBox()
        self.baidu_combobox.setView(QListView())
        self.baidu_combobox.addItems(
            ["百度搜索：自动", "百度搜索：开", "百度搜索：关闭"]
        )
        self.baidu_combobox.setMaximumWidth(245)
        self.baidu_combobox.setCurrentText("百度搜索：" + get_config("enable_baidu"))
        self.baidu_combobox.currentIndexChanged.connect(self.change_baidu)
        left_layout.addWidget(self.baidu_combobox)

        # 添加到状态栏左侧
        self.status_bar.addPermanentWidget(left_container, 1)

    def change_model(self, index):
        new_config = get_config()
        model_name = self.model_combobox.currentText()
        new_config["model"] = TRANSLATE.get(model_name)
        update_config(new_config)
        self.btn_thinking.setVisible(
            model_name
            in [
                "Gemini 3 Flash",
                "Gemini 2.5 Flash",
                "Gemini 2.5 Flash-Lite",
                "DeepSeek-V3.2",
                "GLM-4.7-Flash",
            ]
        )
        self.reasoning_combobox.setVisible(model_name.startswith("Doubao"))
        self.update_status()

    def change_thinking(self, index):
        new_config = get_config()
        thinking_text = self.reasoning_combobox.currentText()
        new_config["reasoning_effort"] = TRANSLATE.get(thinking_text[5:])
        update_config(new_config)
        self.update_status()

    def change_baidu(self, index):
        new_config = get_config()
        baidu_text = self.baidu_combobox.currentText()
        new_config["enable_baidu"] = baidu_text[5:]
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

    def toggle_thinking(self):
        """切换一些模型的深度思考状态"""
        new_config = get_config()
        new_config["enable_thinking"] = not new_config["enable_thinking"]
        update_config(new_config)
        self.btn_thinking.setChecked(new_config["enable_thinking"])
        self.btn_thinking.setStyleSheet(
            self.get_button_style(new_config["enable_thinking"])
        )

    def toggle_tavily(self):
        """切换 Tavily 搜索状态"""
        new_config = get_config()
        if not new_config["enable_tavily"] and not new_config["tavily_api_key"]:
            QMessageBox.warning(
                self,
                "启用失败",
                "• 您还没有设置Tavily API！\n\n"
                f"• 如果想用Tavily搜索，请在设置页面填写并保存 Tavily API 密钥！",
            )
            return
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
                from features.chat.chat_page import ChatPage

                self.chat_page = ChatPage(self)
                self.stacked_widget.addWidget(self.chat_page)
            self.stacked_widget.setCurrentWidget(self.chat_page)
        elif index == 2:  # 游戏列表
            if not self.game_page:
                from features.game.game_page import GamePage

                self.game_page = GamePage(self)
                self.stacked_widget.addWidget(self.game_page)
            self.stacked_widget.setCurrentWidget(self.game_page)
        elif index == 3:  # 交互小说
            if not self.interactive_page:
                from features.interactive_novel.interactive_novel_page import (
                    InteractiveNovelPage,
                )

                self.interactive_page = InteractiveNovelPage(self)
                self.stacked_widget.addWidget(self.interactive_page)
            self.stacked_widget.setCurrentWidget(self.interactive_page)
        elif index == 4:  # 创意写作
            if not self.creative_page:
                from features.creative_writing.creative_writing_page import (
                    CreativeWritingPage,
                )

                self.creative_page = CreativeWritingPage(self)
                self.stacked_widget.addWidget(self.creative_page)
            self.stacked_widget.setCurrentWidget(self.creative_page)
        elif index == 5:  # 设置页面
            if not self.settings_page:
                from features.settings.settings_page import SettingsPage

                self.settings_page = SettingsPage(self)
                self.stacked_widget.addWidget(self.settings_page)
            self.stacked_widget.setCurrentWidget(self.settings_page)
        elif index == 6:  # 角色编辑器页面
            if not self.character_editor:
                from features.character.character_editor import CharacterEditor

                self.character_editor = CharacterEditor(self)
                self.stacked_widget.addWidget(self.character_editor)
            self.stacked_widget.setCurrentWidget(self.character_editor)

        self.page_index = index

    def set_status(self, message):
        """设置状态栏消息"""
        self.status_label.setText(message)

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
                from features.game.idiom_solitaire_page import IdiomSolitairePage

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
            if writing_name == "抽象作文":
                from features.creative_writing.abstract_article_page import (
                    AbstractArticlePage,
                )

                self.writing_pages[writing_name] = AbstractArticlePage(self)
                # 将新写作页面添加到堆栈中
                self.stacked_widget.addWidget(self.writing_pages[writing_name])
            if writing_name == "零分作文":
                from features.creative_writing.zero_point_page import ZeroPointPage

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
