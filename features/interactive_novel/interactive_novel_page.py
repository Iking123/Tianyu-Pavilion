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
    QDialogButtonBox,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QCheckBox,
    QTextEdit,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from core.fiction_manager import (
    get_all_fictions,
    save_fiction,
    delete_fiction,
    get_fiction_by_id,
)
from ui.components import GoBackButton
from ui.styles import BUTTON_STYLES
from .fiction_button import FictionButton, FictionStartDialog
from ui.input_panel import CustomTextEdit
from .fiction_page import InteractiveFictionPage
from .world_devastation_page import WorldDevastationPage


class FictionEditDialog(QDialog):
    """小说编辑对话框"""

    def __init__(self, parent=None, names=None, fiction=None):
        super().__init__(parent)
        self.names = names or []
        self.fiction = fiction or {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("编辑小说" if self.fiction else "添加新小说")
        self.setMinimumSize(1380, 1740)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        # === 基础信息 ===
        base_info_label = QLabel("基础信息")
        base_info_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        form_layout.addRow(base_info_label)

        # 名称
        self.name_input = QLineEdit()
        self.name_input.setText(self.fiction.get("name", ""))
        self.name_input.setMaxLength(50)
        self.name_input.setToolTip("至多50个字符")
        form_layout.addRow("小说名称:", self.name_input)

        # 简介
        self.blurb_input = CustomTextEdit(None, 100)
        self.blurb_input.setText(self.fiction.get("blurb", ""))
        self.blurb_input.setMaximumHeight(100)
        form_layout.addRow("简介:", self.blurb_input)

        # === 情节规则 ===
        plot_info_label = QLabel("情节规则")
        plot_info_label.setStyleSheet(
            "font-weight: bold; font-size: 12pt; margin-top: 10px;"
        )
        form_layout.addRow(plot_info_label)

        # 情节描述
        self.plot_input = CustomTextEdit(None, 3500)
        self.plot_input.setPlaceholderText("描述小说的主要情节...")
        self.plot_input.setPlainText(self.fiction.get("plot", ""))
        form_layout.addRow("情节描述:", self.plot_input)

        # 小说规则
        self.task_input = CustomTextEdit(None, 3500)
        self.task_input.setPlaceholderText("描述小说的规则和限制...")
        self.task_input.setPlainText(self.fiction.get("task", ""))
        form_layout.addRow("小说规则:", self.task_input)

        # 注意事项
        self.plot_attention_input = CustomTextEdit(None, 3500)
        self.plot_attention_input.setPlaceholderText("描述小说的注意事项...")
        self.plot_attention_input.setPlainText(self.fiction.get("plot_attention", ""))
        form_layout.addRow("注意事项:", self.plot_attention_input)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        # 验证字段
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "输入错误", "小说名称不能为空！")
            return
        if name in self.names:
            QMessageBox.warning(self, "输入错误", "小说名称不能重复！")
            return

        # 收集数据
        fiction_data = {
            "name": self.name_input.text().strip(),
            "blurb": self.blurb_input.toPlainText().strip(),
            "plot": self.plot_input.toPlainText().strip(),
            "task": self.task_input.toPlainText().strip(),
            "plot_attention": self.plot_attention_input.toPlainText().strip(),
        }

        # 保留ID（如果是编辑）
        if "id" in self.fiction:
            fiction_data["id"] = self.fiction["id"]

        # 保存小说
        if save_fiction(fiction_data):
            super().accept()
        else:
            QMessageBox.warning(self, "保存失败", "无法保存小说信息")


