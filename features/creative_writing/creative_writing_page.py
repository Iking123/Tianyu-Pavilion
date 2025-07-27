from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QScrollArea,
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize
from funcs import resource_path
from ui.card_widget import CardWidget
from ui.components import GoBackButton


class writingCard(CardWidget):
    """横向写作卡片控件 - 可点击的长条形按钮"""

    def __init__(self, title, description, icon_path, click_handler, parent=None):
        super().__init__(title, description, icon_path, parent=parent)
        self.click_handler = click_handler

    def mousePressEvent(self, event):
        """重写鼠标点击事件，添加自定义处理"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.click_handler()


class CreativeWritingPage(QWidget):
    """创意写作功能页面"""

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
        self.back_button = GoBackButton(self, "返回主页")

        # 页面标题
        title_label = QLabel("创意写作")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 获取返回按钮的宽度作为占位宽度
        button_width = self.back_button.width()

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

        # 写作列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: #F5F7FA;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)

        # 标题
        writings_title = QLabel("选择一种创意写作")
        writings_title.setFont(QFont("Arial", 18, QFont.Bold))
        writings_title.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        writings_title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(writings_title)

        # 写作卡片容器 - 使用垂直布局
        writings_container = QWidget()
        writings_layout = QVBoxLayout(writings_container)
        writings_layout.setContentsMargins(0, 0, 0, 0)
        writings_layout.setSpacing(10)

        # 添加写作卡片
        writings = [
            {
                "title": "抽象作文",
                "description": "使用传统方法，纯随机式输出，写就抽象作文。不调用大模型API，故不消耗token；不过会调用一言api来获取名言金句。",
                "icon": resource_path("resources/icons/abstract.png"),
            },
            {
                "title": "零分作文",
                "description": "用大语言模型，创作零分作文！",
                "icon": resource_path("resources/icons/zero.png"),
            },
        ]

        for writing in writings:
            # 创建闭包函数来正确捕获当前写作的标题
            def create_handler(title):
                return lambda: self.open_writing(title)

            card = writingCard(
                writing["title"],
                writing["description"],
                writing["icon"],
                create_handler(writing["title"]),  # 使用闭包正确捕获当前写作标题
            )
            writings_layout.addWidget(card)

        # 添加底部留白
        writings_layout.addStretch()

        container_layout.addWidget(writings_container)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)

    def open_writing(self, writing_title):
        """打开选中的写作"""
        if self.main_window:
            self.main_window.open_writing_page(writing_title)
