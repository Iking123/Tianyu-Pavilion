from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QSizePolicy
from PyQt5.QtGui import QFont, QTextCursor, QDesktopServices, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtNetwork import QNetworkReply
import time
from . import qtext_markdown_utils  # 导入Markdown工具
from .styles import *  # 导入样式
from core.config_manager import get_config
from funcs import *
from .highlight import *
from core.character_manager import get_character_by_id
from funcs import resource_path


@delay_update
class MessageWidget(QWidget):
    """通用的消息控件"""

    option_clicked = pyqtSignal(str)  # 定义点击信号，传递选项内容

    def __init__(self, parent, role, content, is_thinking=False, auto_scroll=True):
        super().__init__(parent)
        self._adjusting = False
        self.message_display = parent
        self.is_thinking = is_thinking  # 标识是否是思考内容
        self.auto_scroll = auto_scroll
        # 设置大小策略 - 水平扩展，垂直固定
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setAlignment(Qt.AlignTop)  # 顶部对齐

        # 使用 QTextBrowser 替代 QTextEdit - 提供更好的 HTML 支持
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        self.content_browser.setOpenLinks(False)  # 禁止打开内部链接
        self.content_browser.anchorClicked.connect(self.handle_link_click)

        # 禁用所有滚动条
        self.content_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置大小策略
        self.content_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 设置最小宽度和固定高度
        self.content_browser.setMinimumWidth(600)
        self.content_browser.setFixedHeight(0)

        # 设置初始内容
        self.set_content(content)

        # 为选项消息添加点击事件支持
        if role == "option":
            # 设置鼠标悬停样式
            self.setCursor(Qt.PointingHandCursor)
            self.content_browser.setCursor(Qt.PointingHandCursor)
            self.content_browser.viewport().setCursor(Qt.PointingHandCursor)
            # 安装事件过滤器以捕获点击
            self.content_browser.viewport().installEventFilter(self)
        # 如果不是选项，也不是旁白（即role不为空），则考虑角色标签与头像：
        elif role:
            # 创建头像容器
            avatar_widget = QWidget()
            avatar_layout = QHBoxLayout(avatar_widget)
            avatar_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            avatar_layout.setContentsMargins(0, 0, 10, 0)  # 右边距10px

            # 尝试获取角色头像
            character = None
            if role.startswith("character_"):
                character_id = role[10:]
                character = get_character_by_id(character_id)

            # 如果有角色头像，或者是助手
            if character and character.get("avatar") or role.startswith("assistant_"):
                avatar_label = QLabel()
                if role.startswith("assistant_DeepSeek"):
                    avatar_path = "resources/images/deepseek.png"
                elif role.startswith("assistant_豆包"):
                    avatar_path = "resources/images/doubao.png"
                elif role.startswith("assistant"):
                    avatar_path = ""
                else:
                    avatar_path = character["avatar"]

                # 加载头像
                avatar_path = resource_path(avatar_path)
                if os.path.exists(avatar_path):
                    pixmap = QPixmap(avatar_path)
                    # 缩放头像
                    pixmap = pixmap.scaled(
                        60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    avatar_label.setPixmap(pixmap)
                    avatar_layout.addWidget(avatar_label)

            # 角色标签
            role_name = ""
            if role.startswith("assistant_"):
                role_name = role[10:]
                role = "assistant"
            elif role.startswith("character_"):
                role_name = character.get("name", role[10:]) if character else role[10:]
                role = "assistant"  # 将character视为assistant类型
            else:
                match role:
                    case "user":
                        role_name = "你"
                    case "system":
                        role_name = "系统"
            if is_thinking:
                role_name += "（思考）"

            role_label = QLabel(role_name)
            role_font = QFont()
            role_font.setBold(True)
            role_font.setPointSize(12)
            role_label.setFont(role_font)
            role_label.setStyleSheet(MESSAGE_STYLES[role])

            # 将角色名称添加到头像容器
            avatar_layout.addWidget(role_label)

            # 将头像容器添加到主布局
            layout.addWidget(avatar_widget)

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
        self.search_term = ""

        # 添加高度调整计时器
        self.height_adjust_timer = QTimer()
        self.height_adjust_timer.setSingleShot(True)
        self.height_adjust_timer.timeout.connect(self.adjust_height)

        # 初始渲染
        self.render_content()

        # 设置基础样式（使用集中管理的样式）
        self.apply_base_style(role, is_thinking)

        # 外部链接开启
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setOpenLinks(True)

    def eventFilter(self, obj, event):
        """为了选项消息的事件过滤器方法"""
        if (
            hasattr(self, "role")
            and self.role == "option"
            and obj is self.content_browser.viewport()
        ):
            if (
                event.type() == QEvent.MouseButtonRelease
                and event.button() == Qt.LeftButton
            ):
                # 触发选项点击信号
                self.option_clicked.emit(self.raw_content)
                return True
        return super().eventFilter(obj, event)

    def on_request_finished(self, reply):
        url = reply.url().toString()
        if "latex.codecogs.com" in url:
            error = reply.error()
            if error == QNetworkReply.NoError:
                print(f"公式图片加载成功: {url}")
            else:
                print(f"公式图片加载失败: {url}, 错误: {reply.errorString()}")

    def render_content(self):
        """渲染内容"""
        # 如果是助手/旁白消息，就渲染
        if self.role == "assistant" or self.role == "":
            # 使用工具函数渲染Markdown
            html_content = qtext_markdown_utils.markdown_to_html(self.raw_content)
            # print(f"渲染的HTML内容: {html_content}")
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
        # 先加一下，以免用户嫌卡顿，但不一定现在渲染
        cursor = self.content_browser.textCursor()
        cursor.movePosition(cursor.End)
        html_content = qtext_markdown_utils.markdown_to_html(new_content).strip()
        # print(repr(html_content))
        cursor.insertHtml(html_content)  # 直接将new_content转换后插入HTML片段
        self.content_browser.setTextCursor(cursor)

        # 节流控制
        current_time = time.time()
        char_count = len(self.raw_content)
        dynamic_threshold = max(
            0.5, 0.05 + char_count / 100000
        )  # 初始50ms节流，每100字符增加1ms节流时间
        if current_time - self.last_render_time > dynamic_threshold:
            self.render_content()
            self.last_render_time = current_time

    def force_render(self):
        """强制立即渲染内容，忽略节流限制"""
        self.render_content()
        # 强制刷新页面，重新加载图片
        self.content_browser.reload()
        self.last_render_time = time.time()  # 重置计时器

    def apply_base_style(self, role, is_thinking):
        """应用基础样式"""
        # 确定样式键
        if role == "assistant":
            style_key = "assistant_thinking" if is_thinking else "assistant_regular"
        elif role == "user":
            style_key = "user"
        elif role == "system":
            style_key = "system"
        elif role == "option":  # 新增选项样式
            style_key = "option"
        else:
            style_key = "default"

        # 应用样式 - 添加数学公式支持
        base_style = (
            MESSAGE_BASE_STYLES[style_key]
            + """
            img {
                display: inline-block !important;  /* 行内公式强制显示 */
                max-width: 100% !important;
                height: auto !important;
                vertical-align: middle !important;
                background-color: white !important;
                border: 1px solid red !important;  /* 临时添加红色边框，验证是否加载 */
            }
        """
        )
        self.content_browser.setStyleSheet(base_style)

    def set_content(self, content):
        """单纯的设置内容"""
        self.content_browser.setPlainText(content)

    def request_height_adjustment(self):
        """请求高度调整（防抖）"""
        # 停止之前的计时器（如果存在）
        self.__del__()

        # 启动新的计时器（延迟200毫秒）
        self.height_adjust_timer.start(200)

        self.adjust_height()

    def __del__(self):
        """确保定时器在对象销毁时停止"""
        if hasattr(self, "height_adjust_timer") and self.height_adjust_timer.isActive():
            self.height_adjust_timer.stop()

    def adjust_height(self):
        """根据内容自动调整高度，增加安全检查"""
        if (
            not hasattr(self, "message_display")
            or not self.message_display
            or self._adjusting
        ):
            return
        self._adjusting = True

        try:
            scroll_area = self.message_display.scroll_area
            if not scroll_area:
                return

            scrollbar = scroll_area.verticalScrollBar()
            if not scrollbar:
                return

            at_bottom = (
                True
                if self.auto_scroll and scrollbar.value() == scrollbar.maximum()
                else False
            )

            doc = self.content_browser.document()
            if not doc:
                return

            doc_height = doc.size().height()
            new_height = int(doc_height) + 30  # 30px缓冲

            # 仅当需要更新时更新
            if self.content_browser.height() < new_height:
                self.content_browser.setFixedHeight(new_height)
                self.request_delayed_update()

            if at_bottom:
                # 稍长延迟确保高度更新完成
                QTimer.singleShot(100, self.message_display.scroll_to_bottom)

        except (RuntimeError, AttributeError) as e:
            print(f"Height adjustment error: {e}")

        self._adjusting = False

    def render_content(self):
        """渲染内容"""
        if self.role == "assistant" or self.role == "":
            html_content = qtext_markdown_utils.markdown_to_html(self.raw_content)
            self.content_browser.setHtml(html_content)
        else:
            self.content_browser.setPlainText(self.raw_content)

        # 立即调整高度
        self.adjust_height()

    def handle_link_click(self, url):
        """处理链接点击 - 在外部浏览器打开"""
        QDesktopServices.openUrl(url)

    def find_text(self, search_term):
        """在消息内容中查找文本并返回匹配位置"""
        matches = []

        # 获取纯文本内容
        content = self.raw_content

        # 执行搜索（忽略大小写）
        start = 0
        while True:
            index = case_insensitive_find(content, search_term, start)
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
