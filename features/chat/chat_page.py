from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QLabel,
    QSpacerItem,
)
from PyQt5.QtGui import QIcon, QFont
from .chat_component import ChatComponent
from PyQt5.QtCore import Qt


class ChatPage(QWidget):
    """聊天功能页面，包含聊天组件和返回按钮"""

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
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 8pt;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #3A7BC8;
            }
        """
        )
        self.back_button.clicked.connect(self.go_back)

        # 页面标题
        title_label = QLabel("DeepSeek聊天器")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 布局结构：
        # 1. 添加返回按钮（左对齐）
        # 2. 添加水平伸缩，使标题能真正居中
        # 3. 添加标题（居中）
        # 4. 再添加一个与返回按钮等宽的空项目，平衡布局
        # 5. 添加水平伸缩，使右侧空间对称

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

        # 创建聊天组件
        self.chat_component = ChatComponent(self.main_window)
        layout.addWidget(self.chat_component)

        # 设置布局策略
        self.chat_component.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # # 连接滚动按钮
        # if self.main_window:
        #     scroll_button = self.main_window.get_scroll_button()
        #     scroll_button.clicked.connect(self.chat_component.scroll_to_bottom)

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)

    def cleanup(self):
        """清理资源"""
        if hasattr(self, "chat_component") and self.chat_component:
            self.chat_component.cleanup()

    def showEvent(self, event):
        """页面显示时自动设置焦点到聊天组件"""
        super().showEvent(event)
        self.chat_component.setFocus()
        self.main_window.set_status(
            "处理中..." if self.chat_component.worker_active else "就绪"
        )
