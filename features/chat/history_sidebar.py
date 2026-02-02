import re
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QToolButton,
    QMenu,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime

from funcs import resource_path


class NewChatButton(QPushButton):
    """自定义新对话按钮组件"""

    def __init__(self, parent=None, tip="开启新对话"):
        super().__init__(parent)
        self.setFixedHeight(60)  # 固定按钮高度
        self.setIconSize(QSize(134, 28))  # 图标大小

        # 使用资源路径加载图标
        self.setIcon(QIcon(resource_path("resources/images/newchat.png")))

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #e5ebf7;
                border-radius: 15px;
                border: 1px solid #A3C8FF;
            }
            QPushButton:hover {
                background-color: #dae4f7;
            }
            QPushButton:pressed {
                background-color: #dae4f7;
            }
        """
        )

        # 设置工具提示
        self.setToolTip(tip)

        # 设置手形
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class CustomItem(QWidget):
    """自定义聊天项组件"""

    # 定义操作信号
    rename_requested = pyqtSignal(str)  # 传递聊天ID
    delete_requested = pyqtSignal(str)  # 传递聊天ID

    def __init__(self, chat_id: str):
        super().__init__()
        self.chat_id = chat_id
        self.menu_btn = None  # "..." 按钮
        self.is_selected = False  # 是否被选中
        self.init_ui()
        self.set_normal_style()

    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        # 左侧：标题和时间
        left_widget = QWidget()
        left_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 标题
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.Medium))
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumWidth(260)

        # 时间
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 8))
        self.time_label.setStyleSheet("color: #757575;")
        self.time_label.setMaximumWidth(260)

        left_layout.addWidget(self.title_label)
        left_layout.addWidget(self.time_label)

        # 右侧："..." 按钮（初始隐藏）
        self.menu_btn = QToolButton()
        self.menu_btn.setText("···")
        self.menu_btn.setFixedSize(48, 48)
        self.menu_btn.setVisible(False)  # 默认隐藏

        # 设置菜单按钮样式
        self.menu_btn.setStyleSheet(
            """
            QToolButton {
                background-color: transparent;
                border: none;
                color: #555;
                font-size: 18px;
                font-weight: bold;
            }
            QToolButton:hover {
                color: #1976D2;
                background-color: #E3F2FD;
                border-radius: 24px;
            }
        """
        )

        # 创建菜单
        self.init_menu()

        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # 设置手形
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def init_menu(self):
        """初始化操作菜单"""
        menu = QMenu()

        # 添加菜单项
        rename_action = menu.addAction("修改标题")
        delete_action = menu.addAction("删除对话")

        # 连接信号
        rename_action.triggered.connect(
            lambda: self.rename_requested.emit(self.chat_id)
        )
        delete_action.triggered.connect(
            lambda: self.delete_requested.emit(self.chat_id)
        )

        self.menu_btn.setMenu(menu)
        self.menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

    def set_content(self, title: str, time_str: str):
        """设置内容"""
        self.title_label.setText(re.sub(r"[\r\n]+", " ", title))
        self.time_label.setText(time_str)

    def set_selected_style(self):
        """设置选中样式"""
        self.is_selected = True
        self.menu_btn.setVisible(True)  # 显示菜单按钮
        # self.setStyleSheet(
        #     """
        #     QWidget {
        #         background-color: #E3F2FD;
        #         color: #1976D2;
        #         border-radius: 10px;
        #     }
        # """
        # )
        # 更新标题颜色
        self.title_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        self.time_label.setStyleSheet("color: #1976D2;")

    def set_normal_style(self):
        """设置普通样式"""
        self.is_selected = False
        self.menu_btn.setVisible(False)  # 隐藏菜单按钮
        self.setStyleSheet(
            """
            QWidget {
                background-color: none;
                color: #555;
                padding: 0px;
                border-radius: 10px;
            }
            QWidget:hover {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """
        )
        # 重置标签颜色
        self.title_label.setStyleSheet("color: #555;")
        self.time_label.setStyleSheet("color: #757575;")

    def set_selected(self, selected: bool):
        """设置选中状态"""
        if selected:
            self.set_selected_style()
        else:
            self.set_normal_style()


