import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from funcs import get_screen_height, resource_path


class NoneBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: none !important;")


class HomePage(QWidget):
    """主页面，显示四个功能方块和中央设置按钮"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        # 主布局
        grid_layout = QGridLayout(self)

        screen_height = get_screen_height()
        grid_layout.setSpacing(int(screen_height * 0.02))
        margin = int(screen_height * 0.11)
        grid_layout.setContentsMargins(margin, 0, margin, 0)

        # 标题区域
        self.title_area = NoneBackgroundWidget()
        title_layout = QVBoxLayout(self.title_area)
        title_label = QLabel("天语阁")
        title_label.setFont(QFont("DFPShaoNvW5-GB", 48, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 添加 !important 和显式 font-family，避免被main.py中的全局样式表覆盖
        title_label.setStyleSheet(
            f"color: white !important; margin-bottom: 10px; font-family: 'DFPShaoNvW5-GB' !important;"
        )

        subtitle_label = QLabel("Created by Iking")
        subtitle_label.setFont(QFont(".Heiti J", 20))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(
            f"color: silver; margin-bottom: 40px; font-family: '.Heiti J' !important;"
        )

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        empty_space = NoneBackgroundWidget()
        title_layout.addWidget(empty_space)
        grid_layout.addWidget(self.title_area, 0, 0, 1, -1)

        # 创建所有按钮
        self.chat_btn = self.create_circle_button("聊天", "#62B4EB")
        self.creative_btn = self.create_circle_button("创意写作", "#CA84E6")
        self.interactive_btn = self.create_circle_button("交互小说", "#f2c063")
        self.game_btn = self.create_circle_button("小游戏", "#4ace71")
        self.character_btn = self.create_circle_button("角色编辑器", "#8F97BB")
        self.settings_btn = self.create_circle_button("设置", "#95a5a6")

        grid_layout.addWidget(self.chat_btn, 1, 0)
        grid_layout.addWidget(self.creative_btn, 1, 1)
        grid_layout.addWidget(self.game_btn, 1, 2)
        grid_layout.addWidget(self.interactive_btn, 2, 0)
        grid_layout.addWidget(self.character_btn, 2, 1)
        grid_layout.addWidget(self.settings_btn, 2, 2)

        # 连接信号
        self.chat_btn.clicked.connect(lambda: self.switch_to_page(1))
        self.game_btn.clicked.connect(lambda: self.switch_to_page(2))
        self.interactive_btn.clicked.connect(lambda: self.switch_to_page(3))
        self.creative_btn.clicked.connect(lambda: self.switch_to_page(4))
        self.settings_btn.clicked.connect(
            lambda: self.switch_to_page(5)
        )  # 连接到设置页面
        self.character_btn.clicked.connect(
            lambda: self.switch_to_page(6)
        )  # 连接到角色编辑器页面

        # 设置动画效果
        self.setup_animations()

        # 页脚区域（设置成与标题区域所占空间相同）
        self.footer_area = NoneBackgroundWidget()
        grid_layout.addWidget(self.footer_area, 3, 0, 1, -1)

        grid_layout.setRowStretch(0, 27)
        grid_layout.setRowStretch(1, 7)
        grid_layout.setRowStretch(2, 7)
        grid_layout.setRowStretch(3, 29)

    def create_circle_button(self, text="", color="#95a5a6"):
        """创建带阴影的圆形按钮"""
        button = QPushButton()  # 只用图标，不要显示字！
        button.setFixedSize(200, 200)  # 稍微缩小以适应两个按钮
        button.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))

        # 根据按钮类型设置不同的背景图片
        img_map = {
            "聊天": "chat_bg.png",
            "小游戏": "game_bg.png",
            "交互小说": "interactive_bg.png",
            "创意写作": "creative_writing_bg.png",
            "设置": "settings_bg.png",
            "角色编辑器": "character_bg.png",
        }
        img_filename = img_map.get(text, "settings_bg.png")  # 用设置图标当默认图片

        # 使用resource_path处理图片路径
        img_path = resource_path(os.path.join("resources", "images", img_filename))

        # 渐变色
        base_color = QColor(color)
        darker_color = base_color.darker(110)
        lighter_color = base_color.lighter(130)

        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {lighter_color.name()}, stop:1 {darker_color.name()});
                border-radius: 100px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                font-weight: bold;
                text-align: center;
                border-image: url({img_path}) 0 0 0 0 stretch stretch;
            }}
            QPushButton:hover {{
                background-color: {base_color.name()};
                border: 2px solid #FFFF00;
            }}
            QPushButton:pressed {{
                background-color: {darker_color.name()};
            }}
        """
        )

        button.setCursor(Qt.CursorShape.PointingHandCursor)

        # 添加阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 60))
        button.setGraphicsEffect(shadow)

        # 保存阴影效果的引用，用于动画
        button.shadow_effect = shadow

        return button

    def switch_to_page(self, index):
        """切换到指定页面"""
        if self.main_window:
            self.main_window.switch_page(index)

    def setup_animations(self):
        """设置按钮动画效果"""
        # 圆形按钮悬停动画
        for btn in [
            self.chat_btn,
            self.game_btn,
            self.interactive_btn,
            self.creative_btn,
            self.settings_btn,
            self.character_btn,
        ]:

            def circle_enter(e, b=btn):
                # 增加阴影效果
                b.shadow_effect.setBlurRadius(30)
                b.shadow_effect.setOffset(0, 15)

            def circle_leave(e, b=btn):
                # 恢复阴影效果
                b.shadow_effect.setBlurRadius(15)
                b.shadow_effect.setOffset(0, 12)

            btn.enterEvent = circle_enter
            btn.leaveEvent = circle_leave

    def paintEvent(self, event):
        """
        重写paintEvent来直接绘制背景图，以绕过样式表冲突。
        """
        painter = QPainter(self)
        pixmap = QPixmap(resource_path("resources/images/home.jpg"))

        if not pixmap.isNull():
            # 将图片绘制到窗口的整个区域 (self.rect())
            painter.drawPixmap(self.rect(), pixmap)

        # 调用父类的paintEvent，确保子控件（如按钮）也能被正确绘制
        super().paintEvent(event)
