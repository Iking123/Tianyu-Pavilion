from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor
from .qtext_message_widget import MessageWidget


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
        self.scroll_area.setWidgetResizable(True)  # 允许子控件调整大小

        # 设置滚动区域的尺寸策略
        self.scroll_area.setSizePolicy(
            QSizePolicy.Expanding,  # 水平扩展
            QSizePolicy.Expanding,  # 垂直扩展，但子控件决定实际高度
        )

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # +++ 确保垂直滚动条始终可用 +++
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 创建容器
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(10, 0, 10, 0)
        self.container_layout.setSpacing(15)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def add_message(self, widget, auto_scroll=True):
        """添加消息组件"""
        self.container_layout.addWidget(widget)
        if auto_scroll:
            QTimer.singleShot(100, self.scroll_to_bottom)  # 延迟滚动确保布局完成
        return widget

    def add_message_by_role(self, role, content, is_thinking=False, auto_scroll=True):
        """通过角色和内容添加消息"""
        widget = MessageWidget(self, role, content, is_thinking, auto_scroll)
        return self.add_message(widget, auto_scroll)

    def start_assistant_message(self, role, content, is_thinking=False):
        """开始一个新的助手消息"""
        self.current_assistant_widget = self.add_message_by_role(
            role, content, is_thinking
        )
        return self.current_assistant_widget

    def append_to_last_message(self, content):
        """追加到上一条消息"""
        last_message = self.get_last_message()
        if last_message:
            last_message.append_content(content)
            return True
        return False

    def finish_last_message(self):
        """完成上一条消息"""
        last_message = self.get_last_message()
        if last_message:
            last_message.force_render()
            last_message.adjust_height()

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
        self.current_assistant_widget = None
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)  # 从布局中移除
            widget = item.widget()
            if widget:
                if isinstance(widget, MessageWidget) and hasattr(
                    widget, "height_adjust_timer"
                ):
                    widget.height_adjust_timer.stop()
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

    def get_text_position_y(self, widget, position):
        """获取文本位置在容器中的绝对Y坐标"""
        # 获取文本在消息控件中的位置
        cursor = widget.content_browser.textCursor()
        cursor.setPosition(position)
        rect = widget.content_browser.cursorRect(cursor)

        # 转换为容器坐标系
        point_in_widget = widget.content_browser.mapTo(widget, rect.topLeft())
        point_in_container = widget.mapTo(self.container, point_in_widget)
        return point_in_container.y()

    def highlight_current_match(self):
        """高亮当前匹配项并精确滚动到位置"""
        if not self.search_matches or self.current_match_index < 0:
            return

        # 获取当前匹配项
        widget, position, length = self.search_matches[self.current_match_index]

        # 高亮匹配项
        cursor = widget.content_browser.textCursor()
        cursor.setPosition(position)
        cursor.setPosition(position + length, QTextCursor.KeepAnchor)
        widget.content_browser.setTextCursor(cursor)

        # 获取精确的Y坐标
        target_y = self.get_text_position_y(widget, position)

        # 计算视口位置（居中显示）
        viewport_height = self.scroll_area.viewport().height()
        scroll_value = target_y - viewport_height // 2

        # 设置滚动位置（确保在合法范围内）
        scrollbar = self.scroll_area.verticalScrollBar()
        scroll_value = max(0, min(scroll_value, scrollbar.maximum()))
        scrollbar.setValue(scroll_value)

        # 确保光标可见（二次保险）
        widget.content_browser.ensureCursorVisible()

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

    def get_last_message(self):
        """获取最后一条消息"""
        count = self.container_layout.count()
        if count > 0:
            item = self.container_layout.itemAt(count - 1)
            if item and item.widget():
                return item.widget()
        return None

    def remove_last_n_messages(self, n=1):
        """移除最后n条消息"""
        for _ in range(n):
            widget = self.get_last_message()
            if widget:
                self.container_layout.removeWidget(widget)
                widget.deleteLater()
            else:
                break

    def add_search_result(self, result):
        """添加搜索结果到聊天界面"""
        self.add_message_by_role("system", f"网络搜索结果:\n{result}")
