from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QSpacerItem,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.components import GoBackButton, RestartButton
from .chat_component import ChatComponent
from ui.main_window import MainWindow


class ChatPage(QWidget):
    """聊天功能页面，包含聊天组件和返回按钮"""

    def __init__(self, main_window: MainWindow):
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

        # 创建聊天组件
        self.chat_component = ChatComponent(self.main_window)
        self.restart = self.chat_component.restart

        # 顶部按钮
        self.back_button = GoBackButton(self)
        self.restart_button = RestartButton(self)

        # 页面标题
        title_label = QLabel("天语阁聊天器")
        title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 布局结构：
        # 1. 添加顶部按钮（左对齐）
        # 2. 添加水平伸缩，使标题能真正居中
        # 3. 添加标题（居中）
        # 4. 再添加一个与返回按钮等宽的空项目，平衡布局
        # 5. 添加水平伸缩，使右侧空间对称

        # 获取按钮的宽度+padding作为占位宽度
        button_width = self.back_button.width() + 10 + self.restart_button.width()

        toolbar_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        toolbar_layout.addWidget(
            self.restart_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        toolbar_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addSpacerItem(
            QSpacerItem(
                button_width, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )
        )
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        layout.addWidget(toolbar)

        # 设置聊天布局
        self.chat_component.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.chat_component)

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
