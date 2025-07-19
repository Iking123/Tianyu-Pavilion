from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QSizePolicy,
    QLabel,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QEvent
from .styles import INPUT_STYLE, BUTTON_STYLES


class CustomTextEdit(QTextEdit):
    """自定义文本编辑框，支持限制长度、回车发送和字符计数显示"""

    def __init__(self, parent=None, threshold=None):
        super().__init__(parent)
        self.parent_panel = parent
        self.threshold = threshold
        self.count_label = None  # 用于显示字符计数的标签

        # 初始化字符计数标签
        if threshold:
            self.count_label = QLabel(self)
            self.count_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.count_label.setStyleSheet("color: gray; background: transparent;")
            self.update_count_label()
            self.textChanged.connect(self.limit_length)

    def update_count_label(self):
        """更新字符计数标签的文本和位置"""
        if not self.threshold or not self.count_label:
            return

        # 获取当前文本长度
        current_length = len(self.toPlainText())
        # 设置标签文本（当前长度/最大长度）
        self.count_label.setText(f"{current_length}/{self.threshold}")
        self.count_label.adjustSize()  # 调整标签大小以适应文本

        # 计算标签位置（右下角，考虑滚动条和边距）
        margin = 5  # 边距
        scrollbar_width = (
            self.verticalScrollBar().width()
            if self.verticalScrollBar().isVisible()
            else 0
        )
        label_rect = self.count_label.rect()
        x = self.viewport().width() - label_rect.width() - scrollbar_width - margin
        y = self.viewport().height() - label_rect.height() - margin

        # 移动标签到计算位置
        self.count_label.move(x, y)

    def limit_length(self):
        """限制文本长度并更新计数标签"""
        text = self.toPlainText()
        if len(text) > self.threshold:
            cursor = self.textCursor()
            current_pos = cursor.position()

            self.blockSignals(True)
            self.setPlainText(text[: self.threshold])
            self.blockSignals(False)

            cursor.setPosition(min(current_pos, self.threshold))
            self.setTextCursor(cursor)

        # 更新字符计数标签
        self.update_count_label()

    def resizeEvent(self, event):
        """窗口大小变化时重新定位计数标签"""
        super().resizeEvent(event)
        self.update_count_label()

    def keyPressEvent(self, event):
        """处理按键事件"""
        if (
            event.key() == Qt.Key_Return
            and self.parent_panel
            and not (event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier))
        ):
            self.parent_panel.on_send_clicked()
            event.accept()
        else:
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
        self.input_field = CustomTextEdit(
            self, self.threshold
        )  # 传入self作为parent_panel
        self.input_field.setPlaceholderText(self.placeholder)
        self.input_field.setMinimumHeight(100)
        input_font = QFont()
        input_font.setPointSize(12)
        self.input_field.setFont(input_font)
        self.input_field.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.input_field)

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
