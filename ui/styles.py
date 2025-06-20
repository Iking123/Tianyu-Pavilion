APP_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #F5F7FA;
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }
    QScrollArea {
        border: none;
    }
"""

INPUT_STYLE = """
    QTextEdit {
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        padding: 12px;
        font-size: 12pt;
    }
"""

TIME_STYLE = """
    QLabel {
        color: #555;
        font-weight: bold;
        padding: 2px 8px;
        background-color: #f0f0f0;
        border-radius: 4px;
    }
"""

ASSIST_STYLE = """
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    h1 { font-size: 1.6em; }
    h2 { font-size: 1.4em; }
    h3 { font-size: 1.2em; }
    h4 { font-size: 1.1em; }
    pre, code {
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #f5f7fa;
        border-radius: 4px;
        padding: 2px 4px;
        white-space: pre-wrap;
    }
    pre {
        padding: 10px;
        overflow-x: auto;
    }
    blockquote {
        border-left: 3px solid #4A90E2;
        padding-left: 10px;
        margin-left: 0;
        color: #555;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 0 4px 4px 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
        border: 1px solid #ddd !important;
    }
    th {
        background-color: #f2f2f2 !important;
        font-weight: bold;
        border: 1px solid #ddd !important;
    }
    td {
        border: 1px solid #ddd !important;
        padding: 8px;
        text-align: left;
    }
    a {
        color: #4A90E2;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    ul, ol {
        padding-left: 20px;
        margin: 8px 0;
    }
    li {
        margin-bottom: 4px;
    }
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 12px 0;
        height: 1px;
        background-color: #ddd;
    }
    
    /* 代码高亮样式 */
    .highlight {
        background-color: #f5f7fa;
        border-radius: 4px;
        padding: 10px;
        margin: 10px 0;
        overflow-x: auto;
    }
    .highlight pre {
        padding: 0;
        margin: 0;
        background: none;
    }
    
    /* 数学公式样式 */
    .math-formula {{
        font-family: monospace;
        background-color: #f8f9fa;
        padding: 2px 5px;
        border-radius: 3px;
        margin: 2px 0;
    }}
    .math-formula.inline {{
        display: inline;
        border: 1px solid #e0e0e0;
    }}
    .math-formula.block {{
        display: block;
        text-align: center;
        padding: 10px;
        margin: 15px 0;
        border: 1px dashed #c0c0c0;
    }}
    """

THINKING_STYLE = """
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #555;
        padding: 8px;
    }
    pre {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 10px;
        overflow: auto;
    }
    code {
        background-color: #F5F5F5;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: Consolas, Monaco, 'Andale Mono', monospace;
    }
    blockquote {
        border-left: 3px solid #FFC107;  /* 黄色边框 */
        padding-left: 10px;
        margin-left: 0;
        color: #666;
        font-style: italic;
        background-color: #FFFFF0 !important;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
        background-color: #FFFFF0 !important;
    }
    th, td {
        border: 1px solid #E0E0E0;
        padding: 8px;
        text-align: left;
        background-color: #FFFFF0 !important; 
    }
    th {
        background-color: #FFF3CD !important;  /* 浅黄色表头 */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #E65100;  /* 深橙色标题 */
        margin-top: 15px;
        margin-bottom: 10px;
    }
"""

# 不同角色的消息样式
MESSAGE_STYLES = {
    "assistant": """color: #50B7C1;""",
    "user": """color: #888;""",
    "system": """color: #4A90E2;""",
}

BUTTON_STYLES = {
    "send": """
    QPushButton {
        background-color: #4A90E2;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #3A7BC8;
    }
    QPushButton:disabled {
        background-color: #CCCCCC;
    }
    """,
    "clear": """
    QPushButton {
        background-color: #E74C3C;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #C0392B;
    }
    """,
    "scroll": """
        QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #3A7BC8;
        }
    """,
}
