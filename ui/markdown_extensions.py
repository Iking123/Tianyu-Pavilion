import re
import markdown
from markdown.postprocessors import Postprocessor
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
import html as html_module
import html  # 新增导入


class HighlightCodeExtension(markdown.Extension):
    """自定义代码高亮扩展"""

    def extendMarkdown(self, md):
        md.registerExtension(self)
        # 使用后处理器，在HTML生成后替换代码块
        md.postprocessors.register(HighlightCodePostprocessor(md), "highlight_code", 25)


class HighlightCodePostprocessor(Postprocessor):
    """代码高亮后处理器"""

    def __init__(self, md):
        super().__init__(md)
        # 使用深色主题
        self.style = get_style_by_name("monokai")
        # <--- 修改: 关键！设置 nowrap=True，让 Pygments 只返回代码片段，不添加外层的 <div class="highlight"><pre>
        self.formatter = HtmlFormatter(
            style=self.style,
            noclasses=True,
            # wrapcode=True, #
            nowrap=True,  # <--- 关键修改
        )

    def run(self, text):
        """在HTML生成后处理代码块"""

        def replace_code_block(match):
            full_match = match.group(0)

            language_match = re.search(r'class="language-([^"]*)"', full_match)
            if language_match:
                language = language_match.group(1)
            else:
                language = None

            code_match = re.search(r"<code[^>]*>(.*?)</code>", full_match, re.DOTALL)
            if not code_match:
                return full_match

            code_content = html_module.unescape(code_match.group(1))
            code_content = re.sub(r"<[^>]+>", "", code_content)

            try:
                if language:
                    lexer = get_lexer_by_name(language)
                else:
                    lexer = guess_lexer(code_content)
            except:
                lexer = get_lexer_by_name("text")

            # <--- 修改: 现在 highlighted_code 只包含纯粹的高亮后代码 (e.g., <span>...</span>)
            highlighted_code = highlight(code_content, lexer, self.formatter)

            language_display = language if language else lexer.name
            escaped_code = html_module.escape(code_content)

            # --- 使用 <table> 结构，并将纯净的 highlighted_code 放入我们自己的 <pre> 标签 ---
            return f"""
<table class="code-block-container" style="border-collapse: collapse; border-spacing: 0; width: 100%; margin: 15px 0; overflow: hidden; background: #2d3748; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
    
    <tr class="code-block-header-row">
        <td class="code-block-header" style="background: #313641; padding: 12px 15px; border-bottom: 1px solid #485a70;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="text-align: left; padding: 0; margin: 0; border: none;">
                        <span class="code-language" style="color: #e2e8f0; font-size: 11pt; font-weight: 500; text-transform: capitalize;">{language_display}</span>
                    </td>
                    <td style="text-align: right; padding: 0; margin: 0; border: none;">
                        <a href="copycode:{escaped_code}" class="copy-button" style="background: #485a70; color: #e2e8f0; border: none; padding: 5px 12px; font-size: 11pt; cursor: pointer; text-decoration: none;">复制</a>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    
    <tr class="code-block-content-row">
        <td class="code-block-content" style="background: #22272e; padding: 10px !important; margin: 0 !important;">
            <pre style="background: #22272e !important; color: #d4d4d4 !important; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; padding: 15px !important; margin: 0 !important; font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important; font-size: 11pt !important; line-height: 1.5 !important;">{highlighted_code}</pre>
        </td>
    </tr>
</table>
"""

        code_block_pattern = r'<pre><code(?:\s+class="[^"]*")?[^>]*>.*?</code></pre>'
        text = re.sub(code_block_pattern, replace_code_block, text, flags=re.DOTALL)
        return text
