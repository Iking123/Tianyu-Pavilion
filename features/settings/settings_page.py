import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QMessageBox,
    QApplication,
)
from PyQt5.QtGui import QIcon, QFont, QDoubleValidator, QIntValidator
from PyQt5.QtCore import Qt, QTimer
from core.config_manager import *


class SettingsPage(QWidget):
    """设置功能页面"""

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
                background-color: #EA4335;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 8pt;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """
        )
        self.back_button.clicked.connect(self.go_back)

        # 页面标题
        title_label = QLabel("设置")
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

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(250, 15, 250, 15)
        empty_space = QWidget()
        empty_space.setMinimumHeight(200)
        empty_row = QLabel()

        # 用户信息设置
        api_label = QLabel("用户信息设置")
        api_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; margin-top: 20px; font-family: Microsoft YaHei;"
        )
        form_layout.addWidget(api_label)
        form_layout.addWidget(empty_row)

        self.username_input = QLineEdit()
        self.username_input.setMaxLength(5)
        self.username_input.setPlaceholderText("输入 用户名")
        self.username_input.setToolTip("至多5个字符")
        self.username_input.setText(get_username(False))
        form_layout.addRow("用户名：", self.username_input)

        form_layout.addRow(empty_space)

        # API设置
        api_label = QLabel("API设置")
        api_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; margin-top: 20px; font-family: Microsoft YaHei;"
        )
        form_layout.addWidget(api_label)
        form_layout.addWidget(empty_row)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 DeepSeek API 密钥")
        self.api_key_input.setText(get_config("api_key"))
        form_layout.addRow("DeepSeek API 密钥:", self.api_key_input)

        self.tavily_api_key_input = QLineEdit()
        self.tavily_api_key_input.setPlaceholderText("输入 Tavily API 密钥")
        self.tavily_api_key_input.setText(get_config("tavily_api_key"))
        form_layout.addRow("Tavily API 密钥:", self.tavily_api_key_input)

        form_layout.addRow(empty_space)

        # 功能设置
        feature_label = QLabel("功能设置")
        feature_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; margin-top: 20px; font-family: Microsoft YaHei;"
        )
        form_layout.addWidget(feature_label)
        form_layout.addWidget(empty_row)

        self.r1_checkbox = QCheckBox("启用 R1 深度思考")
        self.r1_checkbox.setChecked(get_config("enable_r1"))
        form_layout.addRow(self.r1_checkbox)

        self.tavily_checkbox = QCheckBox("启用 Tavily 搜索")
        self.tavily_checkbox.setChecked(get_config("enable_tavily"))
        form_layout.addRow(self.tavily_checkbox)

        self.baidu_checkbox = QCheckBox("启用百度搜索")
        self.baidu_checkbox.setChecked(get_config("enable_baidu"))
        form_layout.addRow(self.baidu_checkbox)

        # 鼠标滚动速度输入栏
        self.speed_slider_input = QComboBox()
        self.speed_slider_input.addItems([str(i) for i in range(1, 16)])
        self.speed_slider_input.setCurrentText(str(get_config("speed_slider")))
        form_layout.addRow("鼠标滚动速度：", self.speed_slider_input)

        form_layout.addRow(empty_space)

        layout.addLayout(form_layout)

        # 保存按钮
        save_btn = QPushButton("保存并重启")
        save_btn.setFont(QFont("Microsoft Yahei", 12, QFont.Bold))
        save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )
        layout.addWidget(save_btn, 0, Qt.AlignRight)

        # 连接信号
        save_btn.clicked.connect(self.save_settings)

    def save_settings(self):
        """保存设置，然后重启应用"""
        reply = QMessageBox.question(
            self,
            "确认保存",
            "是否保存？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return  # 用户取消

        # 获取输入值
        try:
            username = self.username_input.text().strip()
            api_key = self.api_key_input.text().strip()
            tavily_api_key = self.tavily_api_key_input.text().strip()
            enable_r1 = self.r1_checkbox.isChecked()
            enable_tavily = self.tavily_checkbox.isChecked()
            enable_baidu = self.baidu_checkbox.isChecked()
            speed_slider = int(self.speed_slider_input.currentText())
        except Exception:
            QMessageBox.warning(self, "保存失败", "您可能输入错了什么东西？")
            return  # 报错则不保存

        # 构建新配置
        new_config = get_config().copy()
        new_config["username"] = username
        new_config["api_key"] = api_key
        new_config["tavily_api_key"] = tavily_api_key
        new_config["enable_r1"] = enable_r1
        new_config["enable_tavily"] = enable_tavily
        new_config["enable_baidu"] = enable_baidu
        new_config["speed_slider"] = speed_slider  # 保存鼠标滚动速度

        # 保存配置
        update_config(new_config)
        self.main_window.update_status("设置已保存，应用即将重启...")

        # 延迟重启，让用户看到提示
        QTimer.singleShot(1500, self.restart_application)  # 1.5秒后重启

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)

    def restart_application(self):
        """重启应用程序"""
        # 关闭当前应用
        if self.main_window:
            self.main_window.close()

        # 重启应用
        python = sys.executable  # 获取当前Python解释器路径
        script = os.path.join(os.getcwd(), "main.py")  # 主程序路径

        # 使用subprocess启动新进程
        subprocess.Popen([python, script])

        # 退出当前进程
        QApplication.quit()
