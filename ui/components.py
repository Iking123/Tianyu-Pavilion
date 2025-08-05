from PyQt5.QtWidgets import QPushButton, QTextBrowser
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QPen
from PyQt5.QtCore import QSize, Qt, QEvent
from funcs import resource_path


class GoBackButton(QPushButton):
    """自定义返回按钮组件"""

    def __init__(self, parent=None, tip="返回主页", callback=None):
        super().__init__(parent)
        self.setFixedSize(70, 70)  # 固定按钮大小
        self.setIconSize(QSize(28, 28))  # 图标大小

        # 使用资源路径加载图标
        self.setIcon(QIcon(resource_path("resources/images/goback.png")))

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border-radius: 35px;  /* 圆形按钮 */
            }
            QPushButton:hover {
                background-color: #E0E0E0;  /* 鼠标悬停时的灰色背景 */
            }
            QPushButton:pressed {
                background-color: #C0C0C0;  /* 按下时稍深的灰色 */
            }
        """
        )

        # 设置工具提示
        self.setToolTip(tip)

        if not callback and parent and hasattr(parent, "go_back"):
            callback = parent.go_back
        if callback:
            self.clicked.connect(callback)


class RestartButton(QPushButton):
    """自定义重来按钮组件"""

    def __init__(self, parent=None, tip="开始新对话", callback=None):
        super().__init__(parent)
        self.setFixedSize(70, 70)  # 固定按钮大小
        self.setIconSize(QSize(28, 28))  # 图标大小

        # 使用资源路径加载图标
        self.setIcon(QIcon(resource_path("resources/images/restart.svg")))

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border-radius: 35px;  /* 圆形按钮 */
            }
            QPushButton:hover {
                background-color: #E0E0E0;  /* 鼠标悬停时的灰色背景 */
            }
            QPushButton:pressed {
                background-color: #C0C0C0;  /* 按下时稍深的灰色 */
            }
        """
        )

        # 设置工具提示
        self.setToolTip(tip)

        if not callback and parent and hasattr(parent, "restart"):
            callback = parent.restart
        if callback:
            self.clicked.connect(callback)


class SendButton(QPushButton):
    """自定义发送按钮组件，使用QPainterPath绘制箭头"""

    def __init__(self, parent=None, tip="", callback=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)  # 固定按钮大小
        self.setIconSize(QSize(64, 64))  # 图标大小

        # 创建自定义图标
        self._create_custom_icon()

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #007AFF;  /* 蓝色背景 */
                border-radius: 32px;  /* 圆形按钮 */
                border: none;
            }
            QPushButton:hover {
                background-color: #005BB5;  /* 鼠标悬停时的深蓝色背景 */
            }
            QPushButton:pressed {
                background-color: #004A9A;  /* 按下时更深的蓝色 */
            }
            QPushButton:disabled {
                background-color: #CCCCCC;  /* 禁用时的灰色背景 */
            }
        """
        )

        # 设置工具提示
        if tip:
            self.setToolTip(tip)

        if not callback and parent and hasattr(parent, "on_send_clicked"):
            callback = parent.on_send_clicked
        if callback:
            self.clicked.connect(callback)

    def _create_custom_icon(self):
        """创建自定义箭头图标"""
        # 创建 QPixmap 作为画布
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)  # 透明背景

        # 创建画笔
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        # 创建箭头路径
        path = QPainterPath()

        # 调整坐标以适应64x64的画布，并创建向上的箭头
        scale = 1.0  # 缩放因子
        offset_x = 32  # x偏移，使箭头居中
        offset_y = 32  # y偏移，使箭头居中

        # 定义向上箭头的路径点
        path.moveTo(offset_x, offset_y - 13 * scale)  # 箭头顶点
        path.lineTo(offset_x - 10 * scale, offset_y - 5 * scale)  # 左侧点
        path.moveTo(offset_x, offset_y - 13 * scale)  # 箭头顶点
        path.lineTo(offset_x, offset_y + 13 * scale)  # 中轴
        path.moveTo(offset_x, offset_y - 13 * scale)  # 箭头顶点
        path.lineTo(offset_x + 10 * scale, offset_y - 5 * scale)  # 右侧点

        # 设置画笔样式（这是关键修改！）
        pen = QPen(Qt.white)  # 白色线条
        pen.setWidth(4)  # 设置线宽
        painter.setPen(pen)  # 应用画笔

        # 不需要填充（移除原有的填充设置）
        painter.setBrush(Qt.NoBrush)

        # 绘制路径
        painter.drawPath(path)
        painter.end()

        # 设置图标
        self.setIcon(QIcon(pixmap))

    def setEnabled(self, enabled):
        """重写setEnabled方法，在状态改变时更新图标颜色"""
        super().setEnabled(enabled)
        # 可以在这里根据enabled状态调整图标颜色，但由于背景色已通过CSS控制，这里暂不需要额外处理


class CustomTextBrowser(QTextBrowser):
    def __init__(self, parent=None, tp=Qt.IBeamCursor):
        super().__init__(parent)
        self.tp = tp
        self.viewport().setCursor(tp)
        # 安装事件过滤器到视口（监控鼠标移动事件）
        self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        # 仅处理视口的鼠标移动事件
        if (
            obj == self.viewport()
            and event.type() == QEvent.MouseMove
            and self.cursor().shape() != self.tp
        ):
            # 获取鼠标位置对应的文本光标
            cursor = self.cursorForPosition(event.pos())
            # 检查光标下是否为链接（通过文本光标获取字符格式）
            char_format = cursor.charFormat()
            if char_format.isAnchor():  # 若为链接
                # 沿用默认处理
                return super().eventFilter(obj, event)
            self.viewport().setCursor(self.tp)

        # 默认处理
        return super().eventFilter(obj, event)

    def enterEvent(self, event):
        self.viewport().setCursor(self.tp)
