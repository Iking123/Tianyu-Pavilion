import re
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QSizePolicy
from PyQt5.QtGui import QFont, QTextCursor, QDesktopServices, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QUrl, QTimer
import time
from . import markdown_utils  # 导入Markdown工具
from .styles import *  # 导入样式
from core.config_manager import get_config
from funcs import *
from .highlight import *


class MessageWidget(QWidget):
    """通用的消息控件"""

    def __init__(
        self, role, content, is_thinking=False, parent=None
    ):  # 添加 is_thinking 参数
        super().__init__(parent)
        self.is_thinking = is_thinking  # 标识是否是思考内容
        # 设置大小策略 - 水平扩展，垂直固定
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setAlignment(Qt.AlignTop)  # 顶部对齐

        # 角色标签
        role_name = ""
        match role:
            case "user":
                role_name = "你"
            case "assistant":
                role_name = f"DeepSeek-R1{"（思考）" if is_thinking else ""}"
            case "assistant-v3":
                role_name = "DeepSeek-V3"
                role = "assistant"
            case "system":
                role_name = "系统"
        role_label = QLabel(role_name)
        role_font = QFont()
        role_font.setBold(True)
        role_font.setPointSize(12)
        role_label.setFont(role_font)
        role_label.setStyleSheet(MESSAGE_STYLES[role])
        layout.addWidget(role_label)

        # 使用 QTextBrowser 替代 QTextEdit - 提供更好的 HTML 支持
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        self.content_browser.setOpenLinks(False)  # 禁止打开内部链接
        self.content_browser.anchorClicked.connect(self.handle_link_click)

        # 禁用所有滚动条
        self.content_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置大小策略 - 水平扩展，垂直根据内容调整
        self.content_browser.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.MinimumExpanding
        )

        # 设置最小宽度
        self.content_browser.setMinimumWidth(600)

        # 设置内容 - 使用 Markdown 渲染
        self.set_content(content, role)

        # 设置基础样式
        self.content_browser.setStyleSheet(self.get_base_style(role))

        # 连接高度调整信号
        self.content_browser.document().documentLayout().documentSizeChanged.connect(
            self.request_height_adjustment
        )

        layout.addWidget(self.content_browser)
        self.setLayout(layout)

        # 创建高亮器
        self.highlighter = SearchHighlighter(self.content_browser.document())

        # 存储内容
        self.raw_content = content
        self.role = role
        self.last_render_time = 0
        self.render_threshold = get_config("render_threshold")
        self.search_term = ""

        # 添加高度调整计时器
        self.height_adjust_timer = QTimer()
        self.height_adjust_timer.setSingleShot(True)
        self.height_adjust_timer.timeout.connect(self.adjust_height)

        # 初始渲染
        self.render_content()

    def render_content(self):
        """渲染内容"""
        if self.role == "assistant":
            # 使用工具函数渲染Markdown
            html_content = markdown_utils.markdown_to_html(self.raw_content)
            self.content_browser.setHtml(html_content)

            # 关键修改：根据是否为思考内容设置样式
            if self.is_thinking:
                self.content_browser.document().setDefaultStyleSheet(THINKING_STYLE)
            else:
                self.content_browser.document().setDefaultStyleSheet(ASSIST_STYLE)
        else:
            self.content_browser.setPlainText(self.raw_content)

    def append_content(self, new_content):
        """追加新内容并重新渲染"""
        self.raw_content += new_content

        # 更新最后接收内容的时间
        self.last_content_time = time.time()

        # 节流控制
        current_time = time.time()
        if current_time - self.last_render_time > self.render_threshold:
            self.render_content()
            self.last_render_time = current_time

    def force_render(self):
        """强制立即渲染内容，忽略节流限制"""
        self.render_content()
        self.last_render_time = time.time()  # 重置计时器

    def get_base_style(self, role):
        """获取基础样式"""
        # 如果是思考内容，使用黄色背景
        if self.is_thinking:
            return """
                QTextBrowser {
                    background-color: #FFFFF0;
                    border: 1px solid #E0D5B0;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 11pt;
                }
            """

        # 否则使用常规样式
        if role == "assistant":
            return """
                QTextBrowser {
                    background-color: #F0F7FF;
                    border: 1px solid #C0D5E0;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 11pt;
                }
            """
        elif role == "user":
            return """
                QTextBrowser {
                    background-color: #E6F7ED;
                    border: 1px solid #C0E0D0;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 11pt;
                }
            """
        elif role == "system":
            return """
                QTextBrowser {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 12px;
                    color: #666;
                    font-style: italic;
                    font-size: 11pt;
                }
            """
        else:
            return """
                QTextBrowser {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 12px;
                    color: #666;
                    font-size: 11pt;
                }
        """

    def set_content(self, content, role):
        """设置内容并渲染"""
        # 如果是助手消息，使用 Markdown 渲染
        if role == "assistant":
            # 如果是思考内容，使用思考样式
            if self.is_thinking:
                html_content = markdown_utils.markdown_to_html(content)
                self.content_browser.setHtml(html_content)
                self.content_browser.document().setDefaultStyleSheet(THINKING_STYLE)
            else:
                html_content = markdown_utils.markdown_to_html(content)
                self.content_browser.setHtml(html_content)
                self.content_browser.document().setDefaultStyleSheet(ASSIST_STYLE)
        else:
            self.content_browser.setPlainText(content)

    def request_height_adjustment(self):
        """请求高度调整（防抖）"""
        # 停止之前的计时器（如果存在）
        if self.height_adjust_timer.isActive():
            self.height_adjust_timer.stop()

        # 启动新的计时器（延迟200毫秒）
        self.height_adjust_timer.start(200)

    def adjust_height(self):
        """根据内容自动调整高度，同时保持宽度灵活性"""
        # 保存当前滚动位置
        scrollbar = self.content_browser.verticalScrollBar()
        old_position = scrollbar.value()

        doc = self.content_browser.document()
        doc_height = doc.size().height()
        new_height = int(doc_height) + 30  # 30px缓冲

        # 设置最小高度而不是固定高度
        self.content_browser.setMinimumHeight(new_height)

        # 更新整个控件的大小提示
        self.updateGeometry()

        try:
            # 恢复滚动位置
            QTimer.singleShot(0, lambda: scrollbar.setValue(old_position))
        except Exception:
            pass

    def handle_link_click(self, url):
        """处理链接点击 - 在外部浏览器打开"""
        QDesktopServices.openUrl(url)

    def find_text(self, search_term):
        """在消息内容中查找文本并返回匹配位置"""
        matches = []

        # 获取纯文本内容
        plain_text = self.content_browser.toPlainText()

        # 执行搜索（忽略大小写）
        start = 0
        while True:
            index = case_insensitive_find(plain_text, search_term, start)
            if index == -1:
                break
            matches.append(index)
            start = index + len(search_term)

        return matches

    def set_highlight(self, search_term):
        """设置高亮搜索词"""
        self.highlighter.set_search_term(search_term)

    def clear_highlight(self):
        """清除高亮"""
        self.highlighter.set_search_term("")
