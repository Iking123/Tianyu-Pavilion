from typing import List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QColor

from funcs import resource_path
from .qtext_message_widget import MessageWidget
from .components import ImageWidget, ScrollToBottomButton


class MessageDisplayArea(QWidget):
    """通用的消息显示区域组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.search_matches = []  # 存储搜索匹配项
        self.current_match_index = -1  # 当前匹配索引
        self.current_assistant_widget = None  # 当前助手消息控件

        # 创建滚动到底部按钮
        self.scroll_to_bottom_button = ScrollToBottomButton(
            self, tip="滚动到底部", callback=self.scroll_to_bottom
        )
        self.scroll_to_bottom_button.hide()  # 初始隐藏

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # 允许子控件调整大小

        # 设置滚动区域的尺寸策略
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平扩展
            QSizePolicy.Policy.Expanding,  # 垂直扩展，但子控件决定实际高度
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        # +++ 确保垂直滚动条始终可用 +++
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.slider_upwards = False
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.sliderPressed.connect(self.set_slider_upwards)
        scrollbar.sliderReleased.connect(
            lambda: QTimer.singleShot(
                500, lambda: setattr(self, "slider_upwards", False)
            )
        )

        # 连接滚动条变化信号以更新按钮显示状态
        scrollbar.valueChanged.connect(self.update_scroll_button_visibility)

        # 创建容器
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container_layout.setContentsMargins(10, 0, 10, 0)
        self.container_layout.setSpacing(15)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def format_messages(self):
        """格式化消息列表，方便存储"""
        messages = []
        for i in range(self.container_layout.count()):
            widget = self.container_layout.itemAt(i).widget()
            if (
                isinstance(widget, MessageWidget)
                and hasattr(widget, "raw_role")
                and hasattr(widget, "raw_content")
                and hasattr(widget, "is_thinking")
            ):
                try:
                    messages.append(
                        {
                            "role": widget.raw_role,
                            "content": widget.raw_content,
                            "is_thinking": widget.is_thinking,
                        }
                    )
                except:
                    pass
        return messages

    def resizeEvent(self, event):
        """窗口大小改变时重新定位滚动按钮"""
        super().resizeEvent(event)
        self.position_scroll_button()

    def position_scroll_button(self):
        """将滚动按钮定位到下方中央位置"""
        if hasattr(self, "scroll_to_bottom_button"):
            # 获取滚动区域的几何信息
            scroll_rect = self.scroll_area.geometry()
            button_size = self.scroll_to_bottom_button.size()

            # 计算位置：x为中心，y为下边界向内偏移25像素
            x = (scroll_rect.left() + scroll_rect.right() - button_size.width()) // 2
            y = scroll_rect.bottom() - button_size.height() - 25

            self.scroll_to_bottom_button.move(x, y)
            # 确保按钮在最前面
            self.scroll_to_bottom_button.raise_()

    def at_bottom(self, rigor=False):
        """检查是否在底部（若并非严格模式，则允许小的误差）"""
        scrollbar = self.scroll_area.verticalScrollBar()
        return scrollbar.value() >= scrollbar.maximum() - (0 if rigor else 5)

    def update_scroll_button_visibility(self):
        """更新滚动按钮的显示状态"""
        if not hasattr(self, "scroll_to_bottom_button"):
            return

        if self.at_bottom():
            self.scroll_to_bottom_button.hide()
        else:
            self.scroll_to_bottom_button.show()
            self.position_scroll_button()

    def set_slider_upwards(self):
        if not self.at_bottom(True):
            self.slider_upwards = True

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_Up:
            self.slider_upwards = True
        elif event.key() == Qt.Key.Key_Down:
            self.slider_upwards = False

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.key() == Qt.Key.Key_Up:
            QTimer.singleShot(1500, lambda: setattr(self, "slider_upwards", False))

    def wheelEvent(self, event):
        super().wheelEvent(event)
        delta = event.angleDelta().y()
        if delta > 0:
            self.slider_upwards = True
            QTimer.singleShot(1500, lambda: setattr(self, "slider_upwards", False))
        else:
            self.slider_upwards = False

    def add_widget(
        self, widget: QWidget, auto_scroll=True, alignment=Qt.AlignmentFlag.AlignHCenter
    ):
        """添加控件"""
        self.container_layout.addWidget(widget, alignment=alignment)
        if auto_scroll:
            QTimer.singleShot(300, self.request_scrolling)  # 延迟滚动确保布局完成
        # 延迟更新按钮状态，确保布局完成后再检查
        QTimer.singleShot(350, self.update_scroll_button_visibility)
        return widget

    def add_line(self, auto_scroll=True):
        """添加分割线"""
        line = ImageWidget(resource_path("resources/images/divider.png"), 100)
        return self.add_widget(line, auto_scroll)

    def add_message(self, widget: MessageWidget, auto_scroll=True):
        """添加消息组件"""
        self.container_layout.addWidget(widget)
        if auto_scroll:
            QTimer.singleShot(300, self.request_scrolling)  # 延迟滚动确保布局完成
        # 延迟更新按钮状态，确保布局完成后再检查
        QTimer.singleShot(350, self.update_scroll_button_visibility)
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

        # 清除消息后更新按钮状态
        QTimer.singleShot(100, self.update_scroll_button_visibility)

    def request_scrolling(self):
        """请求滚动到底部，若用户最近往上滚了则不滚动"""
        if self.slider_upwards:
            return
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        # 滚动后立即更新按钮状态
        QTimer.singleShot(100, self.update_scroll_button_visibility)
        self.slider_upwards = False

    def get_all_messages(self) -> List[MessageWidget]:
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
        cursor.setPosition(position + length, QTextCursor.MoveMode.KeepAnchor)
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
        # 将当前匹配项的选中状态清理掉
        widget = self.search_matches[self.current_match_index][0]
        if widget and isinstance(widget, MessageWidget):
            widget.deselect_text()

        self.current_match_index = (self.current_match_index + 1) % len(
            self.search_matches
        )
        self.highlight_current_match()
        return self.current_match_index + 1

    def search_prev(self):
        """跳转到上一个匹配项"""
        if not self.search_matches:
            return
        # 将当前匹配项的选中状态清理掉
        widget = self.search_matches[self.current_match_index][0]
        if widget and isinstance(widget, MessageWidget):
            widget.deselect_text()

        self.current_match_index = (self.current_match_index - 1) % len(
            self.search_matches
        )
        self.highlight_current_match()
        return self.current_match_index + 1

    def get_first_message(self):
        """获取第一条消息"""
        count = self.container_layout.count()
        for i in range(count):
            item = self.container_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageWidget):
                return item.widget()
        return None

    def get_last_widget(self) -> QWidget | None:
        """获取最后一个东西"""
        count = self.container_layout.count()
        for i in range(count - 1, -1, -1):
            item = self.container_layout.itemAt(i)
            if item and item.widget():
                return item.widget()
        return None

    def get_last_message(self):
        """获取最后一条消息"""
        count = self.container_layout.count()
        for i in range(count - 1, -1, -1):
            item = self.container_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageWidget):
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

        # 移除消息后更新按钮状态
        QTimer.singleShot(100, self.update_scroll_button_visibility)

    def add_search_result(self, result):
        """添加搜索结果到聊天界面"""
        self.add_message_by_role("system", f"网络搜索结果:\n{result}")

    def set_all_message_background(self, bg_color, bd_color=None):
        """设置所有消息的背景色。"""
        if bg_color and not bd_color:
            bd_color = QColor(bg_color).darker(110).name()
        messages = self.get_all_messages()
        for message_widget in messages:
            # 调用 MessageWidget 的更新方法
            message_widget.update_style(new_bg_color=bg_color, new_bd_color=bd_color)
