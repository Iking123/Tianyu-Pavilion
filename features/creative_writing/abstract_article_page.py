from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from features.chat.chat_component import ChatComponent
from ui.components import GoBackButton


class AbstractArticlePage(QWidget):
    """抽象作文页面"""

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
        self.back_button = GoBackButton(self, "返回写作列表")

        # 页面标题
        title_label = QLabel("零分作文生成器")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

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

        # 创建聊天组件
        self.chat_component = ChatComponent(self.main_window, False, "输入作文标题", 10)
        layout.addWidget(self.chat_component)
        ipp = self.chat_component.input_panel
        ipp.send_callback = self.send_message

        # 设置布局策略
        self.chat_component.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
