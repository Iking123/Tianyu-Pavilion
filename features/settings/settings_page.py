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
    QTabWidget,
)
from PyQt6.QtGui import QIcon, QFont, QDoubleValidator, QIntValidator
from PyQt6.QtCore import Qt, QTimer
from core.config_manager import *
from ui.components import GoBackButton
from translate import TRANSLATE
from ui.main_window import MainWindow


class UserSet(QWidget):
    """用户信息设置"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # 表单布局
        form_layout = QFormLayout(self)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(200, 200, 200, 15)
        empty_space = QWidget()
        empty_space.setMinimumHeight(30)

        # 用户信息设置
        parent.username_input = QLineEdit()
        parent.username_input.setMaxLength(5)
        parent.username_input.setPlaceholderText("输入 用户名")
        parent.username_input.setToolTip("至多5个字符")
        parent.username_input.setText(get_username(False))
        form_layout.addRow("用户名：", parent.username_input)

        form_layout.addRow(empty_space)


class APISet(QWidget):
    """API设置"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # 表单布局
        form_layout = QFormLayout(self)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(200, 200, 200, 15)
        empty_space = QWidget()
        empty_space.setMinimumHeight(30)

        # API设置
        parent.deepseek_api_key_input = QLineEdit()
        parent.deepseek_api_key_input.setPlaceholderText("输入 DeepSeek API 密钥")
        parent.deepseek_api_key_input.setText(get_config("deepseek_api_key"))
        form_layout.addRow("DeepSeek API 密钥:", parent.deepseek_api_key_input)

        parent.volcengine_api_key_input = QLineEdit()
        parent.volcengine_api_key_input.setPlaceholderText(
            "输入火山方舟（豆包）API 密钥"
        )
        parent.volcengine_api_key_input.setText(get_config("volcengine_api_key"))
        form_layout.addRow("火山方舟（豆包）API 密钥:", parent.volcengine_api_key_input)

        parent.gemini_api_key_input = QLineEdit()
        parent.gemini_api_key_input.setPlaceholderText("输入 Gemini API 密钥")
        parent.gemini_api_key_input.setText(get_config("gemini_api_key"))
        form_layout.addRow("Gemini API 密钥:", parent.gemini_api_key_input)

        parent.glm_api_key_input = QLineEdit()
        parent.glm_api_key_input.setPlaceholderText("输入智谱（GLM） API 密钥")
        parent.glm_api_key_input.setText(get_config("glm_api_key"))
        form_layout.addRow("智谱（GLM） API 密钥:", parent.glm_api_key_input)

        parent.mistral_api_key_input = QLineEdit()
        parent.mistral_api_key_input.setPlaceholderText("输入 Mistral API 密钥")
        parent.mistral_api_key_input.setText(get_config("mistral_api_key"))
        form_layout.addRow("Mistral API 密钥:", parent.mistral_api_key_input)

        parent.tavily_api_key_input = QLineEdit()
        parent.tavily_api_key_input.setPlaceholderText("输入 Tavily API 密钥")
        parent.tavily_api_key_input.setText(get_config("tavily_api_key"))
        form_layout.addRow("Tavily API 密钥:", parent.tavily_api_key_input)

        form_layout.addRow(empty_space)


