from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QDialog,
    QScrollArea,
    QWidget,
    QTextEdit,
    QPushButton,
    QSizePolicy,
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import os
from ui.message_display import MessageDisplayArea


class CharacterButton(QFrame):
    """角色按钮，显示角色信息"""

    clicked = pyqtSignal()  # 自定义 clicked 信号

    def __init__(self, character_data, parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self.setMinimumHeight(120)
        self.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手型
        self.setStyleSheet(
            """
            CharacterButton {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
            CharacterButton:hover {
                border: 2px solid #4A90E2;
                background-color: #F5F9FF;
            }
        """
        )
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)

        # 角色头像
        icon_label = QLabel()
        fixed_height = 100  # 固定高度
        if self.character_data.get("avatar") and os.path.exists(
            self.character_data["avatar"]
        ):
            pixmap = QPixmap(self.character_data["avatar"])
        elif os.path.exists("default_avatar.png"):
            pixmap = QPixmap("default_avatar.png")
        else:
            pixmap = QPixmap()  # 使用空图标

        if not pixmap.isNull():
            # 按高度等比例缩放
            scaled_pixmap = pixmap.scaledToHeight(
                fixed_height, Qt.SmoothTransformation  # 使用平滑缩放，提高质量
            )
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)

        # 角色信息区域
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # 角色标题（名称）
        name = self.character_data.get("name", "未知角色") or "未知角色"
        title_label = QLabel(name)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")
        info_layout.addWidget(title_label)

        # 角色描述
        gender = self.character_data.get("gender", "未知性别") or "未知性别"
        age = self.character_data.get("age", "未知年龄") or "未知年龄"
        identity = self.character_data.get("identity", "未知身份") or "未知身份"
        desc_label = QLabel(f"{gender} - {age} - {identity}")
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #7F8C8D;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, 1)  # 添加伸缩因子使描述区域可以扩展

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # 触发 clicked 信号
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """鼠标进入事件 - 增强悬停效果"""
        self.setStyleSheet(
            """
            CharacterButton {
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
        self.setStyleSheet(
            """
            CharacterButton {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
        """
        )
        super().leaveEvent(event)


class SelectableCharacterButton(CharacterButton):
    """支持选中状态的角色按钮"""

    def __init__(self, character_data, preserved=False, parent=None):
        super().__init__(character_data, parent)
        self.preserved = preserved
        self.selected = False
        # 保存原始悬停样式
        self.hover_style = """
            CharacterButton {
                background-color: #F5F9FF;
                border-radius: 10px;
                border: 2px solid #4A90E2;
                margin: 10px 0;
            }
        """
        # 保存原始非悬停样式
        self.normal_style = """
            CharacterButton {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
        """
        # 选中样式
        self.selected_style = """
            CharacterButton {
                background-color: #E3F2FD;
                border-radius: 10px;
                border: 2px solid #2196F3;
                margin: 5px 0;
            }
        """
        self.setStyleSheet(self.normal_style)

    def set_selected(self, selected):
        """设置选中状态，若被保护则无法选中"""
        if self.preserved:
            return
        self.selected = selected
        self.update_style()

    def update_style(self):
        """根据状态更新样式"""
        if self.selected:
            self.setStyleSheet(self.selected_style)
        else:
            self.setStyleSheet(self.normal_style)

    def enterEvent(self, event):
        """鼠标进入事件 - 只在非选中状态下的非保护按钮应用悬停效果"""
        if not self.selected and not self.preserved:
            super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件 - 只在非选中状态下的非保护按钮恢复原始样式"""
        if not self.selected and not self.preserved:
            super().leaveEvent(event)


class CharacterDetailDialog(QDialog):
    """角色详情对话框，将基本信息和详细信息分开显示"""

    def __init__(self, parent=None, character=None):
        super().__init__(parent)
        self.character = character or {}
        self.setup_ui()

    def setup_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle(f"角色详情 - {self.character.get('name', '未知角色')}")
        self.setMinimumSize(1380, 1740)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === 基本信息区域（带滚动条，高度≤550） ===
        basic_info_scroll = QScrollArea()
        basic_info_scroll.setWidgetResizable(True)
        basic_info_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        basic_info_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        basic_info_scroll.setMaximumHeight(550)  # 关键：限制基本信息区域最大高度

        # 基本信息内容区域
        basic_info_widget = QWidget()
        basic_info_layout = QHBoxLayout(basic_info_widget)
        basic_info_layout.setSpacing(20)
        basic_info_layout.setContentsMargins(20, 20, 20, 20)

        # 头像区域
        avatar_frame = QFrame()
        avatar_frame.setStyleSheet(
            "border: 1px solid #ddd; border-radius: 5px; background-color: white;"
        )
        avatar_layout = QVBoxLayout(avatar_frame)
        avatar_layout.setContentsMargins(5, 5, 5, 5)

        avatar_label = QLabel()
        avatar_label.setFixedSize(264, 350)  # 固定头像尺寸
        avatar_label.setAlignment(Qt.AlignCenter)

        if self.character.get("avatar") and os.path.exists(self.character["avatar"]):
            pixmap = QPixmap(self.character["avatar"])
            scaled_pixmap = pixmap.scaled(
                264, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            avatar_label.setPixmap(scaled_pixmap)
        else:
            avatar_label.setText("无头像")
            avatar_label.setStyleSheet("color: #666;")

        avatar_layout.addWidget(avatar_label, alignment=Qt.AlignCenter)
        basic_info_layout.addWidget(avatar_frame)

        # 标签信息区域
        labels_frame = QFrame()
        labels_layout = QVBoxLayout(labels_frame)
        labels_layout.setSpacing(10)
        labels_layout.setContentsMargins(0, 0, 0, 0)

        # 基本信息标签
        basic_labels = [
            ("姓名", "name"),
            ("性别", "gender"),
            ("年龄", "age"),
            ("身份", "identity"),
        ]

        for title, key in basic_labels:
            value = self.character.get(key, "未知")
            label = QLabel(f"<b>{title}：</b> {value}")
            if key == "name":
                label.setFont(QFont("Arial", 12, QFont.Bold))
            labels_layout.addWidget(label)

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        labels_layout.addWidget(line)

        basic_info_layout.addWidget(labels_frame, 1)  # 占据剩余空间

        # 设置滚动区域内容
        basic_info_scroll.setWidget(basic_info_widget)
        main_layout.addWidget(basic_info_scroll)

        details_area = MessageDisplayArea()
        details_area.setMinimumHeight(200)  # 设置最小高度，避免内容太少时区域过窄

        # 添加详细信息
        details = [
            ("简介", self.character.get("summary", "无")),
            ("性格", self.character.get("personality", "无")),
            ("兴趣", self.character.get("hobbies", "无")),
            ("背景设定", self.character.get("background", "无")),
            ("问候语", self.character.get("greetings", "无")),
        ]

        for title, content in details:
            details_area.add_message_by_role(
                f"assistant_{title}", content, auto_scroll=False
            )

        details_area.container_layout.addSpacing(50)
        main_layout.addWidget(details_area, 1)  # 占据剩余空间

        # # === 底部按钮 ===
        # button_layout = QHBoxLayout()
        # button_layout.setSpacing(10)
        # button_layout.setContentsMargins(20, 10, 20, 10)

        # close_button = QPushButton("关闭")
        # close_button.setFixedWidth(100)
        # close_button.setStyleSheet(
        #     """
        #     QPushButton {
        #         background-color: #4a90e2;
        #         color: white;
        #         border-radius: 5px;
        #         padding: 8px 16px;
        #     }
        #     QPushButton:hover {
        #         background-color: #3a80d2;
        #     }
        # """
        # )
        # close_button.clicked.connect(self.close)

        # button_layout.addStretch()  # 左侧填充
        # button_layout.addWidget(close_button)
        # button_layout.addStretch()  # 右侧填充

        # main_layout.addLayout(button_layout)

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """
        )
        main_layout.addWidget(close_button)
