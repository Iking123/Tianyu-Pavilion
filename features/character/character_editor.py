import threading
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
    QFormLayout,
    QDialog,
    QFileDialog,
    QDialogButtonBox,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QScrollArea,
    QProgressDialog,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from core.character_manager import (
    get_all_characters,
    save_character,
    delete_character,
    get_character_by_id,
)
from core.config_manager import get_assist
from ui.components import GoBackButton
from ui.input_panel import CustomTextEdit
from .character_button import *
from ui.styles import BUTTON_STYLES
from core.character_summary import character_summary


class CharacterEditor(QWidget):
    """角色编辑器页面"""

    summary_completed = pyqtSignal(tuple)  # 新增信号：传递(是否成功, 消息)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_character = None
        self.current_mode = "view"  # view, edit, delete, summary
        self.setup_ui()
        self.summary_completed.connect(self.handle_summary_result)  # 连接信号

    def setup_ui(self):
        # 使用垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === 顶部工具栏 ===
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F0F2F5; padding: 10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 返回按钮
        self.back_button = GoBackButton(self, "返回主页")

        # 标题
        title_label = QLabel("角色编辑器")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 这样才能真正居中！
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
        main_layout.addWidget(toolbar)

        # === 操作按钮区域 ===
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(10)

        # 添加角色按钮
        self.add_btn = QPushButton("➕ 添加新角色")
        self.add_btn.clicked.connect(self.add_new_character)
        button_layout.addWidget(self.add_btn)

        # 编辑角色按钮
        self.edit_btn = QPushButton("✏️ 编辑角色")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self.edit_btn.setCheckable(True)
        button_layout.addWidget(self.edit_btn)

        # 删除角色按钮
        self.delete_btn = QPushButton("❌ 删除角色")
        self.delete_btn.clicked.connect(self.toggle_delete_mode)
        self.delete_btn.setCheckable(True)
        button_layout.addWidget(self.delete_btn)

        # 总结角色信息按钮
        self.summary_btn = QPushButton("📝 总结角色信息")
        self.summary_btn.clicked.connect(self.toggle_summary_mode)
        self.summary_btn.setCheckable(True)
        button_layout.addWidget(self.summary_btn)

        button_container.setStyleSheet(BUTTON_STYLES["option"])
        main_layout.addWidget(button_container)

        # === 模式提示标签 ===
        self.mode_label = QLabel("点击角色查看详情")
        self.mode_label.setStyleSheet(
            """
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )
        self.mode_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mode_label)

        # === 角色列表区域 ===
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(20, 10, 20, 20)

        # 角色列表标题
        list_title = QLabel("角色列表")
        list_title.setFont(QFont("Arial", 14, QFont.Bold))
        list_title.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        list_layout.addWidget(list_title)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
        """
        )

        # 角色列表容器
        self.character_container = QWidget()
        self.character_layout = QVBoxLayout(self.character_container)
        self.character_layout.setContentsMargins(0, 0, 0, 0)
        self.character_layout.setSpacing(5)

        self.scroll_area.setWidget(self.character_container)
        list_layout.addWidget(self.scroll_area)

        main_layout.addWidget(list_container, 1)  # 添加并设置拉伸因子为1

        # 加载角色数据
        self.load_characters()

    def go_back(self):
        """返回主页"""
        if self.parent:
            self.parent.switch_page(0)

    def load_characters(self):
        """加载并显示角色列表"""
        # 清空现有按钮和拉伸因子
        while self.character_layout.count():
            item = self.character_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            else:
                # 删除拉伸因子
                self.character_layout.removeItem(item)

        characters = get_all_characters()

        if not characters:
            # 如果没有角色，显示提示信息
            no_char_label = QLabel("没有可用角色，请点击'添加新角色'按钮创建")
            no_char_label.setStyleSheet(
                """
                color: #999;
                font-size: 12pt;
                padding: 20px;
                text-align: center;
            """
            )
            no_char_label.setAlignment(Qt.AlignCenter)
            self.character_layout.addWidget(no_char_label)
            return

        self.names = []

        # 为每个角色创建按钮
        for char in characters:
            char_button = CharacterButton(char, self)
            char_button.clicked.connect(lambda c=char: self.on_character_clicked(c))
            self.character_layout.addWidget(char_button)
            self.names.append(char.get("name", ""))

        # 添加弹性空间
        self.character_layout.addStretch()

    def toggle_edit_mode(self):
        """切换编辑模式"""
        if self.current_mode == "edit":
            self.reset_mode()
            return
        self.current_mode = "edit"
        self.edit_btn.setChecked(True)
        self.delete_btn.setChecked(False)
        self.mode_label.setText("编辑模式：点击要编辑的角色")
        self.mode_label.setStyleSheet(
            """
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )

    def toggle_delete_mode(self):
        """切换删除模式"""
        if self.current_mode == "delete":
            self.reset_mode()
            return
        self.current_mode = "delete"
        self.delete_btn.setChecked(True)
        self.edit_btn.setChecked(False)
        self.mode_label.setText("删除模式：点击要删除的角色")
        self.mode_label.setStyleSheet(
            """
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )

    def toggle_summary_mode(self):
        """切换总结模式"""
        if self.current_mode == "summary":
            self.reset_mode()
            return
        self.current_mode = "summary"
        self.summary_btn.setChecked(True)
        self.edit_btn.setChecked(False)
        self.delete_btn.setChecked(False)
        self.mode_label.setText("总结模式：点击要总结的角色")
        self.mode_label.setStyleSheet(
            """
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )

    def reset_mode(self):
        """重置为查看模式"""
        self.current_mode = "view"
        self.edit_btn.setChecked(False)
        self.delete_btn.setChecked(False)
        self.summary_btn.setChecked(False)  # 新增：重置总结按钮状态
        self.mode_label.setText("点击角色查看详情")
        self.mode_label.setStyleSheet(
            """
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )

    def on_character_clicked(self, character):
        """当角色被点击时的处理"""
        if self.current_mode == "view":
            # 查看模式：显示角色详情
            self.show_character_details(character)
        elif self.current_mode == "edit":
            # 编辑模式：编辑角色
            if character.get("is_hardcoded", False):
                QMessageBox.information(self, "提示", "系统预设角色不可编辑")
            else:
                self.edit_character(character)
            self.reset_mode()
        elif self.current_mode == "delete":
            # 删除模式：删除角色
            if character.get("is_hardcoded", False):
                QMessageBox.information(self, "提示", "系统预设角色不可删除")
            else:
                self.delete_character(character)
            self.reset_mode()
        elif self.current_mode == "summary":  # 新增总结模式处理
            # 总结模式：生成角色摘要
            if character.get("is_hardcoded", False):
                QMessageBox.information(self, "提示", "系统预设角色不可修改")
            else:
                self.summary_character(character)
            self.reset_mode()

    def summary_character(self, character):
        """生成角色摘要并保存"""
        # 创建进度对话框 - 必须在主线程中创建
        self.progress = QProgressDialog(
            f"正在使用 {get_assist()[10:]} 为 {character['name']} 生成摘要...",
            None,
            0,
            0,
            self,  # 没有取消按钮
        )
        self.progress.setWindowTitle("生成角色摘要")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setCancelButton(None)  # 禁用取消按钮
        self.progress.show()

        # 在后台线程中执行摘要生成
        def generate_summary():
            try:
                summary = character_summary(character["id"])
                # 更新角色数据
                character["summary"] = summary
                # 保存角色
                save_character(character)
                self.summary_completed.emit((True, "摘要生成成功"))
            except Exception as e:
                self.summary_completed.emit((False, f"摘要生成失败: {str(e)}"))

        # 启动后台线程
        thread = threading.Thread(target=generate_summary)
        thread.daemon = True
        thread.start()

    def handle_summary_result(self, result):
        """处理摘要生成结果（在主线程中执行）"""
        success, message = result
        self.progress.close()  # 关闭进度对话框

        if success:
            QMessageBox.information(self, "成功", message)
            # 重新加载角色列表
            self.load_characters()
        else:
            QMessageBox.warning(self, "错误", message)

    def show_character_details(self, character):
        """显示角色详情窗口"""
        dialog = CharacterDetailDialog(self, character)
        dialog.exec_()

    def add_new_character(self):
        """添加新角色"""
        dialog = CharacterEditDialog(self, self.names)
        if dialog.exec_() == QDialog.Accepted:
            self.load_characters()

    def edit_character(self, character):
        """编辑角色"""
        dialog = CharacterEditDialog(self, self.names, character)
        if dialog.exec_() == QDialog.Accepted:
            self.load_characters()

    def delete_character(self, character):
        """删除角色"""
        char_name = character.get("name", "未知角色")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除角色 '{char_name}' 吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if delete_character(character["id"]):
                self.load_characters()
            else:
                QMessageBox.warning(self, "删除失败", "无法删除此角色")


