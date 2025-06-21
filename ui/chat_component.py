from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QSplitter,
    QLineEdit,
    QSizePolicy,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer, QObject
from PyQt5.QtGui import QFont, QTextCursor
import datetime
from .message_widget import ChatMessageWidget
from worker import Worker
from config_manager import *
from .styles import *


class ChatComponent(QWidget):
    """聊天功能组件，可嵌入到主应用中"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # 保存主窗口引用
        # 初始化对话历史
        self.conversation_history = [{"role": "system", "content": get_system_prompt()}]
        self.init_ui()
        self.worker = None
        self.timer = None

        # 存储内容
        self.worker_active = False
        self.thinking_widget = None

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 添加搜索工具栏（在标题下方）
        self.search_toolbar = QWidget()
        self.search_toolbar.setFixedHeight(60)
        search_layout = QHBoxLayout(self.search_toolbar)
        search_layout.setContentsMargins(10, 5, 10, 5)

        # 搜索标签
        search_label = QLabel("搜索:")
        search_label.setStyleSheet(
            "font-size: 12pt; font-weight: bold; color: #4A90E2;"
        )

        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索词 (Ctrl+F)")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedHeight(50)
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #4A90E2;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 11pt;
                min-width: 300px;
            }
        """
        )

        # 导航按钮
        self.prev_button = QPushButton("◀ 上一个")
        self.prev_button.setFixedSize(120, 40)
        self.prev_button.setStyleSheet(BUTTON_STYLES["scroll"] + "font-size: 12pt;")

        self.next_button = QPushButton("下一个 ▶")
        self.next_button.setFixedSize(120, 40)
        self.next_button.setStyleSheet(BUTTON_STYLES["scroll"] + "font-size: 12pt;")

        # 匹配计数
        self.match_label = QLabel("0/0")
        self.match_label.setFixedSize(120, 40)
        self.match_label.setAlignment(Qt.AlignCenter)
        self.match_label.setStyleSheet(
            """
            QLabel {
                background-color: #F0F7FF;
                border: 2px solid #4A90E2;
                border-radius: 8px;
                color: #4A90E2;
                font-size: 14pt;
                font-weight: bold;
            }
        """
        )

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.setFixedSize(100, 40)
        close_button.setStyleSheet(BUTTON_STYLES["scroll"] + "font-size: 12pt;")
        close_button.clicked.connect(lambda: self.search_toolbar.setVisible(False))

        # 添加到布局
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 2)  # 增加权重
        search_layout.addWidget(self.prev_button)
        search_layout.addWidget(self.next_button)
        search_layout.addWidget(self.match_label)
        search_layout.addWidget(close_button)

        main_layout.insertWidget(1, self.search_toolbar)
        self.search_toolbar.setVisible(False)

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)

        # 聊天显示区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(15)  # 增加间距

        # 添加初始系统消息
        self.initial_msg = ChatMessageWidget(
            "system", self.conversation_history[0]["content"]
        )
        self.chat_layout.addWidget(self.initial_msg)

        # 创建定时器更新初始系统消息的时间 - 使用更安全的方式
        self.timer = QTimer()
        self.timer.setParent(self)  # 设置父对象以确保正确销毁
        self.timer.timeout.connect(self.safe_update_time)
        self.timer.start(1000)
        self.safe_update_time()  # 初始更新时间

        self.chat_scroll.setWidget(self.chat_container)
        splitter.addWidget(self.chat_scroll)

        # 输入区域
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 15, 0, 0)

        # 用户输入框 - 增大字体
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setMinimumHeight(100)  # 增加高度
        input_font = QFont()
        input_font.setPointSize(12)  # 增大输入字体
        self.input_field.setFont(input_font)
        self.input_field.setStyleSheet(INPUT_STYLE)
        input_layout.addWidget(self.input_field)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 发送按钮 - 增大按钮尺寸
        self.send_button = QPushButton("发送")
        self.send_button.setFixedHeight(60)
        button_font = QFont()
        button_font.setPointSize(12)
        self.send_button.setFont(button_font)
        self.send_button.setStyleSheet(BUTTON_STYLES["send"])
        self.send_button.clicked.connect(self.send_message)

        # 清除按钮 - 增大按钮尺寸
        clear_button = QPushButton("新对话")
        clear_button.setFixedHeight(60)
        clear_button.setFont(button_font)
        clear_button.setStyleSheet(BUTTON_STYLES["clear"])
        clear_button.clicked.connect(self.clear_conversation)

        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)

        input_layout.addLayout(button_layout)
        splitter.addWidget(input_widget)

        # 设置分割器大小
        splitter.setSizes([1200, 400])  # 增加聊天区域高度
        main_layout.addWidget(splitter)

        # 连接滚动到底部按钮
        scroll_button = self.main_window.get_scroll_button()
        scroll_button.clicked.connect(self.scroll_to_bottom)

        # 设置窗口样式
        self.setStyleSheet(APP_STYLESHEET)
        self.init_search()

        self.init_search()

    def get_button_style(self, enabled):
        """根据状态返回按钮样式"""
        if enabled:
            return """
                QPushButton {
                    background-color: #DBEAFE;
                    color: #4D6BFE;
                    border: 1px solid #007AFF;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 0;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: white;
                    color: #4C4C4C;
                    border: 1px solid #000000;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 0;
                }
            """

    def toggle_r1(self):
        """切换 R1 深度思考状态"""
        new_config = get_config()
        new_config["enable_r1"] = not new_config["enable_r1"]
        update_config(new_config)
        self.btn_r1.setChecked(new_config["enable_r1"])
        self.btn_r1.setStyleSheet(self.get_button_style(new_config["enable_r1"]))

    def toggle_tavily(self):
        """切换 Tavily 搜索状态"""
        new_config = get_config()
        new_config["enable_tavily"] = not new_config["enable_tavily"]
        update_config(new_config)
        self.btn_tavily.setChecked(new_config["enable_tavily"])
        self.btn_tavily.setStyleSheet(
            self.get_button_style(new_config["enable_tavily"])
        )

    def safe_update_time(self):
        """安全更新时间显示"""
        try:
            if not self.initial_msg or not isinstance(
                self.initial_msg, ChatMessageWidget
            ):
                return

            self.initial_msg.set_content(get_system_prompt(), "system")
        except Exception as e:
            print(f"更新时间时出错: {e}")
            self.stop_and_clean_timer()

    def stop_and_clean_timer(self):
        """安全停止并清理定时器"""
        try:
            if self.timer and self.timer.isActive():
                self.timer.stop()
            self.timer = None
        except:
            pass

    def send_message(self):
        user_input = self.input_field.toPlainText().strip()
        if not user_input:
            return

        # 禁用发送按钮
        self.send_button.setEnabled(False)
        # 使用主窗口设置状态
        if self.main_window:
            self.main_window.set_status("处理中...")

        # 设置工作状态
        self.worker_active = True

        # 添加用户消息到界面
        self.add_message("user", user_input)

        # 添加用户消息到历史
        self.conversation_history.append({"role": "user", "content": user_input})

        # 清空输入框
        self.input_field.clear()

        # 创建并启动工作线程
        self.worker = Worker(user_input, self.conversation_history, 1)
        self.worker.update_signal.connect(self.add_message)
        # self.worker.status_signal.connect(self.status_label.setText)
        self.worker.search_complete.connect(self.add_search_result)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def add_message(self, role, content):
        """添加消息到聊天界面（修复版）"""
        # 特殊处理：当收到思考/回复分隔符时创建新控件
        if role and role.startswith("assistant"):
            if "🤔 思考开始" in content:
                # 创建思考控件，并设置 is_thinking=True
                self.thinking_widget = self._create_new_message_widget(
                    role, content, is_thinking=True
                )
                self.scroll_to_bottom()
                return
            elif "💬 回复开始" in content:
                # 思考结束，强制渲染思考内容
                if self.thinking_widget:
                    self.thinking_widget.force_render()
                    self.thinking_widget.adjust_height()
                    self.thinking_widget = None  # 清除引用

                # 创建回复控件，is_thinking=False
                self._create_new_message_widget(role, content)
                self.scroll_to_bottom()
                return

        # 如果当前有思考控件，将内容追加到思考控件
        if role and role.startswith("assistant") and self.thinking_widget:
            self.thinking_widget.append_content(content)
            return

        # 如果当前有回复控件，将内容追加到回复控件
        if (
            role
            and role.startswith("assistant")
            and hasattr(self, "current_assistant_widget")
        ):
            self._append_to_existing(content)
            return

        # 其他情况创建新控件
        self._create_new_message_widget(role, content)
        self.scroll_to_bottom()

    def _create_new_message_widget(self, role, content, is_thinking=False):
        """创建新消息控件并设置当前引用
        :param is_thinking: 是否为思考内容
        """
        widget = ChatMessageWidget(role, content, is_thinking=is_thinking)
        self.chat_layout.addWidget(widget)
        if (
            role and role.startswith("assistant") and not is_thinking
        ):  # 思考控件不是当前回复控件
            self.current_assistant_widget = widget
        return widget

    def _append_to_existing(self, content):
        """追加内容到现有控件"""
        # # 同步输出一下未渲染的内容，以免用户嫌卡顿
        # cursor = self.current_assistant_widget.content_browser.textCursor()
        # cursor.movePosition(QTextCursor.End)
        # cursor.insertText(content)
        # self.current_assistant_widget.content_browser.setTextCursor(cursor)
        # 同个鬼步，同步起来好难看哈哈

        # 调用新的append_content方法
        self.current_assistant_widget.append_content(content)

    def add_search_result(self, search_type, result):
        """添加搜索结果到聊天界面"""
        widget = ChatMessageWidget("system", f"网络搜索结果:\n{result}")
        self.chat_layout.addWidget(widget)
        self.scroll_to_bottom()

    def on_worker_finished(self):
        """工作线程完成时调用"""
        self.send_button.setEnabled(True)
        # 使用主窗口设置状态
        if self.main_window:
            self.main_window.set_status("就绪")
        self.worker_active = False

        # 强制渲染最后的内容
        if hasattr(self, "current_assistant_widget"):
            self.current_assistant_widget.force_render()
            self.current_assistant_widget.adjust_height()
            # 清理当前助手消息引用
            del self.current_assistant_widget

        # 如果思考控件还存在（可能思考结束后没有回复内容），强制渲染它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        # 滚动到底部
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_conversation(self):
        """清除对话历史（带确认弹窗）"""
        # 创建确认对话框
        reply = QMessageBox.question(
            self,
            "确认清除",
            "即将清除对话历史并开启新对话，确定执行吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        # 如果用户选择否，则取消操作
        if reply == QMessageBox.No:
            # 使用主窗口设置状态
            if self.main_window:
                self.main_window.set_status("清除操作已取消")
            return

        """清除对话历史（确认后执行）"""
        # 停止当前工作线程
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        # 清除聊天界面
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 重置对话历史
        self.conversation_history = [{"role": "system", "content": get_system_prompt()}]

        # 添加初始系统消息
        self.initial_msg = ChatMessageWidget(
            "system", self.conversation_history[0]["content"]
        )
        self.chat_layout.addWidget(self.initial_msg)

        # 使用主窗口设置状态
        if self.main_window:
            self.main_window.set_status("对话已清除")

    def keyPressEvent(self, event):
        """处理键盘快捷键 - 增强版"""
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
            self.toggle_search_toolbar()
            return
        elif event.key() == Qt.Key_Escape and self.search_toolbar.isVisible():
            self.search_toolbar.setVisible(False)
            self.clear_all_highlights()
            return
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.search_input.hasFocus():
                self.search_next()
                return

        super().keyPressEvent(event)

    def toggle_search_toolbar(self):
        """切换搜索工具栏显示状态"""
        visible = not self.search_toolbar.isVisible()
        self.search_toolbar.setVisible(visible)

        if visible:
            self.search_input.setFocus()
            self.search_input.selectAll()
        else:
            self.clear_all_highlights()

    def init_search(self):
        """初始化搜索功能 - 增强版"""
        # 连接信号
        self.search_input.textChanged.connect(self.initiate_search)
        self.prev_button.clicked.connect(self.search_prev)
        self.next_button.clicked.connect(self.search_next)

        # 搜索状态
        self.search_term = ""
        self.search_matches = []  # 存储所有匹配项 (widget, position, length)
        self.current_match_index = -1
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

    def initiate_search(self, text):
        """初始化搜索（带延迟）"""
        self.search_term = text.strip()
        self.search_timer.start(300)  # 300ms延迟

    def perform_search(self):
        """执行实际搜索"""
        if not self.search_term:
            self.clear_all_highlights()
            self.match_label.setText("0/0")
            return

        # 重置搜索状态
        self.search_matches = []
        self.current_match_index = -1
        self.clear_all_highlights()

        # 在所有消息中搜索
        for i in range(self.chat_layout.count()):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, ChatMessageWidget):
                # 获取消息的纯文本内容
                plain_text = widget.content_browser.toPlainText()

                # 执行搜索（不区分大小写）
                start = 0
                search_term_lower = self.search_term.lower()
                text_lower = plain_text.lower()

                while True:
                    index = text_lower.find(search_term_lower, start)
                    if index == -1:
                        break

                    # 存储匹配项
                    self.search_matches.append((widget, index, len(self.search_term)))
                    start = index + 1

                # 设置高亮
                widget.set_highlight(self.search_term)

        # 更新匹配计数
        total = len(self.search_matches)
        self.match_label.setText(f"0/{total}" if total > 0 else "0/0")

        # 如果有匹配项，跳转到第一个
        if self.search_matches:
            self.current_match_index = 0
            self.highlight_current_match()

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

        # 更新匹配计数
        self.match_label.setText(
            f"{self.current_match_index + 1}/{len(self.search_matches)}"
        )

    def search_next(self):
        """跳转到下一个匹配项"""
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index + 1) % len(
            self.search_matches
        )
        self.highlight_current_match()

    def search_prev(self):
        """跳转到上一个匹配项"""
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index - 1) % len(
            self.search_matches
        )
        self.highlight_current_match()

    def clear_all_highlights(self):
        """清除所有高亮"""
        for i in range(self.chat_layout.count()):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, ChatMessageWidget):
                widget.clear_highlight()

    def scroll_to_widget(self, widget):
        """滚动到指定控件"""
        # 确保小部件可见
        self.chat_scroll.ensureWidgetVisible(widget)

        # 计算位置
        scrollbar = self.chat_scroll.verticalScrollBar()
        widget_y = widget.mapTo(self.chat_container, widget.pos()).y()

        # 滚动到位置
        scrollbar.setValue(widget_y - 100)  # 添加一点偏移

    def cleanup(self):
        """清理资源，当组件被移除时调用"""
        # 停止定时器
        self.stop_and_clean_timer()

        # 停止工作线程
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