class HistorySidebar(QWidget):
    """历史对话侧边栏组件"""

    chat_selected = pyqtSignal(str)  # 传递聊天ID
    new_chat_requested = pyqtSignal()
    rename_chat_requested = pyqtSignal(str)  # 重命名请求
    delete_chat_requested = pyqtSignal(str)  # 删除请求

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 标题
        title_label = QLabel("历史对话")
        title_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)

        # 新建对话按钮
        self.new_chat_btn = NewChatButton()
        self.new_chat_btn.clicked.connect(self.new_chat_requested.emit)
        layout.addWidget(self.new_chat_btn)

        # 分隔线
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line)

        # 对话列表
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.on_chat_selected)
        layout.addWidget(self.chat_list)

        # 设置样式
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """
        )
        self.chat_list.setStyleSheet(
            """
            QListWidget {
                border: none;
                background-color: #F8F9FA;
            }
            QListWidget::item {
                padding: 0px;
                border-bottom: 1px solid #E0E0E0;
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background: transparent;  # 禁用默认选中样式
            }
        """
        )

    def load_chats(self, chats):
        """加载聊天列表"""
        self.chat_list.clear()

        for chat in chats:
            # 格式化时间
            timestamp = datetime.fromisoformat(chat["timestamp"])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M")

            # 创建列表项
            item = QListWidgetItem()
            item_widget = CustomItem(chat["id"])
            item_widget.set_content(chat["title"], time_str)

            # 连接操作信号
            item_widget.rename_requested.connect(self.rename_chat_requested.emit)
            item_widget.delete_requested.connect(self.delete_chat_requested.emit)

            item.setSizeHint(item_widget.sizeHint())
            self.chat_list.addItem(item)
            self.chat_list.setItemWidget(item, item_widget)

            # 存储聊天ID到item中
            item.setData(Qt.ItemDataRole.UserRole, chat["id"])

            # 存储widget引用以便后续访问
            item.setData(Qt.ItemDataRole.UserRole + 1, item_widget)

    def on_chat_selected(self, clicked_item: QListWidgetItem):
        """处理聊天项点击"""
        # 更新所有项的选中状态
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            widget = self.chat_list.itemWidget(item)
            if widget:
                if item is clicked_item:
                    widget.set_selected_style()
                else:
                    widget.set_normal_style()

        # 发射选中信号
        chat_id = clicked_item.data(Qt.ItemDataRole.UserRole)
        self.chat_selected.emit(chat_id)

    def update_chat_title(self, chat_id: str, new_title: str):
        """更新聊天标题"""
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == chat_id:
                widget = self.chat_list.itemWidget(item)
                if widget:
                    # 更新标题（保持时间不变）
                    current_time = widget.time_label.text()
                    widget.set_content(new_title, current_time)
                break


class SidebarButton(QPushButton):
    """自定义边栏按钮组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 70)  # 固定按钮大小
        self.setIconSize(QSize(28, 28))  # 图标大小

        # 使用资源路径加载图标
        self.hide_icon = QIcon(resource_path("resources/images/hide_sidebar.svg"))
        self.show_icon = QIcon(resource_path("resources/images/show_sidebar.svg"))
        self.setIcon(self.show_icon)

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border-radius: 35px;  /* 圆形按钮 */
            }
            QPushButton:hover {
                background-color: #E0E0E0;  /* 鼠标悬停时的灰色背景 */
            }
            QPushButton:pressed {
                background-color: #C0C0C0;  /* 按下时稍深的灰色 */
            }
        """
        )

        # 设置手形
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 设置工具提示
        self.setToolTip("显示侧边栏")

        self.page = parent
        if parent and hasattr(parent, "history_sidebar"):
            self.clicked.connect(self.toggle_sidebar)

    def toggle_sidebar(self):
        sb = self.page.history_sidebar
        if sb.isVisible():
            sb.setVisible(False)
            self.setIcon(self.show_icon)
            self.setToolTip("显示侧边栏")
        else:
            sb.setVisible(True)
            self.setIcon(self.hide_icon)
            self.setToolTip("隐藏侧边栏")
