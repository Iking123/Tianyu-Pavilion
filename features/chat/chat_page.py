from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QSpacerItem,
    QInputDialog,
    QMessageBox,
    QDialog,
    QLineEdit,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .history_sidebar import HistorySidebar, SidebarButton
from ui.components import GoBackButton, RestartButton
from .chat_component import ChatComponent
from ui.main_window import MainWindow


class ChatPage(QWidget):
    """聊天功能页面，包含聊天组件和返回按钮"""

    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window

        # 主布局 - 改为水平布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建历史侧边栏
        self.history_sidebar = HistorySidebar(self)
        self.history_sidebar.setFixedWidth(300)  # 设置侧边栏宽度
        self.history_sidebar.chat_selected.connect(self.on_chat_selected)
        self.history_sidebar.new_chat_requested.connect(self.on_new_chat_requested)
        self.history_sidebar.rename_chat_requested.connect(self.on_rename_chat)
        self.history_sidebar.delete_chat_requested.connect(self.on_delete_chat)
        self.history_sidebar.setVisible(False)

        # 创建右侧聊天区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F0F2F5; padding: 10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 创建聊天组件
        self.chat_component = ChatComponent(self.main_window)
        self.restart = self.chat_component.restart

        # 顶部按钮
        self.sidebar_button = SidebarButton(self)
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
        button_width = (
            self.sidebar_button.width()
            + 10
            + self.back_button.width()
            + 10
            + self.restart_button.width()
        )

        toolbar_layout.addWidget(
            self.sidebar_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
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

        right_layout.addWidget(toolbar)

        # 设置聊天布局
        self.chat_component.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        right_layout.addWidget(self.chat_component)

        # 添加到主布局
        main_layout.addWidget(self.history_sidebar)
        main_layout.addWidget(right_widget)

        # 加载历史对话列表
        self.load_chat_list()

    def load_chat_list(self):
        """加载历史对话列表"""
        chats = self.chat_component.history_manager.get_all_chats()
        self.history_sidebar.load_chats(chats)

    def on_chat_selected(self, chat_id):
        """处理历史对话选择"""
        self.chat_component.load_chat_history(chat_id)

    def on_new_chat_requested(self):
        """处理新建对话请求"""
        self.chat_component.restart(force=True)
        self.chat_component.chat_id = None
        self.load_chat_list()  # 刷新列表

    def on_rename_chat(self, chat_id: str):
        """重命名聊天"""
        # 弹出对话框获取新标题
        # new_title, ok = QInputDialog.getText(self, "修改标题", "请输入新标题:")
        input_dialog = QInputDialog(self)
        input_dialog.setInputMode(QInputDialog.InputMode.TextInput)
        input_dialog.setWindowTitle("修改标题")
        input_dialog.setLabelText("请输入新标题（最多30个字符）：")
        line_edit = input_dialog.findChild(QLineEdit)
        if line_edit:
            line_edit.setMaxLength(30)
        title = self.chat_component.history_manager.get_title_by_id(chat_id)
        input_dialog.setTextValue(title)
        input_dialog.resize(960, 120)
        input_dialog.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        input_dialog.show()
        if input_dialog.exec() == QDialog.DialogCode.Accepted:
            new_title = input_dialog.textValue()  # 点击ok 后 获取输入对话框内容
            # 更新数据库和界面
            self.chat_component.history_manager.update_chat_title(chat_id, new_title)
            self.history_sidebar.update_chat_title(chat_id, new_title)

    def on_delete_chat(self, chat_id: str):
        """删除聊天"""
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个对话吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 从数据库删除
            self.chat_component.history_manager.delete_chat(chat_id)
            # 重新加载聊天列表
            self.load_chat_list()

    # 在 showEvent 方法中添加刷新列表
    def showEvent(self, event):
        """页面显示时自动设置焦点到聊天组件并刷新历史列表"""
        super().showEvent(event)
        self.chat_component.setFocus()
        self.main_window.set_status(
            "处理中..." if self.chat_component.worker_active else "就绪"
        )
        self.load_chat_list()  # 刷新历史对话列表

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
