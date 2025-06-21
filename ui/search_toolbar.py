# search_toolbar.py
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SearchToolbar(QWidget):
    """通用的搜索工具栏组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # 搜索标签
        search_label = QLabel("搜索:")
        search_label.setStyleSheet(
            "font-size: 12pt; font-weight: bold; color: #4A90E2;"
        )

        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索词 (Ctrl+F)")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedHeight(50)
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #4A90E2;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 11pt;
                min-width: 300px;
            }
        """
        )

        # 导航按钮
        self.prev_button = QPushButton("◀ 上一个")
        self.prev_button.setFixedSize(120, 40)
        self.prev_button.setStyleSheet(
            """
            QPushButton {
                background-color: #DBEAFE;
                color: #4D6BFE;
                border: 1px solid #007AFF;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 0;
            }
            QPushButton:hover {
                background-color: #C7D7FE;
            }
            """
        )

        self.next_button = QPushButton("下一个 ▶")
        self.next_button.setFixedSize(120, 40)
        self.next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #DBEAFE;
                color: #4D6BFE;
                border: 1px solid #007AFF;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 0;
            }
            QPushButton:hover {
                background-color: #C7D7FE;
            }
            """
        )

        # 匹配计数
        self.match_label = QLabel("0/0")
        self.match_label.setFixedSize(120, 40)
        self.match_label.setAlignment(Qt.AlignCenter)
        self.match_label.setStyleSheet(
            """
            QLabel {
                background-color: #F0F7FF;
                border: 2px solid #4A90E2;
                border-radius: 8px;
                color: #4A90E2;
                font-size: 14pt;
                font-weight: bold;
            }
        """
        )

        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.setFixedSize(100, 40)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #DBEAFE;
                color: #4D6BFE;
                border: 1px solid #007AFF;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 0;
            }
            QPushButton:hover {
                background-color: #C7D7FE;
            }
            """
        )

        # 添加到布局
        layout.addWidget(search_label)
        layout.addWidget(self.search_input, 2)  # 增加权重
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.match_label)
        layout.addWidget(self.close_button)

        # 设置搜索工具栏初始不可见
        self.setVisible(False)

        # 设置大小策略，确保在布局中正确显示
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def connect_signals(self, search_changed, prev_action, next_action, close_action):
        """连接信号到外部处理函数"""
        self.search_input.textChanged.connect(search_changed)
        self.prev_button.clicked.connect(prev_action)
        self.next_button.clicked.connect(next_action)
        self.close_button.clicked.connect(close_action)

    def set_match_count(self, current, total):
        """设置匹配计数显示"""
        self.match_label.setText(f"{current}/{total}")

    def get_search_term(self):
        """获取搜索词"""
        return self.search_input.text().strip()

    def focus_search_input(self):
        """聚焦到搜索输入框并选中所有文本"""
        self.search_input.setFocus()
        self.search_input.selectAll()
