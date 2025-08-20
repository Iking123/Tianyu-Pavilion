import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QIcon, QFontDatabase
from PyQt6.QtNetwork import QNetworkAccessManager
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from ui.main_window import MainWindow
from core.config_manager import get_config
from ui.styles import APP_STYLESHEET, ENHANCED_SCROLLBAR_STYLE
from core.character_summary import character_summary
from funcs import resource_path


class SomethingWorker(QObject):
    finished = pyqtSignal()  # 任务完成信号

    def run_task(self):
        """耗时操作"""
        from core.jieba_summarizer import summarizer

        self.finished.emit()  # 任务完成后发送信号


def main():
    thread = QThread()
    worker = SomethingWorker()  # 创建独立对象
    worker.moveToThread(thread)  # 多线程来搞事情
    thread.started.connect(worker.run_task)  # 线程启动时执行耗时任务
    thread.start()
    worker.finished.connect(thread.quit)  # 任务完成后让线程退出
    worker.finished.connect(worker.deleteLater)  # 清理 worker
    thread.finished.connect(thread.deleteLater)  # 线程结束后清理自身

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用高DPI缩放
    os.environ["QT_SCALE_FACTOR"] = "1"  # 强制缩放因子=1

    app = QApplication(sys.argv)

    # === Windows专属优化 ===
    if sys.platform == "win32":
        # 1. 设置AppUserModelID加速启动
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "TianYuGe.App"
            )
        except Exception as e:
            print(f"Windows优化设置失败: {e}")

        # 2. 禁用DPI虚拟化，避免界面模糊
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    # 设置应用样式
    app.setStyle("Fusion")

    # ⚠️ 重要：先设置调色板，再设置样式表
    # 创建调色板（但不要覆盖滚动条相关的颜色）
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Text, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 144, 226))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # 然后设置样式表（这样CSS优先级更高）
    combined_style = APP_STYLESHEET + ENHANCED_SCROLLBAR_STYLE
    app.setStyleSheet(combined_style)

    # 设置应用全局字体
    app_font = app.font()
    app_font.setPointSize(11)
    app.setFont(app_font)

    # 加载外部TTF字体
    QFontDatabase.addApplicationFont(
        resource_path("resources/font/1610424926410123.ttf")
    )
    QFontDatabase.addApplicationFont(resource_path("resources/font/黑白心中文字体.TTF"))

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

    # 尝试加载不同尺寸的图标
    for icon_file in icon_sizes:
        icon_path = resource_path(os.path.join("resources", "icons", icon_file))
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
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
