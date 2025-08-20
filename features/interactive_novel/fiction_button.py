from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
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
from PyQt6.QtGui import QFont, QColor
from core.character_manager import get_all_characters, get_character_name
from core.config_manager import get_assist
from core.fiction_manager import get_fiction_by_id
from features.character.character_button import SelectableCharacterButton
from ui.card_widget import CardWidget


class FictionButton(CardWidget):
    """小说按钮，显示小说信息"""

    def __init__(self, fiction_data, parent=None):
        title = fiction_data.get("name", "未知小说") or "未知小说"
        description = fiction_data.get("blurb", "无简介") or "无简介"
        icon_path = fiction_data.get("avatar")
        super().__init__(title, description, icon_path, 100, parent)
        self.fiction_data = fiction_data


class FictionStartDialog(QDialog):
    """小说启动对话框，用于选择角色"""

    def __init__(self, parent=None, fiction_id=None, name=None):
        super().__init__(parent)
        self.fiction_id = fiction_id
        self.name = name
        self.selected_characters = []
        self.forced_character_id = None
        self.characters_num_level = 3  # 默认3级（最多3人）
        self.characters_minimun = 1  # 默认至少要1名角色

        # 获取小说信息（如果有强制角色）
        if self.fiction_id:
            fiction = get_fiction_by_id(self.fiction_id)
            if fiction:
                self.forced_character_id = fiction.get("forced_character_id")
                if self.forced_character_id:
                    self.selected_characters.append(self.forced_character_id)
                self.characters_num_level = fiction.get("characters_num_level", 3)
                self.characters_minimun = fiction.get("characters_minimun", False)

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("选择角色")
        self.setMinimumSize(1380, 1720)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel(f"请选择参与《{self.name}》的角色")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 角色数量提示
        max_characters = self.get_max_characters()
        subtitle_text = f"本小说的开局将由 <b>{get_assist(True)}</b> 撰写<br>请选择"
        if max_characters == self.characters_minimun:
            subtitle_text += f" <b>{max_characters}</b> 名主角"
        else:
            subtitle_text += f"至多 <b>{max_characters}</b> 名主角，"
            subtitle_text += (
                f"至少 <b>{self.characters_minimun}</b> 名主角"
                if self.characters_minimun
                else "可不选"
            )
        if self.forced_character_id:
            subtitle_text += " （含强制角色）"

        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #7F8C8D; margin-bottom: 10px;")
        subtitle_label.setTextFormat(Qt.TextFormat.RichText)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        # 角色选择区域（使用滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        button_layout.addStretch(1)  # 添加伸缩因子
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.btn_accept = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.btn_accept.setVisible(
            len(self.selected_characters) >= self.characters_minimun
        )
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
            forced_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
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
            self.btn_accept.setVisible(
                len(self.selected_characters) >= self.characters_minimun
            )
        else:
            # 检查是否超过最大数量
            max_chars = self.get_max_characters()
            forced_count = 1 if self.forced_character_id else 0
            if len(self.selected_characters) + forced_count >= max_chars:
                QMessageBox.warning(
                    self, "选择限制", f"最多只能选择 {max_chars} 名角色！"
                )
                return

            # 若当前小说为4级角色数（至多10人），则检查该角色是否有简介
            if self.characters_num_level == 4 and not character.get("summary", None):
                name = character.get("name", "该角色")
                QMessageBox.warning(
                    self,
                    "选择限制",
                    "• 由于本小说至多容许10名主角进入，为节约token，仅能选有简介的角色！\n"
                    f"• 如果想用 {name} ，请在角色编辑器页面为 {name} 添加简介！",
                )
                return

            # 添加选择
            self.selected_characters.append(character_id)
            button.set_selected(True)  # 更新按钮状态
            self.btn_accept.setVisible(
                len(self.selected_characters) >= self.characters_minimun
            )

    def accept(self):
        max_chars = self.get_max_characters()

        if len(self.selected_characters) < self.characters_minimun:
            QMessageBox.warning(
                self, "选择错误", f"必须选择至少{self.characters_minimun}名主角！"
            )
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
