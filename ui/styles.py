APP_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #F5F7FA;
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }
    QLabel {
        background-color: none;
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
        border-radius: 4px;
    }
    
    QToolTip {
        background-color: white;
        color: black;
        font-size: 10pt;
    }
    
    QComboBox QAbstractItemView {
        border: 1px solid #ccc;
        background: snow;
    }
    /* 列表项基础样式（非悬停/非选中） */
    QComboBox QAbstractItemView::item {
        color: black;  /* 默认黑色文字 */
        padding: 8px 12px; /* 增大点击区域，避免误触 */
    }
    QComboBox QAbstractItemView::item:selected {
        background: #4a90e2;
        background-color: #4a90e2;
        color: white;
    }
    
    QMenu {
        border: 1px solid #ccc;
        background: snow;
    }
    QMenu::item {
        color: black;  /* 默认黑色文字 */
        padding: 8px 12px; /* 增大点击区域，避免误触 */
    }
    QMenu::item:selected {
        background-color: #4a90e2;
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

# 不同消息，“角色名称”部分的样式
MESSAGE_STYLES = {
    "": """color: #4A90E2;""",
    "assistant": """color: #50B7C1;""",
    "user": """color: #888;""",
    "system": """color: #4A90E2;""",
    "option": """color: black;""",
    "text": """color: black;""",
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
    "option": """
    #buttonContainer {
        background-color: #F3DEFF;
    }
    QPushButton {
        background-color: #F3DEFF;
        color: #6B6B6B;
        border: none;
        border-radius: 8px;
        padding: 8px 15px;
        font-family: Microsoft YaHei;
        min-width: 120px;
    }
    QPushButton:hover {
        background-color: #EED0FD;
        color: black;
        font-weight: bold;
        text-decoration: underline;
    }
    QPushButton:pressed {
        background-color: #E6C8F5;
        color: black;
        font-weight: bold;
        text-decoration: underline;
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
            color: #333;
            font-size: 11pt;
        }
    """,
    "assistant_thinking": """
        QTextBrowser {
            background-color: #FFFFF0;
            border: 1px solid #E0D5B0;
            border-radius: 8px;
            padding: 12px;
            color: #555;
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
        QTextBrowser {
            color: black;
            background-color: white;
            border: 1px solid black;
            border-radius: 4px;
            padding: 10px;
        }
    """,
    "default": """
        QTextBrowser {
            background-color: #FCF9F5; /* 接近米色的浅暖色调，像旧书页的质感 */
            border: 1px solid #EFE6DD; /* 淡奶茶色边框，柔和不突兀 */
            border-radius: 8px;
            padding: 12px;
            color: #4A3A29;
            font-size: 11pt;
        }
    """,
    "text": """
        color: black;
        background-color: white;
        border: 1px solid black;
        border-radius: 4px;
        padding: 10px;
    """,
}
