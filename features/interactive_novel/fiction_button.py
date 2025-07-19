from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QDialog,
    QVBoxLayout,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
    QDialogButtonBox,
    QMessageBox,
    QScrollArea,
    QWidget,
    QPushButton,
)
from PyQt5.QtGui import QFont, QColor
from core.character_manager import get_all_characters, get_character_name
from core.fiction_manager import get_fiction_by_id
from features.character.character_button import SelectableCharacterButton


class FictionButton(QFrame):
    """小说按钮，显示小说信息"""

    clicked = pyqtSignal()  # 自定义 clicked 信号

    def __init__(self, fiction_data, parent=None):
        super().__init__(parent)
        self.fiction_data = fiction_data
        self.setMinimumHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            """
            FictionButton {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
            FictionButton:hover {
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

        # 小说信息区域
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # 小说标题
        title = self.fiction_data.get("name", "未知小说") or "未知小说"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")
        info_layout.addWidget(title_label)

        # 小说简介
        blurb = self.fiction_data.get("blurb", "无简介") or "无简介"
        blurb_label = QLabel(blurb)
        blurb_label.setFont(QFont("Arial", 10))
        blurb_label.setStyleSheet("color: #7F8C8D;")
        blurb_label.setWordWrap(True)
        info_layout.addWidget(blurb_label)

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
            FictionButton {
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
            FictionButton {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                margin: 10px 0;
            }
        """
        )
        super().leaveEvent(event)


class FictionStartDialog(QDialog):
    """小说启动对话框，用于选择角色"""

    def __init__(self, parent=None, fiction_id=None):
        super().__init__(parent)
        self.fiction_id = fiction_id
        self.selected_characters = []
        self.forced_character_id = None
        self.characters_num_level = 3  # 默认3级（最多3人）
        self.direct = False  # 默认不允许直接进入

        # 获取小说信息（如果有强制角色）
        if self.fiction_id:
            fiction = get_fiction_by_id(self.fiction_id)
            if fiction:
                self.forced_character_id = fiction.get("forced_character_id")
                if self.forced_character_id:
                    self.selected_characters.append(self.forced_character_id)
                self.characters_num_level = fiction.get("characters_num_level", 3)
                self.direct = fiction.get("direct", False)

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("选择角色")
        self.setMinimumSize(1380, 1720)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("请选择参与小说的角色")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 角色数量提示
        max_characters = self.get_max_characters()
        subtitle_text = f"最多可选择 {max_characters} 个角色"
        if self.forced_character_id:
            subtitle_text += " (包含强制角色)"

        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #7F8C8D; margin-bottom: 10px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # 角色选择区域（使用滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")

        # 角色容器
        self.characters_container = QWidget()
        self.characters_layout = QVBoxLayout(self.characters_container)
        self.characters_layout.setSpacing(10)
        self.characters_layout.setContentsMargins(5, 5, 5, 5)
        self.characters_layout.addStretch(1)  # 底部添加伸缩因子

        # 添加角色
        self.load_characters()

        scroll_area.setWidget(self.characters_container)
        layout.addWidget(scroll_area, 1)  # 占据剩余空间

        # 按钮区域
        button_layout = QHBoxLayout()

        # 添加"直接进入"按钮（如果允许）
        if self.direct:
            direct_button = QPushButton("直接进入")
            direct_button.setMinimumSize(100, 40)
            direct_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #43A047;
                }
                """
            )
            direct_button.clicked.connect(self.direct_enter)
            button_layout.addWidget(direct_button)

        button_layout.addStretch(1)  # 添加伸缩因子

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_layout.addWidget(button_box)

        layout.addLayout(button_layout)

    def get_max_characters(self):
        """根据级别获取最大角色数"""
        if self.characters_num_level <= 3:
            return self.characters_num_level
        else:  # level 4
            return 10

    def load_characters(self):
        """加载所有角色"""
        characters = get_all_characters()

        # 首先添加强制角色（如果有）
        if self.forced_character_id:
            for char in characters:
                if char["id"] == self.forced_character_id:
                    self.add_character_button(char, is_forced=True)
                    break

        # 添加其他角色
        for char in characters:
            if self.forced_character_id and char["id"] == self.forced_character_id:
                continue  # 跳过已添加的强制角色
            self.add_character_button(char)

    def add_character_button(self, character, is_forced=False):
        """添加角色按钮"""
        # 使用新的SelectableCharacterButton
        button = SelectableCharacterButton(character, is_forced, self)

        # 设置强制角色的特殊样式
        if is_forced:
            button.setStyleSheet(
                """
                CharacterButton {
                    background-color: #FFF8E1;
                    border-radius: 10px;
                    border: 2px solid #FFC107;
                    margin: 5px 0;
                }
                CharacterButton:hover {
                    background-color: #FFF0C2;
                    border: 2px solid #FFA000;
                }
                """
            )
            # 添加强制标识
            forced_label = QLabel("强制角色")
            forced_label.setFont(QFont("Arial", 8, QFont.Bold))
            forced_label.setStyleSheet(
                "background-color: #FFC107;"
                "color: white;"
                "border-radius: 3px;"
                "padding: 2px 5px;"
                "margin-left: 10px;"
            )
            button.layout().addWidget(forced_label)

        # 连接点击信号
        button.clicked.connect(
            lambda ch=character: self.toggle_character_selection(ch, button)
        )

        # 添加到布局（顶部）
        self.characters_layout.insertWidget(self.characters_layout.count() - 1, button)

    def toggle_character_selection(self, character, button):
        """切换角色选择状态"""
        character_id = character["id"]

        # 强制角色不可取消
        if character_id == self.forced_character_id:
            return

        # 检查是否已选中
        if character_id in self.selected_characters:
            # 取消选择
            self.selected_characters.remove(character_id)
            button.set_selected(False)  # 更新按钮状态
        else:
            # 检查是否超过最大数量
            max_chars = self.get_max_characters()
            forced_count = 1 if self.forced_character_id else 0
            if len(self.selected_characters) + forced_count >= max_chars:
                QMessageBox.warning(
                    self, "选择限制", f"最多只能选择 {max_chars} 个角色！"
                )
                return

            # 若当前小说为4级角色数（至多10人），则检查该角色是否有简介
            if self.characters_num_level == 4 and not character.get("summary", None):
                name = character.get("name", "该角色")
                QMessageBox.warning(
                    self,
                    "选择限制",
                    "• 由于本小说至多容许10名主角进入，为节约token，仅能选有简介的角色！\n\n"
                    f"• 如果想用{name}，请在角色编辑器页面为{name}添加简介！",
                )
                return

            # 添加选择
            self.selected_characters.append(character_id)
            button.set_selected(True)  # 更新按钮状态

    def accept(self):
        max_chars = self.get_max_characters()

        if (
            len(self.selected_characters) - bool(self.forced_character_id) == 0
            and not self.direct
        ):
            QMessageBox.warning(self, "选择错误", "必须选择至少1名主角！")
            return

        if len(self.selected_characters) > max_chars:
            QMessageBox.warning(self, "选择错误", f"最多只能选择 {max_chars} 名主角！")
            return

        unique_chars = list(
            map(lambda id: get_character_name(id), self.selected_characters)
        )
        if len(unique_chars) < len(self.selected_characters):
            QMessageBox.warning(self, "选择错误", "不能选择重名角色！")
            return

        super().accept()

    def direct_enter(self):
        """直接进入小说（不选择任何角色）"""
        # 只包含强制角色（如果有）
        self.selected_characters = (
            [self.forced_character_id] if self.forced_character_id else []
        )
        self.accept()
