from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QSizePolicy,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QEvent
from .styles import INPUT_STYLE, BUTTON_STYLES


class CustomTextEdit(QTextEdit):
    """自定义文本编辑框，支持回车发送"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_panel = parent

    def keyPressEvent(self, event):
        """处理按键事件"""
        # 如果是回车键，并且没有按Ctrl或Shift
        if event.key() == Qt.Key_Return and not (
            event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        ):
            if self.parent_panel:
                self.parent_panel.on_send_clicked()
            event.accept()
        else:
            # 其他按键正常处理
            super().keyPressEvent(event)


class InputPanel(QWidget):
    def __init__(
        self,
        send_callback=None,
        clear_callback=None,
        show_clear_button=False,
        threshold=None,
        placeholder="输入消息...",
        tooltip=None,
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
        if tooltip:
            self.setToolTip(tooltip)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 0)

        # 使用自定义的文本编辑框
        self.input_field = CustomTextEdit(self)  # 传入self作为parent_panel
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

        if self.show_clear_button:
            self.clear_button = QPushButton("新对话")
            self.clear_button.setFixedHeight(60)
            button_font = QFont()
            button_font.setPointSize(12)
            self.clear_button.setFont(button_font)
            self.clear_button.setStyleSheet(BUTTON_STYLES["clear"])
            self.clear_button.clicked.connect(self.on_clear_clicked)
            button_layout.addWidget(self.clear_button)

        self.send_button = QPushButton("发送")
        self.send_button.setFixedHeight(60)
        button_font = QFont()
        button_font.setPointSize(12)
        self.send_button.setFont(button_font)
        self.send_button.setStyleSheet(BUTTON_STYLES["send"])
        self.send_button.clicked.connect(self.on_send_clicked)

        button_layout.addStretch()
        button_layout.addWidget(self.send_button)

        layout.addLayout(button_layout)

    def on_send_clicked(self):
        """处理发送按钮点击事件"""
        if not self.send_button.isEnabled():
            return  # 防止重复点击

        text = self.get_input_text()
        if text and self.send_callback:
            self.send_button.setEnabled(False)  # 立即禁用
            self.send_callback(text)
            QTimer.singleShot(100, self.clear_input)

    def on_clear_clicked(self):
        """处理清除按钮点击事件"""
        if self.clear_callback:
            self.clear_callback()

    def get_input_text(self):
        """获取输入框内容"""
        return self.input_field.toPlainText().strip()

    def clear_input(self):
        """清空输入框并设置焦点"""
        self.input_field.clear()
        self.input_field.setFocus()  # 自动聚焦

    def set_send_enabled(self, enabled):
        """设置发送按钮状态"""
        self.send_button.setEnabled(enabled)

    def limit_length(self):
        text = self.input_field.toPlainText()
        if len(text) > self.threshold:
            cursor = self.input_field.textCursor()
            current_pos = cursor.position()

            # 使用块操作减少重绘
            self.input_field.blockSignals(True)
            self.input_field.setPlainText(text[: self.threshold])
            self.input_field.blockSignals(False)

            cursor.setPosition(min(current_pos, self.threshold))
            self.input_field.setTextCursor(cursor)
