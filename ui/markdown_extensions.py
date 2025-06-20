import re
import markdown
from markdown.preprocessors import Preprocessor
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


class HighlightCodeExtension(markdown.Extension):
    """自定义代码高亮扩展"""

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(HighlightCodePreprocessor(md), "highlight_code", 30)


class HighlightCodePreprocessor(Preprocessor):
    """代码高亮预处理器"""

    def __init__(self, md):
        super().__init__(md)
        self.style = get_style_by_name("friendly")
        self.formatter = HtmlFormatter(
            style=self.style,
            noclasses=True,
            wrapcode=True,
            cssstyles="white-space: pre-wrap; word-wrap: break-word;",
        )

    def run(self, lines):
        new_lines = []
        in_code_block = False
        code_lines = []
        language = None

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # 结束代码块
                    in_code_block = False

                    # 尝试根据语言名称获取lexer
                    try:
                        lexer = (
                            get_lexer_by_name(language)
                            if language
                            else guess_lexer("\n".join(code_lines))
                        )
                    except:
                        lexer = get_lexer_by_name("text")

                    # 高亮代码
                    highlighted_code = highlight(
                        "\n".join(code_lines), lexer, self.formatter
                    )

                    new_lines.append(highlighted_code)
                    code_lines = []
                    language = None
                else:
                    # 开始代码块
                    in_code_block = True
                    # 提取语言名称
                    language_str = line.strip()[3:].strip()
                    language = language_str if language_str else None
            elif in_code_block:
                code_lines.append(line)
            else:
                new_lines.append(line)

        return new_lines
