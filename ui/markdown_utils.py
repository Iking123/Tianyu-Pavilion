import re
import markdown
import textwrap
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from .markdown_extensions import HighlightCodeExtension
from bs4 import BeautifulSoup


def markdown_to_html(content):
    """将Markdown转换为HTML"""
    content = textwrap.dedent(content)

    # 解决删除线兼容性问题（使用通用方法）
    content = re.sub(r"~~(.*?)~~", r"<del>\1</del>", content)

    try:
        html = markdown.markdown(
            content,
            extensions=[
                FencedCodeExtension(),
                TableExtension(),
                "nl2br",
                "sane_lists",
                HighlightCodeExtension(),
                "markdown.extensions.extra",
            ],
        )
    except Exception as e:
        print(f"Markdown解析错误: {e}")
        # 对原始内容进行HTML转义
        escaped_content = markdown.markdown(markdown.util.code_escape(content))
        return f"""
        <div style="
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            font-size: 11pt;
            color: #333;
            line-height: 1.6;
            padding: 15px;
            border: 1px solid #ffcccc;
            background-color: #fffafa;
        ">
            <p><strong>Markdown解析错误:</strong> {str(e)}</p>
            <pre>{escaped_content}</pre>
        </div>
        """

    # 使用BeautifulSoup处理HTML更安全可靠
    soup = BeautifulSoup(html, "html.parser")

    # 增强表格样式（只针对真正的表格）
    for table in soup.find_all("table"):
        table["style"] = "border:1px solid #ccc; border-collapse:collapse;"

        for th in table.find_all("th"):
            th["style"] = (
                "border:1px solid #ccc; padding:8px; background-color:#f2f2f2;"
            )

        for td in table.find_all("td"):
            td["style"] = "border:1px solid #ccc; padding:8px;"

    # 转换为字符串
    html = str(soup)

    # 添加CSS样式
    return f"""
    <style>
        .markdown-list {{
            margin-top: 4px;
            margin-bottom: 4px;
            padding-left: 0;
        }}
        li {{
            margin: 6px 0;
        }}
        del {{
            text-decoration: line-through;
            color: #999;
        }}
    </style>
    <div style="
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 11pt;
        color: #333;
        line-height: 1.6;
    ">
        {html}
    </div>
    """