class InteractiveNovelPage(QWidget):
    """交互小说编辑器页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_fiction = None
        self.current_mode = "view"  # view, edit, delete
        self.setup_ui()

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
        toolbar_layout.addWidget(self.back_button)

        # 标题
        title_label = QLabel("交互小说")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 居中布局
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

        # 添加小说按钮
        self.add_btn = QPushButton("➕ 添加新小说")
        self.add_btn.clicked.connect(self.add_new_fiction)
        button_layout.addWidget(self.add_btn)

        # 编辑小说按钮
        self.edit_btn = QPushButton("✏️ 编辑小说")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self.edit_btn.setCheckable(True)
        button_layout.addWidget(self.edit_btn)

        # 删除小说按钮
        self.delete_btn = QPushButton("❌ 删除小说")
        self.delete_btn.clicked.connect(self.toggle_delete_mode)
        self.delete_btn.setCheckable(True)
        button_layout.addWidget(self.delete_btn)

        button_container.setStyleSheet(BUTTON_STYLES["option"])
        main_layout.addWidget(button_container)

        # === 模式提示标签 ===
        self.mode_label = QLabel("点击小说进入")
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

        # === 小说列表区域 ===
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(20, 10, 20, 20)

        # 小说列表标题
        list_title = QLabel("小说列表")
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

        # 小说列表容器
        self.fiction_container = QWidget()
        self.fiction_layout = QVBoxLayout(self.fiction_container)
        self.fiction_layout.setContentsMargins(0, 0, 0, 0)
        self.fiction_layout.setSpacing(5)

        self.scroll_area.setWidget(self.fiction_container)
        list_layout.addWidget(self.scroll_area)

        main_layout.addWidget(list_container, 1)  # 添加并设置拉伸因子为1

        # 加载小说数据
        self.load_fictions()

    def go_back(self):
        """返回主页"""
        if self.parent:
            self.parent.switch_page(0)

    def load_fictions(self):
        """加载并显示小说列表"""
        # 清空现有按钮和拉伸因子
        while self.fiction_layout.count():
            item = self.fiction_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            else:
                # 删除拉伸因子
                self.fiction_layout.removeItem(item)

        fictions = get_all_fictions()

        if not fictions:
            # 如果没有小说，显示提示信息
            no_fic_label = QLabel("没有可用小说，请点击'添加新小说'按钮创建")
            no_fic_label.setStyleSheet(
                """
                color: #999;
                font-size: 12pt;
                padding: 20px;
                text-align: center;
            """
            )
            no_fic_label.setAlignment(Qt.AlignCenter)
            self.fiction_layout.addWidget(no_fic_label)
            return

        self.names = []

        # 为每部小说创建按钮
        for fic in fictions:
            fic_button = FictionButton(fic, self)
            fic_button.clicked.connect(lambda c=fic: self.on_fiction_clicked(c))
            self.fiction_layout.addWidget(fic_button)
            self.names.append(fic.get("name", ""))

        # 添加弹性空间
        self.fiction_layout.addStretch()

    def toggle_edit_mode(self):
        """切换编辑模式"""
        if self.current_mode == "edit":
            self.reset_mode()
            return
        self.current_mode = "edit"
        self.edit_btn.setChecked(True)
        self.delete_btn.setChecked(False)
        self.mode_label.setText("编辑模式：点击要编辑的小说")
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
        self.mode_label.setText("删除模式：点击要删除的小说")
        self.mode_label.setStyleSheet(
            """
            background-color: #f8d7da;
            color: #721c24;
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
        self.mode_label.setText("点击小说进入")
        self.mode_label.setStyleSheet(
            """
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )

    def on_fiction_clicked(self, fiction):
        """当小说被点击时的处理"""
        if self.current_mode == "view":
            # 查看模式：启动小说
            self.start_fiction(fiction)
        elif self.current_mode == "edit":
            # 编辑模式：编辑小说
            if fiction.get("is_hardcoded", False):
                QMessageBox.information(self, "提示", "系统预设小说不可编辑")
            else:
                self.edit_fiction(fiction)
            self.reset_mode()
        elif self.current_mode == "delete":
            # 删除模式：删除小说
            if fiction.get("is_hardcoded", False):
                QMessageBox.information(self, "提示", "系统预设小说不可删除")
            else:
                self.delete_fiction(fiction)
            self.reset_mode()

    def start_fiction(self, fiction):
        """启动小说"""
        dialog = FictionStartDialog(self, fiction["id"])
        if dialog.exec_() == QDialog.Accepted:
            # 获取选择的角色
            selected_characters = dialog.selected_characters

            # 创建小说页面并切换到该页面
            fiction_page = (
                WorldDevastationPage(
                    main_window=self.parent,
                    fiction_id=fiction["id"],
                    character_ids=selected_characters,
                )
                if "default_2" in selected_characters
                else InteractiveFictionPage(
                    main_window=self.parent,
                    fiction_id=fiction["id"],
                    character_ids=selected_characters,
                )
            )

            # 添加到主窗口并切换页面
            if self.parent:
                self.parent.add_page(fiction_page)
                self.parent.switch_to_page(fiction_page)

    def add_new_fiction(self):
        """添加新小说"""
        dialog = FictionEditDialog(self, self.names)
        if dialog.exec_() == QDialog.Accepted:
            self.load_fictions()

    def edit_fiction(self, fiction):
        """编辑小说"""
        dialog = FictionEditDialog(self, self.names, fiction)
        if dialog.exec_() == QDialog.Accepted:
            self.load_fictions()

    def delete_fiction(self, fiction):
        """删除小说"""
        fic_name = fiction.get("name", "未知小说")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除小说 '{fic_name}' 吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if delete_fiction(fiction["id"]):
                self.load_fictions()
            else:
                QMessageBox.warning(self, "删除失败", "无法删除此小说")
