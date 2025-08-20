from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QTextCharFormat, QSyntaxHighlighter, QBrush, QColor


class SearchHighlighter(QSyntaxHighlighter):
    """文本高亮器，用于在消息中高亮搜索匹配项"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_term = ""
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QBrush(QColor("#FFFF00")))  # 黄色背景
        self.highlight_format.setForeground(QBrush(QColor("#000000")))  # 黑色文本

    def set_search_term(self, term):
        """设置要搜索的文本"""
        self.search_term = term
        self.rehighlight()

    def highlightBlock(self, text):
        """高亮匹配的文本块"""
        if not self.search_term:
            return

        # 不区分大小写的搜索 - 使用 PatternOption
        regex = QRegularExpression(
            self.search_term, QRegularExpression.PatternOption.CaseInsensitiveOption
        )

        # 使用 globalMatch() 方法进行匹配（PyQt6 推荐方式）
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start, length, self.highlight_format)
