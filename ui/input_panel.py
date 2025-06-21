from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QSizePolicy,
)
from PyQt5.QtGui import QFont
from .styles import INPUT_STYLE, BUTTON_STYLES


class InputPanel(QWidget):
    """可复用的输入面板组件，包含输入框和按钮"""

    def __init__(
        self,
        send_callback=None,
        clear_callback=None,
        show_clear_button=False,
        threshold=None,
        placeholder="输入消息...",
        parent=None,
    ):
        super().__init__(parent)
        self.send_callback = send_callback
        self.clear_callback = clear_callback
        self.show_clear_button = (
            show_clear_button  # 我们只在聊天页面中显示清除按钮，其他页面不显示
        )
        self.threshold = threshold
        self.placeholder = placeholder
        self.init_ui()

    def init_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 0)

        # 用户输入框
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(self.placeholder)
        self.input_field.setMinimumHeight(100)
        input_font = QFont()
        input_font.setPointSize(12)
        self.input_field.setFont(input_font)
        self.input_field.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.input_field)
        if self.threshold:
            self.input_field.textChanged.connect(self.limit_length)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 清除按钮 - 新增条件显示
        if self.show_clear_button:
            self.clear_button = QPushButton("新对话")
            self.clear_button.setFixedHeight(60)
            button_font = QFont()
            button_font.setPointSize(12)
            self.clear_button.setFont(button_font)
            self.clear_button.setStyleSheet(BUTTON_STYLES["clear"])
            self.clear_button.clicked.connect(self.on_clear_clicked)
            button_layout.addWidget(self.clear_button)

        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedHeight(60)
        button_font = QFont()
        button_font.setPointSize(12)
        self.send_button.setFont(button_font)
        self.send_button.setStyleSheet(BUTTON_STYLES["send"])
        self.send_button.clicked.connect(self.on_send_clicked)

        # 添加伸缩空间（当没有清除按钮时保持布局平衡）
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)

        layout.addLayout(button_layout)

    def on_send_clicked(self):
        """处理发送按钮点击事件"""
        if self.send_callback:
            self.send_callback(self.get_input_text())
            self.clear_input()

    def on_clear_clicked(self):
        """处理清除按钮点击事件"""
        if self.clear_callback:
            self.clear_callback()

    def get_input_text(self):
        """获取输入框内容"""
        return self.input_field.toPlainText().strip()

    def clear_input(self):
        """清空输入框"""
        self.input_field.clear()

    def set_send_enabled(self, enabled):
        """设置发送按钮状态"""
        self.send_button.setEnabled(enabled)

    def limit_length(self):
        if len(self.input_field.toPlainText()) > self.threshold:
            # 保留前threshold个字符
            cursor = self.input_field.textCursor()
            current_pos = cursor.position()  # 保存当前光标位置
            self.input_field.setPlainText(
                self.input_field.toPlainText()[: self.threshold]
            )
            # 恢复光标位置（不超过新长度）
            cursor.setPosition(min(current_pos, self.threshold))
            self.input_field.setTextCursor(cursor)