class CharacterEditDialog(QDialog):
    """角色编辑对话框"""

    def __init__(self, parent=None, names=None, character=None):
        super().__init__(parent)
        self.names = names or []
        self.character = character or {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("编辑角色" if self.character else "添加新角色")
        self.setMinimumSize(1380, 1740)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)  # 增加垂直间距

        # === 基础信息 ===
        base_info_label = QLabel("基础信息")
        base_info_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        form_layout.addRow(base_info_label)

        # 名称
        self.name_input = QLineEdit()
        self.name_input.setText(self.character.get("name", ""))
        self.name_input.setMaxLength(50)
        self.name_input.setToolTip("至多50个字符")
        form_layout.addRow("角色名称:", self.name_input)

        # 性别
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女", "其他"])
        current_gender = self.character.get("gender", "")
        if current_gender:
            index = self.gender_combo.findText(current_gender)
            if index >= 0:
                self.gender_combo.setCurrentIndex(index)
        form_layout.addRow("性别:", self.gender_combo)

        # 年龄
        self.age_input = QLineEdit()
        self.age_input.setText(self.character.get("age", ""))
        self.age_input.setMaxLength(10)
        self.age_input.setToolTip("至多10个字符")
        form_layout.addRow("年龄:", self.age_input)

        # 身份
        self.identity_input = QLineEdit()
        self.identity_input.setText(self.character.get("identity", ""))
        self.identity_input.setMaxLength(40)
        self.identity_input.setToolTip("至多40个字符")
        form_layout.addRow("身份:", self.identity_input)

        # === 详细信息 ===
        detail_info_label = QLabel("详细信息")
        detail_info_label.setStyleSheet(
            "font-weight: bold; font-size: 12pt; margin-top: 10px;"
        )
        form_layout.addRow(detail_info_label)

        # 性格
        self.personality_input = CustomTextEdit(None, 50)
        self.personality_input.setPlaceholderText("描述角色的性格特点...")
        self.personality_input.setPlainText(self.character.get("personality", ""))
        self.personality_input.setMaximumHeight(100)
        form_layout.addRow("性格:", self.personality_input)

        # 兴趣
        self.hobbies_input = CustomTextEdit(None, 50)
        self.hobbies_input.setPlaceholderText("描述角色的兴趣爱好...")
        self.hobbies_input.setPlainText(self.character.get("hobbies", ""))
        self.hobbies_input.setMaximumHeight(100)
        form_layout.addRow("兴趣:", self.hobbies_input)

        # 背景设定
        self.background_input = CustomTextEdit(None, 10000)
        self.background_input.setPlaceholderText("描述角色的背景故事...")
        self.background_input.setPlainText(self.character.get("background", ""))
        form_layout.addRow("背景设定:", self.background_input)

        # 问候语
        self.greetings_input = CustomTextEdit(None, 150)
        self.greetings_input.setPlaceholderText("填写角色的问候语...")
        self.greetings_input.setPlainText(self.character.get("greetings", ""))
        self.greetings_input.setMaximumHeight(100)
        form_layout.addRow("问候语:", self.greetings_input)

        # === 头像 ===
        avatar_label = QLabel("头像")
        avatar_label.setStyleSheet(
            "font-weight: bold; font-size: 12pt; margin-top: 10px;"
        )
        form_layout.addRow(avatar_label)

        avatar_layout = QHBoxLayout()
        self.avatar_input = QLineEdit()
        self.avatar_input.setText(self.character.get("avatar", ""))
        avatar_layout.addWidget(self.avatar_input)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_avatar)
        avatar_layout.addWidget(self.browse_btn)
        form_layout.addRow("头像路径:", avatar_layout)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择头像", "", "图片文件 (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.avatar_input.setText(file_path)

    def accept(self):
        # 验证字段
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "输入错误", "角色名称不能为空！")
            return

        # 收集数据
        character_data = {
            "name": self.name_input.text().strip(),
            "gender": self.gender_combo.currentText(),
            "age": self.age_input.text().strip(),
            "identity": self.identity_input.text().strip(),
            "personality": self.personality_input.toPlainText().strip(),
            "hobbies": self.hobbies_input.toPlainText().strip(),
            "background": self.background_input.toPlainText().strip(),
            "greetings": self.greetings_input.toPlainText().strip(),
            "avatar": self.avatar_input.text().strip(),
        }

        # 保留ID（如果是编辑）
        if "id" in self.character:
            character_data["id"] = self.character["id"]

        # 保存角色
        if save_character(character_data):
            super().accept()
        else:
            QMessageBox.warning(self, "保存失败", "无法保存角色信息")
