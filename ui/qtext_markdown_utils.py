import hashlib
import re
import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.backends.backend_agg import FigureCanvasAgg
import markdown
import textwrap
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from .markdown_extensions import HighlightCodeExtension
from bs4 import BeautifulSoup
from PyQt6.QtCore import QUrl

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
    # print(content)

    # 预处理：查找并修复被缩进的“围栏代码块”。
    # 这个问题会导致 Markdown 解析器将它们错误地识别为“缩进代码块”，
    # 从而绕过了我们自定义的 FencedCodeExtension 和 HighlightCodeExtension。
    # 我们通过 textwrap.dedent 来移除这些代码块的公共前导空格。
    def dedent_fenced_code_block(match):
        return textwrap.dedent(match.group(0))

    # 这个正则表达式会匹配整个围栏代码块（从 ``` 到 ```），包括被缩进的情况。
    # re.DOTALL 使得 '.' 可以匹配换行符。
    # re.MULTILINE 使得 '^' 和 '$' 可以匹配每一行的开头和结尾。
    content = re.sub(
        r"^[ ]*(`{3,}|~{3,}).*?^[ ]*\1[ ]*$",
        dedent_fenced_code_block,
        content,
        flags=re.DOTALL | re.MULTILINE,
    )
    # print(content)

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

    # 增强表格样式（只针对真正的“数据”表格）
    for table in soup.find_all("table"):
        # <--- 修改: 增加判断，跳过我们的代码块表格，避免样式污染
        if "code-block-container" in table.get("class", []):
            continue

        table["style"] = "border:1px solid #ccc; border-collapse:collapse;"

        for th in table.find_all("th"):
            th["style"] = (
                "border:1px solid #ccc; padding:8px; background-color:#f2f2f2;"
            )

        for td in table.find_all("td"):
            td["style"] = "border:1px solid #ccc; padding:8px;"

    # 转换为字符串
    html = str(soup)

    # <--- 修改: 更新style标签内的CSS以匹配新的table结构
    # 添加强化的CSS样式和JavaScript复制功能
    return f"""
    <style>
        p {{
            line-height: 1.2;
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }}
        
        /* 行内代码 */
        code {{
            font-family: 'HYQiHei' !important;
            background: transparent !important;
        }}
        
        /* 代码块容器 - 使用 table 选择器 */
        table.code-block-container {{
            border-collapse: collapse !important;
            border-spacing: 0 !important;
            width: 100% !important;
            margin: 15px 0 !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            background: #2d3748 !important;
        }}
        
        /* 代码块头部 - 使用 td 选择器，并增加padding来确保高度 */
        td.code-block-header {{
            background: #313641 !important;
            padding: 12px 15px !important; /* 控制头部高度 */
            border-bottom: 1px solid #485a70 !important;
        }}
        
        .code-language {{
            color: #e2e8f0 !important;
            font-size: 11pt !important;
            font-weight: 500 !important;
            text-transform: capitalize !important;
        }}
        
        .copy-button {{
            background: #485a70 !important;
            color: #e2e8f0 !important;
            border: none !important;
            padding: 5px 12px !important;
            font-size: 11pt !important;
            cursor: pointer !important;
            transition: all 0.2s !important;
            text-decoration: none !important;
        }}
        
        .copy-button:hover {{
            background: #a0aec0 !important;
            color: white !important;
        }}
        
        /* 代码内容区域 - 使用 td 选择器 */
        td.code-block-content {{
            background: #22272e !important;
            margin: 0 !important;
            padding: 10px !important;
            overflow: hidden !important;
        }}
        
        /* 代码内容区域的 pre 标签 */
        td.code-block-content pre {{
            background: #22272e !important;
            color: #d4d4d4 !important;
            margin: 0 !important;
            padding: 15px !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
            font-size: 11pt !important;
            line-height: 1.5 !important;
            border: none !important;
        }}
        
        /* 覆盖 Pygments 生成的 pre 样式，因为我们已将其提取出来 */
        .highlight pre {{
             padding: 0 !important;
             margin: 0 !important;
             background: transparent !important; /* 背景由td控制 */
             border: none !important;
        }}
        
        /* 列表样式 */
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
        
        /* 数学公式样式 */
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
        
        /* 数学公式容器样式 */
        .math-container {{
            text-align: center;
            margin: 10px 0;
        }}
        
        /* 数学公式错误回退样式 */
        .math-fallback {{
            font-family: 'Times New Roman', serif;
            font-style: italic;
        }}
        
        .math-fallback.inline {{
            display: inline;
            background-color: #f8f9fa;
            padding: 2px 5px;
            border-radius: 3px;
            border: 1px solid #e0e0e0;
            font-size: 0.95em;
        }}
        
        .math-fallback.block {{
            display: block;
            text-align: center;
            background-color: #f8f9fa;
            padding: 10px;
            margin: 15px 0;
            border: 1px dashed #c0c0c0;
            border-radius: 4px;
            font-size: 1.1em;
        }}
    </style>
    
    <script>
        function copyCodeBlock(button) {{
            const codeContainer = button.closest('.code-block-container');
            const codeContent = codeContainer.querySelector('.code-block-content');
            const rawCode = codeContent.getAttribute('data-code');
            
            if (rawCode) {{
                // 使用现代clipboard API或fallback到execCommand
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(rawCode).then(function() {{
                        showCopySuccess(button);
                    }}, function(err) {{
                        console.error('复制失败:', err);
                        fallbackCopyTextToClipboard(rawCode, button);
                    }});
                }} else {{
                    fallbackCopyTextToClipboard(rawCode, button);
                }}
            }}
        }}
        
        function fallbackCopyTextToClipboard(text, button) {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            
            // 避免滚动到底部
            textArea.style.top = "0";
            textArea.style.left = "0";
            textArea.style.position = "fixed";
            
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {{
                const successful = document.execCommand('copy');
                if (successful) {{
                    showCopySuccess(button);
                }} else {{
                    alert('复制失败，请手动复制代码');
                }}
            }} catch (err) {{
                console.error('Fallback复制失败:', err);
                alert('复制失败，请手动复制代码');
            }}
            
            document.body.removeChild(textArea);
        }}
        
        function showCopySuccess(button) {{
            const originalText = button.textContent;
            button.textContent = '已复制!';
            button.style.background = '#48bb78';
            
            setTimeout(() => {{
                button.textContent = originalText;
                button.style.background = '#485a70';
            }}, 2000);
        }}
    </script>
    
    <div style="
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 11pt;
        line-height: 1.2;
    ">
        {html}
    </div>
    """
