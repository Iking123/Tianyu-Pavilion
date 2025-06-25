from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QScrollArea,
    QFrame,
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize


class GameCard(QFrame):
    """横向游戏卡片控件"""

    def __init__(self, title, description, icon_path, click_handler, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setStyleSheet(
            """
            GameCard {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
            GameCard:hover {
                border: 2px solid #4A90E2;
                background-color: #F5F9FF;
            }
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)

        # 游戏图标
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            pixmap = QPixmap(80, 80)
            pixmap.fill(QColor(74, 144, 226))  # 蓝色占位符
        icon_label.setPixmap(
            pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # 游戏信息区域
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # 游戏标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")
        info_layout.addWidget(title_label)

        # 游戏描述
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #7F8C8D;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, 1)  # 添加伸缩因子使描述区域可以扩展

        # 游戏按钮
        self.play_button = QPushButton("开始\n游戏")
        self.play_button.setFixedSize(80, 80)
        self.play_button.setFont(QFont("Arial", 10))
        self.play_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3A7BC8;
            }
        """
        )
        self.play_button.clicked.connect(click_handler)
        layout.addWidget(self.play_button, 0, Qt.AlignRight)

        layout.addStretch(0)


class GamePage(QWidget):
    """小游戏功能页面"""

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
                font-size: 8pt;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )
        self.back_button.clicked.connect(self.go_back)

        # 页面标题
        title_label = QLabel("小游戏")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 获取返回按钮的宽度作为占位宽度
        button_width = self.back_button.sizeHint().width()

        toolbar_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        toolbar_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        toolbar_layout.addSpacerItem(
            QSpacerItem(button_width, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        )
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        layout.addWidget(toolbar)

        # 游戏列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: #F5F7FA;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)

        # 标题
        games_title = QLabel("选择一个小游戏")
        games_title.setFont(QFont("Arial", 18, QFont.Bold))
        games_title.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        games_title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(games_title)

        # 游戏卡片容器 - 使用垂直布局
        games_container = QWidget()
        games_layout = QVBoxLayout(games_container)
        games_layout.setContentsMargins(0, 0, 0, 0)
        games_layout.setSpacing(10)

        # 添加游戏卡片 (暂时使用占位图标)
        games = [
            {
                "title": "成语接龙",
                "description": "与AI进行成语接龙对战，看谁能坚持到最后！",
                "icon": "icons/idiom.png",
            },
            {
                "title": "数学挑战",
                "description": "挑战你的数学能力，解决各种数学难题",
                "icon": "icons/math.png",
            },
            {
                "title": "单词拼写",
                "description": "测试你的英语词汇量，提升拼写能力",
                "icon": "icons/spelling.png",
            },
            {
                "title": "知识问答",
                "description": "涵盖科学、历史、文化等领域的趣味问答",
                "icon": "icons/quiz.png",
            },
        ]

        for game in games:
            # 创建闭包函数来正确捕获当前游戏的标题
            def create_handler(title):
                return lambda: self.open_game(title)

            card = GameCard(
                game["title"],
                game["description"],
                game["icon"],
                create_handler(game["title"]),  # 使用闭包正确捕获当前游戏标题
            )
            games_layout.addWidget(card)

        # 添加底部留白
        games_layout.addStretch()

        container_layout.addWidget(games_container)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)

    def open_game(self, game_title):
        """打开选中的游戏"""
        if self.main_window:
            self.main_window.open_game_page(game_title)
