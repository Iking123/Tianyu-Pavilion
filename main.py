import os
import sys
from PyQt5.QtWidgets import QApplication, QScrollArea, QScrollBar
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import QTimer
from PyQt5.QtNetwork import QNetworkAccessManager
from ui.main_window import MainWindow
from core.config_manager import get_config
from ui.styles import APP_STYLESHEET, ENHANCED_SCROLLBAR_STYLE


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    # ⚠️ 重要：先设置调色板，再设置样式表
    # 创建调色板（但不要覆盖滚动条相关的颜色）
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(50, 50, 50))
    palette.setColor(QPalette.Text, QColor(50, 50, 50))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
    palette.setColor(QPalette.Highlight, QColor(74, 144, 226))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # 然后设置样式表（这样CSS优先级更高）
    combined_style = APP_STYLESHEET + ENHANCED_SCROLLBAR_STYLE
    app.setStyleSheet(combined_style)

    # 设置应用全局字体
    app_font = app.font()
    app_font.setPointSize(11)
    app.setFont(app_font)

    # 设置全局滚轮速率
    app.setWheelScrollLines(get_config("speed_slider"))

    # 创建主窗口
    window = MainWindow()

    # 设置应用图标（优先使用不同尺寸）
    icon_sizes = [
        "icon_256x256.ico",  # 主图标
        "icon_128x128.ico",  # 中等图标
        "icon_64x64.ico",  # 小图标
        "icon_32x32.ico",  # 任务栏图标
        "icon.png",  # 通用格式
        "icon.jpg",  # 备用格式
    ]

    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    icon_dir = os.path.join(base_path, "resources", "icons")

    # 尝试加载不同尺寸的图标
    for icon_file in icon_sizes:
        icon_path = os.path.join(icon_dir, icon_file)
        if os.path.exists(icon_path):
            window.setWindowIcon(QIcon(icon_path))
            break
    else:
        print("警告: 未找到应用图标文件")

    # 全局网络管理器监控错误
    global_network_manager = QNetworkAccessManager()
    global_network_manager.sslErrors.connect(
        lambda reply, errors: print(f"SSL错误: {[e.errorString() for e in errors]}")
    )
    global_network_manager.finished.connect(
        lambda reply: print(
            f"请求完成: {reply.url().toString()}, 状态: {reply.errorString()}"
        )
    )

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
