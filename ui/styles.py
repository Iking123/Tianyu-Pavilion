APP_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #F5F7FA;
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }
    QScrollArea {
        border: none;
    }
    /* 状态栏样式 */
    QStatusBar {
        background-color: #F0F0F0;
        border-top: 1px solid #D0D0D0;
        padding: 0 5px;
        height: 40px;  /* 明确设置高度 */
    }
    QStatusBar QLabel {
        color: #555;
        font-weight: bold;
        padding: 0 3px;
    }
    QStatusBar QPushButton {
        min-height: 22px;
        /* 移除最小宽度设置 */
        padding: 2px 8px;  /* 减少内边距 */
        font-size: 10pt;  /* 增大字体 */
        border-radius: 3px;
    }
    /* 滚动按钮样式 */
    QStatusBar QPushButton[style*="scroll"] {
        background-color: #4A90E2;
        color: white;
    }
"""

ENHANCED_SCROLLBAR_STYLE = """
/* 垂直滚动条整体 */
QScrollBar:vertical {
    border: none;
    background: #F5F5F5;
    width: 16px;         /* 增加整体宽度 */
    margin: 0px;
    border-radius: 8px;  /* 相应调整背景圆角 */
}

/* 垂直滚动条滑块 - 关键修改：让border-radius等于宽度的一半 */
QScrollBar::handle:vertical {
    background: #A0A0A0;
    min-height: 40px;
    border-radius: 6px;  /* 12px宽度的一半 */
    margin: 2px 2px;     /* 左右边距设为2px，让滑块实际宽度为16px */
}

QScrollBar::handle:vertical:hover {
    background: #808080;
    border-radius: 6px;  /* 保持一致 */
}

QScrollBar::handle:vertical:pressed {
    background: #606060;
    border-radius: 6px;  /* 保持一致 */
}

/* 移除上下箭头 */
QScrollBar::add-line:vertical, 
QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
    border: none;
}

/* 移除滑块周围的空间 */
QScrollBar::add-page:vertical, 
QScrollBar::sub-page:vertical {
    background: none;
}

/* 水平滚动条（如果需要的话）*/
QScrollBar:horizontal {
    border: none;
    background: #F5F5F5;
    height: 16px;        /* 增加整体高度 */
    margin: 0px;
    border-radius: 8px;  /* 相应调整背景圆角 */
}

QScrollBar::handle:horizontal {
    background: #A0A0A0;
    min-width: 40px;
    border-radius: 6px;  /* 12px高度的一半 */
    margin: 2px 2px;
}

QScrollBar::handle:horizontal:hover {
    background: #808080;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:pressed {
    background: #606060;
    border-radius: 6px;
}

QScrollBar::add-line:horizontal, 
QScrollBar::sub-line:horizontal {
    width: 0px;
    background: none;
    border: none;
}

QScrollBar::add-page:horizontal, 
QScrollBar::sub-page:horizontal {
    background: none;
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
    img[src*=".svg"] {
        max-width: 100%;
        height: auto;
        background-color: transparent;
        border: none !important;
    }

    /* 行内公式样式必须与函数中设置的一致 */
    img[src*=".svg"][style*="inline"] {
        max-height: 1.1em !important;  /* 关键：加!important确保优先 */
        margin: 0 1px !important;
    }

    /* 块级公式同理 */
    img[src*=".svg"][style*="block"] {
        max-height: 2.5em !important;
        margin: 0.3em auto !important;
    }
    
    /* 数学公式容器样式 */
    .math-container {
        text-align: center;
        margin: 10px 0;
    }
    
    /* 数学公式错误回退样式 */
    .math-fallback {
        font-family: 'Times New Roman', serif;
        font-style: italic;
        color: #333;
    }
    
    .math-fallback.inline {
        display: inline;
        background-color: #f8f9fa;
        padding: 2px 5px;
        border-radius: 3px;
        border: 1px solid #e0e0e0;
        font-size: 0.95em;
    }
    
    .math-fallback.block {
        display: block;
        text-align: center;
        background-color: #f8f9fa;
        padding: 10px;
        margin: 15px 0;
        border: 1px dashed #c0c0c0;
        border-radius: 4px;
        font-size: 1.1em;
    }
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
    
    /* Thinking 模式下的 SVG 数学公式样式 */
    /* 数学公式样式 */
    img[src*=".svg"] {
        max-width: 100%;
        height: auto;
        background-color: transparent;
        border: none !important;
    }

    /* 行内公式样式必须与函数中设置的一致 */
    img[src*=".svg"][style*="inline"] {
        max-height: 1.1em !important;  /* 关键：加!important确保优先 */
        margin: 0 1px !important;
    }

    /* 块级公式同理 */
    img[src*=".svg"][style*="block"] {
        max-height: 2.5em !important;
        margin: 0.3em auto !important;
    }
    
    /* Thinking 模式下的数学公式错误回退样式 */
    .math-fallback {
        font-family: 'Times New Roman', serif;
        font-style: italic;
        color: #666;
    }
    
    .math-fallback.inline {
        display: inline;
        background-color: #FFFFF0;
        padding: 2px 5px;
        border-radius: 3px;
        border: 1px solid #E0D5B0;
        font-size: 0.95em;
    }
    
    .math-fallback.block {
        display: block;
        text-align: center;
        background-color: #FFFFF0;
        padding: 10px;
        margin: 15px 0;
        border: 1px dashed #D0C090;
        border-radius: 4px;
        font-size: 1.1em;
    }
"""

# 不同消息，“角色名称”部分的样式
MESSAGE_STYLES = {
    "": """color: #4A90E2;""",
    "assistant": """color: #50B7C1;""",
    "user": """color: #888;""",
    "system": """color: #4A90E2;""",
    "option": """color: black;""",
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
    "option": """
        QPushButton {
            background-color: #5DADE2;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 30px;
            font-family: Microsoft YaHei;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #3498DB;
        }
        QPushButton:pressed {
            background-color: #2E86C1;
        }
    """,
}

TOGGLE_BUTTON_STYLE_ENABLED = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
"""

TOGGLE_BUTTON_STYLE_DISABLED = """
    QPushButton {
        background-color: #f44336;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
"""

MESSAGE_BASE_STYLES = {
    "assistant_regular": """
        QTextBrowser {
            background-color: #F0F7FF;
            border: 1px solid #C0D5E0;
            border-radius: 8px;
            padding: 12px;
            font-size: 11pt;
        }
    """,
    "assistant_thinking": """
        QTextBrowser {
            background-color: #FFFFF0;
            border: 1px solid #E0D5B0;
            border-radius: 8px;
            padding: 12px;
            font-size: 11pt;
        }
    """,
    "user": """
        QTextBrowser {
            background-color: #E6F7ED;
            border: 1px solid #C0E0D0;
            border-radius: 8px;
            padding: 12px;
            font-size: 11pt;
        }
    """,
    "system": """
        QTextBrowser {
            background-color: #F8F8F8;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 12px;
            color: #666;
            font-style: italic;
            font-size: 11pt;
        }
    """,
    "option": """
        color: black;
        background-color: white;
        border: 1px solid black;
        border-radius: 4px;
        padding: 10px;
    """,
    "default": """
        QTextBrowser {
            background-color: #FCF9F5; /* 接近米色的浅暖色调，像旧书页的质感 */
            border: 1px solid #EFE6DD; /* 淡奶茶色边框，柔和不突兀 */
            border-radius: 8px;
            padding: 12px;
            color: #666;
            font-size: 11pt;
        }
    """,
}
