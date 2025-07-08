import hashlib
import re
import os
import requests
import urllib.parse
import markdown
import textwrap
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from .markdown_extensions import HighlightCodeExtension
from bs4 import BeautifulSoup
from PyQt5.QtCore import QUrl

# 创建缓存目录
CACHE_DIR = os.path.join(os.getcwd(), "formula_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _download_image(url, save_path):
    """下载图片到本地缓存"""
    try:
        # 添加浏览器头信息，避免被服务器拒绝
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
        print(f"下载失败，状态码: {response.status_code}")
        return False
    except Exception as e:
        print(f"下载图片出错: {e}")
        return False


def _get_cached_path(url):
    """生成缓存文件路径（基于URL哈希）"""
    url_hash = hashlib.md5(url.encode()).hexdigest()  # 用URL哈希作为文件名
    return os.path.join(CACHE_DIR, f"{url_hash}.png")


def _create_math_image(formula, inline=False):
    """修改为：优先加载本地缓存，无缓存则下载"""
    if not formula:
        return ""
    formula = formula.strip().replace("\n", " ")
    formula_encoded = urllib.parse.quote(formula)

    # 生成原始URL
    if inline:
        url = f"https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B150%7D%20%5Cbg_white%20%5Clarge%20{formula_encoded}"
        style = "vertical-align: middle; display: inline-block; max-height: 1.2em;"
    else:
        url = f"https://latex.codecogs.com/png.latex?%5Cdpi%7B150%7D%20%5Cbg_white%20%5Clarge%20{formula_encoded}"
        style = "display: block; margin: 0.5em auto; max-height: 3em;"

    # 检查本地缓存
    cached_path = _get_cached_path(url)
    if not os.path.exists(cached_path):
        # 缓存不存在，下载
        if not _download_image(url, cached_path):
            return f"[公式加载失败: {formula}]"  # 失败时显示文本提示

    # 用本地路径替换远程URL
    local_url = QUrl.fromLocalFile(cached_path).toString()  # 转换为本地文件URL
    return (
        f'<img src="{local_url}" alt="{formula}" title="{formula}" style="{style}" />'
    )


def replace_math_with_images(text):
    """
    将数学公式替换为图片标签
    """
    # 首先处理块级公式: $$...$$ 和 \[...\]
    text = re.sub(
        r"(?<!\\)\$\$((?:[^$]|\\\$)+?)(?<!\\)\$\$|\\\[((?:[^\]]|\\\])+?)\\\]",
        lambda m: _create_math_image(m.group(1) or m.group(2)),
        text,
        flags=re.DOTALL,
    )

    # 然后处理行内公式: $...$ 和 \(...\)
    text = re.sub(
        r"(?<!\\)\$((?:[^$]|\\\$)+?)(?<!\\)\$|\\\(((?:[^)]|\\\))+?)\\\)",
        lambda m: _create_math_image(m.group(1) or m.group(2), inline=True),
        text,
        flags=re.DOTALL,
    )
    return text


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

    # 预处理：处理数学公式
    content = replace_math_with_images(content)

    # 修复有序列表中的空行问题
    content = re.sub(
        r"(\n\d+\.\s.*?)(\n\n+)(\d+\.\s)", r"\1\n\n\3", content, flags=re.DOTALL
    )

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
        .math-formula {{
            max-width: 100%;
            overflow: auto;
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
