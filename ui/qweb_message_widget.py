from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer
import time
from . import markdown_utils
from .styles import *
from core.config_manager import get_config
from funcs import *


@delay_update
class MessageWidget(QWidget):
    """通用的消息控件"""

    def __init__(self, role, content, is_thinking=False, parent=None):
        super().__init__(parent)
        self._adjusting = False
        self.message_display = parent
        self.is_thinking = is_thinking
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setAlignment(Qt.AlignTop)

        # 角色标签
        role_name = ""
        match role:
            case "user":
                role_name = "你"
            case "assistant":
                role_name = f"DeepSeek-R1{'（思考）' if is_thinking else ''}"
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

        # 使用 QWebEngineView
        self.content_view = QWebEngineView()
        # 使用120%的缩放因子解决字体大小问题
        self.content_view.setZoomFactor(1.2)
        self.content_view.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.MinimumExpanding
        )
        self.content_view.setMinimumWidth(600)
        self.content_view.setContextMenuPolicy(Qt.NoContextMenu)
        # 使用背景色
        self.content_view.page().setBackgroundColor(Qt.transparent)

        # 连接页面加载完成信号
        self.content_view.loadFinished.connect(self.on_page_loaded)

        # 存储内容
        self.raw_content = content
        self.role = role
        self.is_rendered = False

        # 设置初始内容
        self.set_content(content, role)

        layout.addWidget(self.content_view)
        self.setLayout(layout)

        # 设置基础样式
        self.apply_base_style(role, is_thinking)

        # 高度调整计时器
        self.height_adjust_timer = QTimer()
        self.height_adjust_timer.setSingleShot(True)
        self.height_adjust_timer.timeout.connect(self.adjust_height)

    def on_page_loaded(self, ok):
        """页面加载完成后调整高度"""
        if ok and not self.is_rendered:
            self.adjust_height()
            self.is_rendered = True

    def render_content(self, content=None):
        """渲染内容为HTML"""
        content = content or self.raw_content
        html_content = markdown_utils.markdown_to_html(content)

        # 添加MathJax支持
        mathjax_script = """
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <script>
        MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']]
          },
          svg: {
            fontCache: 'global'
          }
        };
        </script>
        """

        # 确定背景样式
        bg_style = ""
        if self.role == "assistant":
            if self.is_thinking:
                bg_style = "background-color: #FFFFF0;"  # 思考状态背景
            else:
                bg_style = "background-color: #F0F7FF;"  # 助手正常背景
        elif self.role == "user":
            bg_style = "background-color: #E6F7ED;"  # 用户背景
        elif self.role == "system":
            bg_style = "background-color: #F8F8F8;"  # 系统背景

        # 确保MathJax在内容加载后执行
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    font-size: 13pt;  /* 增大字体 */
                    color: #333;
                    margin: 0;
                    padding: 12px;
                    border-radius: 8px;
                    line-height: 1.4;  /* 减小行高 */
                    {bg_style}
                }}
                p, li, td, th {{
                    margin: 4px 0;  /* 减小段落和列表项间距 */
                }}
                pre, code {{
                    font-family: 'Consolas', 'Courier New', monospace;
                    background-color: rgba(0,0,0,0.05);
                    border-radius: 4px;
                    margin: 4px 0;  /* 减小代码块间距 */
                }}
                pre {{
                    padding: 8px;  /* 减小内边距 */
                    overflow-x: auto;
                }}
                code {{
                    padding: 1px 3px;  /* 减小内边距 */
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    margin: 4px 0;  /* 减小图片间距 */
                }}
                table {{
                    border-collapse: collapse;
                    margin: 8px 0;  /* 减小表格间距 */
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 6px;  /* 减小单元格内边距 */
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 0.8em;  /* 减小标题间距 */
                    margin-bottom: 0.4em;
                }}
                ul, ol {{
                    margin-top: 4px;  /* 减小列表间距 */
                    margin-bottom: 4px;
                }}
                li {{
                    margin-bottom: 2px;  /* 减小列表项间距 */
                }}
                blockquote {{
                    margin: 8px 0;  /* 减小引用块间距 */
                    padding: 8px;  /* 减小内边距 */
                }}
            </style>
            {mathjax_script}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        self.content_view.setHtml(full_html)
        self.is_rendered = False  # 标记需要重新调整高度

    def append_content(self, new_content):
        """追加新内容并重新渲染"""
        self.raw_content += new_content
        self.render_content()

    def force_render(self):
        """强制立即渲染内容"""
        self.render_content()

    def apply_base_style(self, role, is_thinking):
        """应用基础样式"""
        if role == "assistant":
            style_key = "assistant_thinking" if is_thinking else "assistant_regular"
        elif role == "user":
            style_key = "user"
        elif role == "system":
            style_key = "system"
        else:
            style_key = "default"

        # 设置整个消息控件的样式
        self.setStyleSheet(MESSAGE_BASE_STYLES[style_key])

    def set_content(self, content, role):
        """设置内容并渲染"""
        self.raw_content = content
        self.render_content()

    def adjust_height(self):
        """根据内容自动调整高度"""
        if self._adjusting or self.message_display is None:
            return

        self._adjusting = True

        try:
            # 通过JavaScript获取页面实际高度
            self.content_view.page().runJavaScript(
                """
                // 获取实际内容高度
                var body = document.body;
                var html = document.documentElement;
                var height = Math.max(
                    body.scrollHeight, 
                    body.offsetHeight, 
                    html.clientHeight, 
                    html.scrollHeight, 
                    html.offsetHeight
                );
                
                // 减去不必要的边距
                var computedStyle = window.getComputedStyle(body);
                var paddingTop = parseFloat(computedStyle.paddingTop);
                var paddingBottom = parseFloat(computedStyle.paddingBottom);
                
                height - paddingTop - paddingBottom;
            """,
                self.update_height,
            )
        except Exception as e:
            print(f"高度调整错误: {e}")
            self._adjusting = False

    def update_height(self, height):
        """更新视图高度"""
        try:
            if not height:
                return

            # 添加5px的缓冲
            new_height = int(height) + 5

            # 更新高度
            self.content_view.setMinimumHeight(new_height)
            self.content_view.setMaximumHeight(new_height)

            # 请求延迟更新
            self.request_delayed_update()

            # 滚动到底部
            if self.message_display:
                QTimer.singleShot(100, self.message_display.scroll_to_bottom)

        finally:
            self._adjusting = False