class FeatureSet(QWidget):
    """功能设置"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # 表单布局
        form_layout = QFormLayout(self)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(200, 200, 200, 15)
        empty_space = QWidget()
        empty_space.setMinimumHeight(30)

        # 功能设置
        parent.tavily_checkbox = QCheckBox()
        parent.tavily_checkbox.setChecked(get_config("enable_tavily"))
        form_layout.addRow("启用 Tavily 搜索：", parent.tavily_checkbox)

        parent.baidu_combobox = QComboBox()
        parent.baidu_combobox.addItems(["自动", "开", "关闭"])
        parent.baidu_combobox.setCurrentText(str(get_config("enable_baidu")))
        form_layout.addRow("启用百度搜索：", parent.baidu_combobox)

        parent.thinking_checkbox = QCheckBox()
        parent.thinking_checkbox.setChecked(get_config("enable_thinking"))
        form_layout.addRow(
            "启用深度思考（DeepSeek等）：",
            parent.thinking_checkbox,
        )

        parent.reasoning_combobox = QComboBox()
        parent.reasoning_combobox.addItems(["无", "低", "中", "高"])
        parent.reasoning_combobox.setCurrentText(
            TRANSLATE.get(str(get_config("reasoning_effort")), "无")
        )
        form_layout.addRow("深度程度（豆包）：", parent.reasoning_combobox)

        parent.sp_checkbox = QCheckBox()
        parent.sp_checkbox.setChecked(get_config("sp") or False)
        if get_username(False) in ["Iking", "雨落流绮"]:
            form_layout.addRow("启用 SP 模式：", parent.sp_checkbox)

        # 滚动速度
        parent.speed_slider_input = QComboBox()
        parent.speed_slider_input.addItems([str(i) for i in range(1, 16)])
        parent.speed_slider_input.setCurrentText(str(get_config("speed_slider")))
        form_layout.addRow("鼠标滚动速度：", parent.speed_slider_input)

        parent.ex_scroll_step_input = QLineEdit()
        parent.ex_scroll_step_input.setValidator(QIntValidator())
        parent.ex_scroll_step_input.setToolTip("请输入一个整数")
        parent.ex_scroll_step_input.setText(str(get_config("ex_scroll_step")))
        form_layout.addRow("上下键额外滚动步长：", parent.ex_scroll_step_input)

        form_layout.addRow(empty_space)


class SettingsPage(QWidget):
    """设置功能页面"""

    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        # 保存初始滚动速度用于比较
        self.initial_speed_slider = get_config("speed_slider")
        self.initial_ex_scroll_step = get_config("ex_scroll_step")

        # 使用垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === 顶部工具栏 ===
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F0F2F5; padding: 10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 返回按钮
        self.back_button = GoBackButton(self)
        toolbar_layout.addWidget(self.back_button)

        # 页面标题
        title_label = QLabel("设置")
        title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 居中布局
        button_width = self.back_button.width()
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
        main_layout.addWidget(toolbar)

        self.tabs = QTabWidget()
        self.tabs.addTab(UserSet(self), "用户信息设置")
        self.tabs.addTab(APISet(self), "API设置")
        self.tabs.addTab(FeatureSet(self), "功能设置")
        main_layout.addWidget(self.tabs, 1)  # 添加并设置拉伸因子为1

        # 启用TabBar扩展（均分宽度），清除默认样式
        tab_bar = self.tabs.tabBar()
        tab_bar.setExpanding(True)  # 关键：让每个标签均分TabBar宽度
        tab_bar.setDocumentMode(True)  # 简化TabBar样式，减少默认留白

        # 优化样式表：确保标签无留白、均匀分布
        self.tabs.setStyleSheet(
            """
            /* 清除TabBar的默认内边距和外边距，避免标签靠左 */
            QTabBar {
                padding: 0px;
                margin: 0px;
                border: none;
            }
            
            /* 配置每个标签的样式：无间距、文字居中、均分宽度 */
            QTabBar::tab {
                min-height: 40px;  /* 最小高度40px */
                padding: 15px 20px; /* 上下内边距15px，左右20px，让文字不贴边 */
                margin: 0px;           /* 清除标签之间的默认间距 */
                text-align: center;    /* 文字居中显示 */
                border: none;          /* 清除默认边框 */
                border-radius: 8px;
                color: #6B6B6B;
            }
            
            /* 最后一个标签去掉右边框，避免多余线条 */
            QTabBar::tab:last {
                border-right: none;
            }
            
            /* 选中标签的样式 */
            QTabBar::tab:selected {
                font-weight: bold;
                color: black;
            }
            
            /* 鼠标悬浮样式 */
            QTabBar::tab:hover:!selected {
                background-color: #EAECEF;
                color: black;
            }
            
            /* 清除TabWidget的默认边框，避免视觉留白 */
            QTabWidget::pane {
                border: none;
                padding: 0px;
            }
        """
        )

        # 获取QTabBar并设置手形光标
        tab_bar = self.tabs.tabBar()
        # 设置鼠标悬浮手形光标
        tab_bar.setCursor(Qt.CursorShape.PointingHandCursor)

        # 保存按钮（修改为"保存"）
        save_btn = QPushButton("保存")
        save_btn.setFont(QFont("zixiaohundanqingxingshu_trial", 25, QFont.Weight.Bold))
        save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-family: zixiaohundanqingxingshu_trial !important;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )
        save_btn.setMinimumSize(300, 120)
        main_layout.addWidget(save_btn, 1, Qt.AlignmentFlag.AlignRight)

        # 连接信号
        save_btn.clicked.connect(self.save_settings)

    def save_settings(self):
        """保存设置，不再自动重启"""
        # 检查滚动速度是否被修改
        try:
            new_speed = int(self.speed_slider_input.currentText())
            new_ex_scroll_step = int(self.ex_scroll_step_input.text().strip())
            speed_changed = (
                new_speed != self.initial_speed_slider
                or new_ex_scroll_step != self.initial_ex_scroll_step
            )
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
            mistral_api_key = self.mistral_api_key_input.text().strip()
            glm_api_key = self.glm_api_key_input.text().strip()
            enable_tavily = self.tavily_checkbox.isChecked()
            enable_baidu = self.baidu_combobox.currentText().strip()
            reasoning_effort = TRANSLATE.get(
                self.reasoning_combobox.currentText().strip(), "minimal"
            )
            sp = self.sp_checkbox.isChecked()
            speed_slider = int(self.speed_slider_input.currentText())
            ex_scroll_step = int(self.ex_scroll_step_input.text().strip())
        except Exception:
            QMessageBox.warning(self, "保存失败", "您可能输入错了什么东西？")
            return  # 报错则不保存

        # 构建新配置
        new_config = get_config().copy()
        new_config["username"] = username
        new_config["deepseek_api_key"] = deepseek_api_key
        new_config["volcengine_api_key"] = volcengine_api_key
        new_config["gemini_api_key"] = gemini_api_key
        new_config["mistral_api_key"] = mistral_api_key
        new_config["glm_api_key"] = glm_api_key
        new_config["tavily_api_key"] = tavily_api_key
        new_config["enable_tavily"] = enable_tavily
        new_config["enable_baidu"] = enable_baidu
        new_config["reasoning_effort"] = reasoning_effort
        new_config["speed_slider"] = speed_slider
        new_config["ex_scroll_step"] = ex_scroll_step
        if get_username(False) in ["Iking", "雨落流绮"]:
            new_config["sp"] = sp

        # 保存配置
        update_config(new_config)

        # 更新状态栏
        if self.main_window:
            self.main_window.btn_tavily.setChecked(enable_tavily)
            self.main_window.baidu_combobox.setCurrentText("百度搜索：" + enable_baidu)
            self.main_window.reasoning_combobox.setCurrentText(
                "深度思考：" + reasoning_effort
            )
            if speed_changed:
                self.main_window.update_status(
                    "设置已保存！需要重启天语阁才能使滚动速度生效"
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
        if hasattr(self, "tavily_checkbox"):
            self.tavily_checkbox.setChecked(get_config("enable_tavily"))
        if hasattr(self, "baidu_combobox"):
            self.baidu_combobox.setCurrentText(str(get_config("enable_baidu")))
        if hasattr(self, "reasoning_combobox"):
            self.reasoning_combobox.setCurrentText(
                TRANSLATE.get(str(get_config("reasoning_effort")), "无")
            )
