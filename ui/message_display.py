# message_display.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from .message_widget import MessageWidget


class MessageDisplayArea(QWidget):
    """通用的消息显示区域组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.search_matches = []  # 存储搜索匹配项
        self.current_match_index = -1  # 当前匹配索引
        self.current_assistant_widget = None  # 当前助手消息控件

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 创建容器
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(15)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def add_message(self, widget):
        """添加消息组件"""
        self.container_layout.addWidget(widget)
        self.scroll_to_bottom()
        return widget

    def add_message_by_role(self, role, content, is_thinking=False):
        """通过角色和内容添加消息"""
        widget = MessageWidget(role, content, is_thinking)
        return self.add_message(widget)

    def start_assistant_message(self, role, content):
        """开始一个新的助手消息"""
        self.current_assistant_widget = self.add_message_by_role(role, content)
        return self.current_assistant_widget

    def append_to_assistant_message(self, content):
        """追加内容到当前助手消息"""
        if self.current_assistant_widget:
            self.current_assistant_widget.append_content(content)
            return True
        return False

    def finish_assistant_message(self):
        """完成当前助手消息"""
        if self.current_assistant_widget:
            self.current_assistant_widget.force_render()
            self.current_assistant_widget.adjust_height()
            self.current_assistant_widget = None

    def clear_messages(self):
        """清除所有消息"""
        self.current_assistant_widget = None  # 清除当前助手引用
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def get_all_messages(self):
        """获取所有消息控件"""
        messages = []
        for i in range(self.container_layout.count()):
            widget = self.container_layout.itemAt(i).widget()
            if isinstance(widget, MessageWidget):
                messages.append(widget)
        return messages

    def perform_search(self, search_term):
        """执行搜索并返回匹配项"""
        self.search_matches = []
        self.current_match_index = -1

        if not search_term:
            self.clear_all_highlights()
            return 0

        # 在所有消息中搜索
        messages = self.get_all_messages()
        for widget in messages:
            # 获取消息的纯文本内容
            plain_text = widget.content_browser.toPlainText()

            # 执行搜索（不区分大小写）
            start = 0
            search_term_lower = search_term.lower()
            text_lower = plain_text.lower()

            while True:
                index = text_lower.find(search_term_lower, start)
                if index == -1:
                    break

                # 存储匹配项
                self.search_matches.append((widget, index, len(search_term)))
                start = index + 1

            # 设置高亮
            widget.set_highlight(search_term)

        return len(self.search_matches)

    def highlight_current_match(self):
        """高亮当前匹配项并滚动到位置"""
        if not self.search_matches or self.current_match_index < 0:
            return

        # 获取当前匹配项
        widget, position, length = self.search_matches[self.current_match_index]

        # 滚动到该消息
        self.scroll_to_widget(widget)

        # 高亮匹配项
        cursor = widget.content_browser.textCursor()
        cursor.setPosition(position)
        cursor.setPosition(position + length, QTextCursor.KeepAnchor)
        widget.content_browser.setTextCursor(cursor)
        widget.content_browser.ensureCursorVisible()

    def scroll_to_widget(self, widget):
        """滚动到指定控件"""
        # 确保小部件可见
        self.scroll_area.ensureWidgetVisible(widget)

        # 计算位置
        scrollbar = self.scroll_area.verticalScrollBar()
        widget_y = widget.mapTo(self.container, widget.pos()).y()

        # 滚动到位置
        scrollbar.setValue(widget_y - 100)  # 添加一点偏移

    def clear_all_highlights(self):
        """清除所有高亮"""
        messages = self.get_all_messages()
        for widget in messages:
            widget.clear_highlight()

    def search_next(self):
        """跳转到下一个匹配项"""
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index + 1) % len(
            self.search_matches
        )
        self.highlight_current_match()
        return self.current_match_index + 1

    def search_prev(self):
        """跳转到上一个匹配项"""
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index - 1) % len(
            self.search_matches
        )
        self.highlight_current_match()
        return self.current_match_index + 1
