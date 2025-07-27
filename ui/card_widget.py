from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont, QPixmap


class CardWidget(QFrame):
    """通用的卡片小部件基类"""

    clicked = pyqtSignal()  # 自定义点击信号

    def __init__(self, title, description, icon_path=None, min_height=120, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(min_height)
        self.setCursor(Qt.PointingHandCursor)
        self.title = title
        self.description = description
        self.icon_path = icon_path

        # 基础样式
        self.normal_style = """
            CardWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
            CardWidget:hover {
                border: 2px solid #4A90E2;
                background-color: #F5F9FF;
            }
        """

        self.setStyleSheet(self.normal_style)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)

        # 添加图标（如果有）
        if self.icon_path:
            icon_label = QLabel()
            fixed_height = 100

            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaledToHeight(
                    fixed_height, Qt.SmoothTransformation
                )
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setAlignment(Qt.AlignCenter)

            layout.addWidget(icon_label)

        # 信息区域
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")
        info_layout.addWidget(title_label)

        # 描述
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #7F8C8D;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, 1)  # 添加伸缩因子

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """鼠标进入事件 - 增强悬停效果"""
        self.setStyleSheet(
            """
            CardWidget {
                background-color: #F5F9FF;
                border-radius: 10px;
                border: 2px solid #4A90E2;
                margin: 10px 0;
            }
        """
        )
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件 - 恢复原始样式"""
        self.setStyleSheet(self.normal_style)
        super().leaveEvent(event)
