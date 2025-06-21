from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QTextEdit,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


class NovelPage(QWidget):
    """写小说功能页面"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F0F2F5; padding: 10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 返回按钮
        self.back_button = QPushButton("← 返回主页")
        self.back_button.setIcon(QIcon.fromTheme("go-previous"))
        self.back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )
        self.back_button.clicked.connect(self.go_back)

        # 页面标题
        title_label = QLabel("小说创作")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 获取返回按钮的宽度作为占位宽度
        button_width = self.back_button.sizeHint().width()

        toolbar_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        toolbar_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        toolbar_layout.addSpacerItem(
            QSpacerItem(button_width, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        )
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        layout.addWidget(toolbar)

        # 输入区域
        input_layout = QVBoxLayout()

        prompt_label = QLabel("创作提示:")
        prompt_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        input_layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("输入小说主题、风格或情节...")
        self.prompt_input.setMinimumHeight(100)
        input_layout.addWidget(self.prompt_input)

        layout.addLayout(input_layout)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("生成小说")
        self.generate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3A7BC8;
            }
        """
        )

        self.save_btn = QPushButton("保存小说")
        self.save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )

        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

        # 输出区域
        output_layout = QVBoxLayout()

        output_label = QLabel("生成结果:")
        output_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        output_layout.addWidget(output_label)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        output_layout.addWidget(self.output_area)

        layout.addLayout(output_layout)

        # 连接信号
        self.generate_btn.clicked.connect(self.generate_novel)

    def generate_novel(self):
        """生成小说内容"""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        # 这里可以调用API生成小说内容
        # 示例：
        self.output_area.setPlainText(f"正在根据提示生成小说: {prompt}...")

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)
