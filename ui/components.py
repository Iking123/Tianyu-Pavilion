from PyQt6.QtWidgets import QWidget, QPushButton, QTextBrowser, QLabel
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QPainterPath,
    QPen,
    QColor,
    QPaintEvent,
    QBrush,
)
from PyQt6.QtCore import QSize, Qt, QEvent, QPointF, QRectF
from funcs import resource_path


class ImageWidget(QLabel):
    def __init__(self, img: str | QPixmap, h: int | None = None):
        super().__init__()
        if isinstance(img, str):
            img = QPixmap(img)
        if h:
            img = img.scaledToHeight(h)
        self.setPixmap(img)


class ColoredWidget(QWidget):
    def __init__(self, color: QColor = QColor("#F5F7FA")):
        super().__init__()
        self.backgroundColor = color

    def setBackgroundColor(self, color: str):
        self.backgroundColor = QColor(color)
        self.setStyleSheet(f"background-color: {color}")
        self.update()  # 触发重绘

    def paintEvent(self, event: QPaintEvent):
        # 创建绘制器
        painter = QPainter(self)

        # 设置抗锯齿渲染
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 填充背景色
        painter.fillRect(self.rect(), self.backgroundColor)

        # # 可选：添加边框
        # painter.setPen(Qt.GlobalColor.darkGray)
        # painter.drawRect(self.rect().adjusted(0, 0, -1, -1))


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

        # 设置手形
        self.setCursor(Qt.CursorShape.PointingHandCursor)

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

        # 设置手形
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if not callback and parent and hasattr(parent, "restart"):
            callback = parent.restart
        if callback:
            self.clicked.connect(callback)


class ZoomButton(QPushButton):
    """自定义缩放按钮组件"""

    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setFixedSize(54, 54)  # 固定按钮大小
        self.setIconSize(QSize(32, 32))  # 图标大小

        # 使用资源路径加载图标
        self.minimize_icon = QIcon(resource_path("resources/images/minimize.png"))
        self.maximize_icon = QIcon(resource_path("resources/images/maximize.png"))
        self.setIcon(self.minimize_icon)
        self.status = True

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border-radius: 15px;
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
        self.setToolTip("缩小")

        # 设置手形
        self.setCursor(Qt.CursorShape.PointingHandCursor)

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

        # 设置默认光标为箭头
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _create_custom_icon(self):
        """创建自定义箭头图标"""
        # 创建 QPixmap 作为画布
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)  # 透明背景

        # 创建画笔
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

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
        pen = QPen(Qt.GlobalColor.white)  # 白色线条
        pen.setWidth(4)  # 设置线宽
        painter.setPen(pen)  # 应用画笔

        # 不需要填充（移除原有的填充设置）
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 绘制路径
        painter.drawPath(path)
        painter.end()

        # 设置图标
        self.setIcon(QIcon(pixmap))

    def setEnabled(self, enabled):
        """重写setEnabled方法，在状态改变时更新图标颜色"""
        super().setEnabled(enabled)
        # 可以在这里根据enabled状态调整图标颜色，但由于背景色已通过CSS控制，这里暂不需要额外处理

    # 当鼠标进入按钮区域时
    def enterEvent(self, event):
        if self.isEnabled():  # 只在按钮可用时显示手形
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    # 当鼠标离开按钮区域时
    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # 恢复默认光标
        super().leaveEvent(event)


class ScrollToBottomButton(QPushButton):
    """自定义滚动到底部按钮组件，使用QPainterPath绘制向下箭头"""

    def __init__(self, parent=None, tip="滚动到底部", callback=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)  # 固定按钮大小
        self.setIconSize(QSize(60, 60))  # 图标大小

        # 创建自定义图标
        self._create_custom_icons()

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 36);
                border: 2px solid #CCCCCC;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """
        )

        # 设置工具提示
        self.setToolTip(tip)

        if callback:
            self.clicked.connect(callback)

    def _create_custom_icons(self):
        """创建正常状态和悬停状态的自定义向下箭头图标"""
        # 创建正常状态图标
        self.normal_icon = self._create_arrow_icon(Qt.GlobalColor.darkGray)
        self.hover_icon = self._create_arrow_icon(Qt.GlobalColor.black)

        # 设置默认图标
        self.setIcon(QIcon(self.normal_icon))

    def _create_arrow_icon(self, color):
        """创建指定颜色的向下箭头图标"""
        # 创建 QPixmap 作为画布
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.GlobalColor.transparent)  # 透明背景

        # 创建画笔
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

        # 创建向下箭头路径 (⌵ 形状)
        path = QPainterPath()

        # 箭头的中心位置
        center_x = 30
        center_y = 30

        # 定义向下箭头的路径点
        # 左上点
        path.moveTo(center_x - 10, center_y - 5)
        # 底部点
        path.lineTo(center_x, center_y + 5)
        # 右上点
        path.lineTo(center_x + 10, center_y - 5)

        # 设置画笔样式
        pen = QPen(color)
        pen.setWidth(3)  # 设置线宽
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # 圆形端点
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)  # 圆形连接
        painter.setPen(pen)

        # 不填充，只绘制线条
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 绘制路径
        painter.drawPath(path)
        painter.end()

        return pixmap

    def enterEvent(self, event):
        """鼠标进入事件，切换到悬停图标"""
        self.setIcon(QIcon(self.hover_icon))
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件，切换回正常图标"""
        self.setIcon(QIcon(self.normal_icon))
        super().leaveEvent(event)


class CustomTextBrowser(QTextBrowser):
    def __init__(self, parent=None, tp=Qt.CursorShape.IBeamCursor):
        super().__init__(parent)
        self.tp = tp
        self.viewport().setCursor(tp)
        # 安装事件过滤器到视口（监控鼠标移动事件）
        self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        # 仅处理视口的鼠标移动事件
        if (
            obj == self.viewport()
            and event.type() == QEvent.Type.MouseMove
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
