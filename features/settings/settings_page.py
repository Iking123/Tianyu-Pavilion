import sys
import os
import subprocess
from PyQt6.QtWidgets import (
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
from PyQt6.QtGui import QIcon, QFont, QDoubleValidator, QIntValidator
from PyQt6.QtCore import Qt, QTimer
from core.config_manager import *
from ui.components import GoBackButton
from translate import TRANSLATE
from ui.main_window import MainWindow


class SettingsPage(QWidget):
    """设置功能页面"""

    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        # 保存初始滚动速度用于比较
        self.initial_speed_slider = get_config("speed_slider")

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
        self.back_button = GoBackButton(self)

        # 页面标题
        title_label = QLabel("设置")
        title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 获取返回按钮的宽度作为占位宽度
        button_width = self.back_button.sizeHint().width()

        toolbar_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
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

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(250, 15, 250, 15)
        empty_space = QWidget()
        empty_space.setMinimumHeight(120)
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

        self.deepseek_api_key_input = QLineEdit()
        self.deepseek_api_key_input.setPlaceholderText("输入 DeepSeek API 密钥")
        self.deepseek_api_key_input.setText(get_config("deepseek_api_key"))
        form_layout.addRow("DeepSeek API 密钥:", self.deepseek_api_key_input)

        self.volcengine_api_key_input = QLineEdit()
        self.volcengine_api_key_input.setPlaceholderText("输入火山方舟（豆包）API 密钥")
        self.volcengine_api_key_input.setText(get_config("volcengine_api_key"))
        form_layout.addRow("火山方舟（豆包）API 密钥:", self.volcengine_api_key_input)

        self.gemini_api_key_input = QLineEdit()
        self.gemini_api_key_input.setPlaceholderText("输入 Gemini API 密钥")
        self.gemini_api_key_input.setText(get_config("gemini_api_key"))
        form_layout.addRow("Gemini API 密钥:", self.gemini_api_key_input)

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

        self.tavily_checkbox = QCheckBox()
        self.tavily_checkbox.setChecked(get_config("enable_tavily"))
        form_layout.addRow("启用 Tavily 搜索：", self.tavily_checkbox)

        self.baidu_combobox = QComboBox()
        self.baidu_combobox.addItems(["自动", "开", "关闭"])
        self.baidu_combobox.setCurrentText(str(get_config("enable_baidu")))
        form_layout.addRow("启用百度搜索：", self.baidu_combobox)

        self.thinking_combobox = QComboBox()
        self.thinking_combobox.addItems(["自动", "开", "关闭"])
        self.thinking_combobox.setCurrentText(
            TRANSLATE.get(str(get_config("thinking_type")), "关闭")
        )
        form_layout.addRow(
            "启用深度思考（豆包1.6、Gemini Flash）：", self.thinking_combobox
        )

        # 鼠标滚动速度输入栏
        self.speed_slider_input = QComboBox()
        self.speed_slider_input.addItems([str(i) for i in range(1, 16)])
        self.speed_slider_input.setCurrentText(str(get_config("speed_slider")))
        form_layout.addRow("鼠标滚动速度：", self.speed_slider_input)

        form_layout.addRow(empty_space)

        layout.addLayout(form_layout)

        # 保存按钮（修改为"保存"）
        save_btn = QPushButton("保存")
        save_btn.setFont(QFont("Microsoft Yahei", 12, QFont.Weight.Bold))
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
        layout.addWidget(save_btn, 0, Qt.AlignmentFlag.AlignRight)

        # 连接信号
        save_btn.clicked.connect(self.save_settings)

    def save_settings(self):
        """保存设置，不再自动重启"""
        # 检查滚动速度是否被修改
        try:
            new_speed = int(self.speed_slider_input.currentText())
            speed_changed = new_speed != self.initial_speed_slider
        except:
            speed_changed = False

        # 根据滚动速度是否修改显示不同的提示
        message = "是否保存？" + ("（重启后生效）" if speed_changed else "")

        reply = QMessageBox.question(
            self,
            "确认保存",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return  # 用户取消

        # 获取输入值
        try:
            username = self.username_input.text().strip()
            tavily_api_key = self.tavily_api_key_input.text().strip()
            deepseek_api_key = self.deepseek_api_key_input.text().strip()
            volcengine_api_key = self.volcengine_api_key_input.text().strip()
            gemini_api_key = self.gemini_api_key_input.text().strip()
            enable_tavily = self.tavily_checkbox.isChecked()
            enable_baidu = self.baidu_combobox.currentText().strip()
            thinking_type = TRANSLATE.get(
                self.thinking_combobox.currentText().strip(), "disabled"
            )
            speed_slider = int(self.speed_slider_input.currentText())
        except Exception:
            QMessageBox.warning(self, "保存失败", "您可能输入错了什么东西？")
            return  # 报错则不保存

        # 构建新配置
        new_config = get_config().copy()
        new_config["username"] = username
        new_config["deepseek_api_key"] = deepseek_api_key
        new_config["volcengine_api_key"] = volcengine_api_key
        new_config["gemini_api_key"] = gemini_api_key
        new_config["tavily_api_key"] = tavily_api_key
        new_config["enable_tavily"] = enable_tavily
        new_config["enable_baidu"] = enable_baidu
        new_config["thinking_type"] = thinking_type
        new_config["speed_slider"] = speed_slider  # 保存鼠标滚动速度

        # 保存配置
        update_config(new_config)

        # 更新状态栏
        if self.main_window:
            self.main_window.btn_tavily.setChecked(enable_tavily)
            self.main_window.baidu_combobox.setCurrentText("百度搜索：" + enable_baidu)
            self.main_window.thinking_combobox.setCurrentText(
                "深度思考：" + thinking_type
            )
            if speed_changed:
                self.main_window.update_status(
                    "设置已保存！需要重启应用才能使鼠标滚动速度生效"
                )
            else:
                self.main_window.update_status("设置已保存！")

    def go_back(self):
        """返回主页"""
        if self.main_window:
            self.main_window.switch_page(0)

    def showEvent(self, event):
        """页面显示时刷新一些可通过状态栏更改的设置"""
        super().showEvent(event)
        self.tavily_checkbox.setChecked(get_config("enable_tavily"))
        self.baidu_combobox.setCurrentText(str(get_config("enable_baidu")))
        self.thinking_combobox.setCurrentText(
            TRANSLATE.get(str(get_config("thinking_type")), "关闭")
        )
