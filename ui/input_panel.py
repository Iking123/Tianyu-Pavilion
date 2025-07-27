from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QSizePolicy,
    QLabel,
    QFrame,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QEvent
from .styles import INPUT_STYLE, BUTTON_STYLES
from ui.components import SendButton


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
        self.show_clear_button = show_clear_button
        self.threshold = threshold
        self.placeholder = placeholder
        self.button_row = None  # 底部按钮行布局

        # 创建容器样式
        self.container = QFrame()
        self.container.setObjectName("inputContainer")
        self.container.setStyleSheet(self._get_container_style())

        self.init_ui()
        if tooltip:
            self.setToolTip(tooltip)

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.addWidget(self.container)

        # 容器内部布局
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 使用自定义的文本编辑框
        self.input_field = CustomTextEdit(self, self.threshold)
        self.input_field.setPlaceholderText(self.placeholder)
        self.input_field.setMinimumHeight(100)
        input_font = QFont()
        input_font.setPointSize(12)
        self.input_field.setFont(input_font)

        # 移除输入框边框（由容器提供）
        input_style = INPUT_STYLE.replace("border: 1px solid #CCCCCC;", "border: none;")
        self.input_field.setStyleSheet(input_style)
        container_layout.addWidget(self.input_field)

        # 不要有分割线！
        # separator = QFrame()
        # separator.setFrameShape(QFrame.HLine)
        # separator.setStyleSheet("background-color: #E0E0E0;")
        # separator.setFixedHeight(1)
        # container_layout.addWidget(separator)

        # 创建底部按钮行
        self.button_row = QWidget()
        button_row_layout = QHBoxLayout(self.button_row)
        button_row_layout.setContentsMargins(10, 10, 10, 10)
        button_row_layout.setSpacing(10)

        # 添加清除按钮（如果有）
        if self.show_clear_button:
            self.clear_button = QPushButton("新对话")
            self.clear_button.setFixedHeight(40)
            button_font = QFont()
            button_font.setPointSize(11)
            self.clear_button.setFont(button_font)
            self.clear_button.setStyleSheet(BUTTON_STYLES["clear"])
            self.clear_button.clicked.connect(self.on_clear_clicked)
            button_row_layout.addWidget(self.clear_button)

        # 添加拉伸空间（按钮将居右）
        button_row_layout.addStretch()

        # 发送按钮
        # self.send_button = QPushButton("发送")
        # self.send_button.setFixedHeight(40)
        # button_font = QFont()
        # button_font.setPointSize(11)
        # self.send_button.setFont(button_font)
        # self.send_button.setStyleSheet(BUTTON_STYLES["send"])
        # self.send_button.clicked.connect(self.on_send_clicked)
        self.send_button = SendButton(self)
        button_row_layout.addWidget(self.send_button)

        container_layout.addWidget(self.button_row)

    def _get_container_style(self):
        """从输入框样式提取容器样式"""
        # 提取背景色
        bg_color = "#FFFFFF"  # 默认白色
        if "background-color:" in INPUT_STYLE:
            start = INPUT_STYLE.find("background-color:") + len("background-color:")
            end = INPUT_STYLE.find(";", start)
            if end != -1:
                bg_color = INPUT_STYLE[start:end].strip()

        # 提取圆角
        radius = "8px"  # 默认圆角
        if "border-radius:" in INPUT_STYLE:
            start = INPUT_STYLE.find("border-radius:") + len("border-radius:")
            end = INPUT_STYLE.find(";", start)
            if end != -1:
                radius = INPUT_STYLE[start:end].strip()

        # 提取边框
        border = "1px solid #CCCCCC"  # 默认边框
        if "border:" in INPUT_STYLE:
            start = INPUT_STYLE.find("border:") + len("border:")
            end = INPUT_STYLE.find(";", start)
            if end != -1:
                border = INPUT_STYLE[start:end].strip()

        # 创建容器样式
        return f"""
            QFrame#inputContainer {{
                background-color: {bg_color};
                border: {border};
                border-radius: {radius};
            }}
        """

    def add_button(self, text, callback, style="option"):
        """向按钮行添加自定义按钮"""
        if not self.button_row:
            return

        button = QPushButton(text)
        button.setFixedHeight(40)
        button_font = QFont()
        button_font.setPointSize(11)
        button.setFont(button_font)

        # 应用样式
        if style in BUTTON_STYLES:
            button.setStyleSheet(BUTTON_STYLES[style])
        else:
            button.setStyleSheet(BUTTON_STYLES["option"])

        button.clicked.connect(callback)

        # 在清除按钮后添加新按钮
        layout = self.button_row.layout()
        if self.show_clear_button and layout.indexOf(self.clear_button) >= 0:
            # 在清除按钮后添加
            layout.insertWidget(layout.indexOf(self.clear_button) + 1, button)
        else:
            # 在清除按钮位置添加（如果没有清除按钮）
            layout.insertWidget(0, button)

        return button

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
        self.send_button.setEnabled(True)  # 重新启用发送按钮

    def set_send_enabled(self, enabled):
        """设置发送按钮状态"""
        self.send_button.setEnabled(enabled)
