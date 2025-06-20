import re
import markdown
import textwrap
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from .markdown_extensions import HighlightCodeExtension


def markdown_to_html(content):
    """将Markdown转换为HTML"""
    content = textwrap.dedent(content)
    content = re.sub(
        r"(\n\s*\|[^\n]+\|\s*\n)(\s*\|[^\n]+\|\s*\n)*",
        _fix_table_format,
        content,
        flags=re.MULTILINE,
    )

    try:
        html = markdown.markdown(
            content,
            extensions=[
                FencedCodeExtension(),
                TableExtension(),
                "nl2br",
                "sane_lists",
                HighlightCodeExtension(),
            ],
        )
    except Exception as e:
        print(f"Markdown解析错误: {e}")
        html = f"<pre>{content}</pre>"

    # 增强表格样式
    html = re.sub(
        r"<table>",
        r'<table style="border:1px solid #ccc; border-collapse:collapse;">',
        html,
    )
    html = re.sub(
        r"<th>",
        r'<th style="border:1px solid #ccc; padding:8px; background-color:#f2f2f2;">',
        html,
    )
    html = re.sub(r"<td>", r'<td style="border:1px solid #ccc; padding:8px;">', html)

    return f"""
    <div style="
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 11pt;
        color: #333;
        line-height: 1.6;
    ">
        {html}
    </div>
    """


def _fix_table_format(match):
    """修复表格格式"""
    table_block = match.group(0)
    table_block = re.sub(r"(\|)\s*(-+)\s*", r"\1\2", table_block)
    return "\n\n" + table_block.strip() + "\n\n"
