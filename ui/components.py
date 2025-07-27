from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QBrush, QPen
from PyQt5.QtCore import QSize, Qt
from funcs import resource_path


class GoBackButton(QPushButton):
    """自定义返回按钮组件"""

    def __init__(self, parent=None, tip="返回", callback=None):
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


class SendButton(QPushButton):
    """自定义发送按钮组件，使用QPainterPath绘制箭头"""

    def __init__(self, parent=None, tip="", callback=None):
        super().__init__(parent)
        self.setFixedSize(70, 70)  # 固定按钮大小
        self.setIconSize(QSize(70, 70))  # 图标大小

        # 创建自定义图标
        self._create_custom_icon()

        # 设置样式表
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #007AFF;  /* 蓝色背景 */
                border-radius: 35px;  /* 圆形按钮 */
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
        pixmap = QPixmap(70, 70)
        pixmap.fill(Qt.transparent)  # 透明背景

        # 创建画笔
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        # 创建箭头路径
        path = QPainterPath()

        # 调整坐标以适应70x70的画布，并创建向上的箭头
        # 将箭头居中并适当缩放
        scale = 2.0  # 缩放因子
        offset_x = 35  # x偏移，使箭头居中
        offset_y = 35  # y偏移，使箭头居中

        # 定义向上箭头的路径点
        path.moveTo(offset_x, offset_y - 15 * scale)  # 箭头顶点
        path.lineTo(offset_x - 8 * scale, offset_y - 5 * scale)  # 左侧点
        path.lineTo(offset_x - 4 * scale, offset_y - 5 * scale)  # 左侧内角
        path.lineTo(offset_x - 4 * scale, offset_y + 15 * scale)  # 左侧底部
        path.lineTo(offset_x + 4 * scale, offset_y + 15 * scale)  # 右侧底部
        path.lineTo(offset_x + 4 * scale, offset_y - 5 * scale)  # 右侧内角
        path.lineTo(offset_x + 8 * scale, offset_y - 5 * scale)  # 右侧点
        path.closeSubpath()  # 闭合路径

        # 设置画笔和画刷
        painter.setPen(QPen(Qt.NoPen))  # 无边框
        painter.setBrush(QBrush(Qt.white))  # 白色填充

        # 绘制路径
        painter.drawPath(path)
        painter.end()

        # 设置图标
        self.setIcon(QIcon(pixmap))

    def setEnabled(self, enabled):
        """重写setEnabled方法，在状态改变时更新图标颜色"""
        super().setEnabled(enabled)
        # 可以在这里根据enabled状态调整图标颜色，但由于背景色已通过CSS控制，这里暂不需要额外处理
