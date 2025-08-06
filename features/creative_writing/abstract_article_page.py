from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.components import GoBackButton, RestartButton
from ui.message_display import MessageDisplayArea
from ui.my_slider import MySlider
from .bullshit import BullshitWorker
from ui.main_window import MainWindow


class AbstractArticlePage(QWidget):
    """抽象作文页面"""

    def __init__(self, main_window: MainWindow):
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

        # 顶部按钮
        self.back_button = GoBackButton(self, "返回写作列表")
        self.restart_button = RestartButton(self)

        # 页面标题
        title_label = QLabel("抽象作文生成器")
        title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        button_width = self.back_button.width() + 10 + self.restart_button.width()
        toolbar_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        toolbar_layout.addWidget(
            self.restart_button, alignment=Qt.AlignmentFlag.AlignLeft
        )
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        toolbar_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addSpacerItem(
            QSpacerItem(
                button_width, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )
        )
        toolbar_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        layout.addWidget(toolbar)

        # 输入区域
        input_layout = QFormLayout()
        input_layout.setVerticalSpacing(15)  # 增加垂直间距

        heading_label = QLabel("作文标题：")
        heading_label.setStyleSheet(
            "font-size: 16pt; margin-left: 10px;"
        )  # 给标签添加左边距
        self.heading_input = QLineEdit()
        self.heading_input.setPlaceholderText("输入作文标题...")
        self.heading_input.setStyleSheet("font-size: 16pt; margin: 5px 20px 0px 20px;")
        input_layout.addRow(heading_label, self.heading_input)

        self.length_input = MySlider(
            self, 0, 10000, 100, 300, 1000, "字数要求： ", 16, "字", 950
        )
        input_layout.addRow(self.length_input)

        layout.addLayout(input_layout)
        layout.addSpacing(50)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("生成作文")
        self.generate_btn.setStyleSheet(
            """
            QPushButton {
                font-family: 'DFPShaoNvW5-GB';
                background-color: #34A853;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 28pt;
            }
            QPushButton:hover {
                background-color: #3A7BC8;
            }
        """
        )
        button_layout.addWidget(self.generate_btn)
        layout.addLayout(button_layout)
        layout.addSpacing(50)

        # 输出区域
        self.output_layout = MessageDisplayArea()
        output_label = QLabel("生成结果：")
        output_label.setStyleSheet("font-size: 16pt; margin-bottom: 5px;")
        self.output_layout.container_layout.addWidget(output_label)
        self.output_message = None
        layout.addWidget(self.output_layout)

        # 连接信号
        self.generate_btn.clicked.connect(self.generate_article)

    def generate_article(self):
        """生成作文内容"""
        prompt = self.heading_input.text().strip()
        if not prompt:
            QMessageBox.warning(self, "输入错误", "请输入标题！")
            return
        length = self.length_input.value
        self.worker = BullshitWorker(prompt, length)
        self.worker.update_signal.connect(
            self.add_message_content, Qt.ConnectionType.QueuedConnection
        )
        self.worker.status_signal.connect(
            self.main_window.set_status, Qt.ConnectionType.QueuedConnection
        )
        self.output_message = self.output_layout.add_message_by_role(
            "", f"# {prompt}\r\n"
        )
        self.worker.start()

    def add_message_content(self, content):
        self.output_message.append_content(content, True)

    def go_back(self):
        """返回写作列表"""
        if self.main_window:
            self.main_window.switch_to_writing_list()

    def restart(self):
        """重来"""
        # 创建确认对话框
        reply = QMessageBox.question(
            self,
            "确认重来",
            "即将清除已有作文并恢复初始作文设置，确定执行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        # 如果用户选择否，则取消操作
        if reply == QMessageBox.StandardButton.No:
            # 使用主窗口设置状态
            if self.main_window:
                self.main_window.set_status("重来操作已取消")
            return

        # 停止当前工作线程
        if hasattr(self, "worker") and self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        # 清除作文
        self.output_layout.clear_messages()

        # 恢复初始设置
        self.heading_input.setText("")
        self.length_input.slider.setValue(950)
        output_label = QLabel("生成结果：")
        output_label.setStyleSheet("font-size: 16pt; margin-bottom: 5px;")
        self.output_layout.container_layout.addWidget(output_label)
        if self.main_window:
            self.main_window.set_status("就绪")
