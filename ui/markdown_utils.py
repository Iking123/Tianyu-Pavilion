import re
import markdown
import textwrap
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from .markdown_extensions import HighlightCodeExtension
from bs4 import BeautifulSoup


def fix_table_separators(content):
    """修复表格分隔行问题"""
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # 检查是否可能是表格分隔行
        if re.match(r"^\|.*\|$", line) and re.search(r"[-]+", line):
            # 标准化分隔行：将多个减号替换为单个减号
            fixed_line = re.sub(r"-+", "-", line)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def markdown_to_html(content):
    content = textwrap.dedent(content)

    # 修复有序列表中的空行问题
    content = re.sub(
        r"(\n\d+\.\s.*?)(\n\n+)(\d+\.\s)", r"\1\n\n\3", content, flags=re.DOTALL
    )

    # 增强嵌套列表支持 - 删除这行有问题的正则替换
    # 注释掉或删除这行: content = re.sub(r"^[ ]{3,}([-*])\s", r"  \1 ", content, flags=re.MULTILINE)

    # 新增：修复嵌套列表缩进
    # 将3空格缩进转换为4空格（Markdown标准）
    content = re.sub(r"^([ ]{3})", r"    ", content, flags=re.MULTILINE)

    # 预处理：修复表格分隔行问题
    content = fix_table_separators(content)

    # 解决删除线兼容性问题
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
            line-height: 1.2;
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
        /* 添加嵌套列表支持 */
        ol ol, ol ul, ul ol, ul ul {{
            margin-top: 4px;
            margin-bottom: 4px;
            padding-left: 20px;
        }}
    </style>
    <div style="
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 11pt;
        color: #333;
        line-height: 1.2;
    ">
        {html}
    </div>
    """
