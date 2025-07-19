import hashlib
import re
import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.backends.backend_agg import FigureCanvasAgg
import urllib.parse
import markdown
import textwrap
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from .markdown_extensions import HighlightCodeExtension
from bs4 import BeautifulSoup
from PyQt5.QtCore import QUrl
import numpy as np

# 创建缓存目录
CACHE_DIR = os.path.join(os.getcwd(), "formula_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def is_latex_available():
    """检测本地是否安装了LaTeX"""
    try:
        # 尝试执行latex命令，检查返回码
        subprocess.run(
            ["latex", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def configure_matplotlib():
    """根据LaTeX可用性配置matplotlib"""
    if is_latex_available():
        plt.rcParams["text.usetex"] = True  # 使用LaTeX渲染
        plt.rcParams["text.latex.preamble"] = (
            r"\usepackage{amsmath}\usepackage{ctex}"  # 加载amsmath和ctex包
        )
        print("LaTeX 可用，使用 LaTeX 渲染数学公式")
    else:
        plt.rcParams["text.usetex"] = False  # 使用matplotlib内置渲染
        plt.rcParams["mathtext.fontset"] = "cm"  # 使用Computer Modern字体
        plt.rcParams["font.family"] = ["SimHei"]  # 使用系统中已安装的支持中文的字体
        print("LaTeX 不可用，使用 matplotlib 内置渲染")


def _create_math_svg(formula, inline=False):
    """使用matplotlib生成紧凑透明背景的SVG数学公式（终极优化版）"""
    if not formula:
        return ""

    # 确保公式格式标准化（移除首尾空格和换行）
    formula = formula.strip().replace("\n", " ")

    # 生成缓存文件名（包含公式内容哈希和是否内联的标记）
    cache_key = f"{formula}_{inline}"
    cache_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()
    cached_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "formula_cache",
        f"math_{cache_hash}.svg",
    )

    # 创建缓存目录（如果不存在）
    os.makedirs(os.path.dirname(cached_path), exist_ok=True)

    # 检查缓存（如果存在且未强制删除，则使用缓存）
    if os.path.exists(cached_path):
        local_url = QUrl.fromLocalFile(cached_path).toString()
        style_class = "math-svg-inline" if inline else "math-svg-block"
        return f'<img src="{local_url}" class="{style_class}" alt="{formula}" title="{formula}" />'

    try:
        # 记录函数调用（用于调试确认）
        print(f"生成数学公式 SVG: {formula[:20]}... ({'行内' if inline else '块级'})")

        # 配置matplotlib（确保中文正常显示）
        plt.rcParams["text.usetex"] = False  # 使用matplotlib内置渲染，避免依赖LaTeX
        plt.rcParams["font.family"] = ["SimHei"]  # 使用系统中已安装的支持中文的字体

        # 创建图形和坐标轴（初始尺寸设为极小值，后续动态调整）
        fig = plt.figure(figsize=(0.1, 0.1))
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        # 隐藏坐标轴和边框
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # 设置完全透明背景
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)

        # 确定字体大小（行内公式更小，块级公式更大）
        font_size = 32 if inline else 36

        # 渲染数学公式
        # 使用center_baseline垂直对齐，确保公式基线居中
        text = ax.text(
            0.5,
            0.5,
            f"${formula}$",
            fontsize=font_size,
            horizontalalignment="center",
            verticalalignment="center_baseline",
            transform=ax.transAxes,
        )

        # 强制计算布局以获取精确边界
        canvas.draw()
        renderer = canvas.get_renderer()
        bbox = text.get_window_extent(renderer)

        # 转换边界框尺寸为英寸（基于当前DPI）
        dpi = fig.dpi
        width_inches = bbox.width / dpi
        height_inches = bbox.height / dpi

        # 添加极少量边距
        margin = 0.02
        width_inches += margin
        height_inches += margin

        # 设置图形大小为精确匹配内容的大小
        fig.set_size_inches(width_inches, height_inches)

        # 调整坐标轴范围以确保内容居中
        ax.set_xlim(0, width_inches)
        ax.set_ylim(0, height_inches)

        # 保存为SVG，使用bbox_inches='tight'进一步裁剪
        fig.savefig(
            cached_path,
            format="svg",
            bbox_inches="tight",
            pad_inches=0.05,
            transparent=True,
        )

        # 关闭图形以释放资源
        plt.close(fig)

        # 构建HTML标签（添加特定类名以便CSS精确控制）
        local_url = QUrl.fromLocalFile(cached_path).toString()
        style_class = "math-svg-inline" if inline else "math-svg-block"

        return f'<img src="{local_url}" class="{style_class}" alt="{formula}" title="{formula}" />'

    except Exception as e:
        print(f"生成数学公式SVG失败: {e}")
        # 失败时返回纯文本格式
        if inline:
            return f'<span class="math-fallback">${formula}$</span>'
        else:
            return f'<div class="math-fallback">$$ {formula} $$</div>'


# 初始化matplotlib配置
configure_matplotlib()


def replace_math_with_images(text):
    """
    将数学公式替换为SVG图片标签
    """
    # 首先处理块级公式: $$...$$ 和 \[...\]
    text = re.sub(
        r"(?<!\\)\$\$((?:[^$]|\\\$)+?)(?<!\\)\$\$|\\\[((?:[^\]]|\\\])+?)\\\]",
        lambda m: _create_math_svg(m.group(1) or m.group(2)),
        text,
        flags=re.DOTALL,
    )

    # 然后处理行内公式: $...$ 和 \(...\)
    text = re.sub(
        r"(?<!\\)\$((?:[^$]|\\\$)+?)(?<!\\)\$|\\\(((?:[^)]|\\\))+?)\\\)",
        lambda m: _create_math_svg(m.group(1) or m.group(2), inline=True),
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


def clear_formula_cache():
    """清空公式缓存"""
    try:
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith(".svg"):
                    os.remove(os.path.join(CACHE_DIR, filename))
            print(f"已清空公式缓存目录: {CACHE_DIR}")
    except Exception as e:
        print(f"清空缓存失败: {e}")


def get_cache_info():
    """获取缓存信息"""
    try:
        if not os.path.exists(CACHE_DIR):
            return {"count": 0, "size": 0}

        files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".svg")]
        total_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in files)

        return {
            "count": len(files),
            "size": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
        }
    except Exception as e:
        print(f"获取缓存信息失败: {e}")
        return {"count": 0, "size": 0}


def markdown_to_html(content):
    content = textwrap.dedent(content)

    # 插入空行以支持段落直接衔接无序列表
    lines = content.split("\n")
    new_lines = []
    for i in range(len(lines)):
        if i > 0 and lines[i].startswith("- ") and not lines[i - 1].strip() == "":
            new_lines.append("")
        new_lines.append(lines[i])
    content = "\n".join(new_lines)

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
        /* SVG数学公式样式 */
        img[src*=".svg"] {{
            max-width: 100%;
            height: auto;
            background-color: transparent;
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
