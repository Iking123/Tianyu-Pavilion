import os
import sys
from PyQt6.QtWidgets import QApplication, QScrollArea
from PyQt6.QtGui import QPalette, QColor, QIcon, QFontDatabase
from PyQt6.QtNetwork import QNetworkAccessManager
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QEvent, Qt
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


def ex_scroll(
    scroll_area: QScrollArea, key, ex_scroll_step=get_config("ex_scroll_step")
):
    scroll_bar = scroll_area.verticalScrollBar()
    if scroll_bar:
        # 计算新的滚动位置
        current_pos = scroll_bar.value()
        if key == Qt.Key.Key_Up:
            new_pos = max(0, current_pos - ex_scroll_step)
        else:  # Key_Down
            new_pos = min(
                scroll_bar.maximum(),
                current_pos + ex_scroll_step,
            )

        # 设置新的滚动位置
        scroll_bar.setValue(new_pos)


class ScrollSpeedFilter(QObject):
    def eventFilter(self, obj, event):
        # 检测键盘按下事件
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()

            # 检查是否是上键或下键
            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                # 获取当前具有焦点的部件
                focus_widget = QApplication.focusWidget()

                if focus_widget:
                    # 查找是否有滚动区域或可滚动部件
                    scroll_area = self.find_scroll_parent(focus_widget)
                    if scroll_area:
                        ex_scroll(scroll_area, key)

                # print(obj.__class__.__name__)
                if hasattr(obj, "parent") and obj.parent():
                    p = obj.parent()
                    n = p.__class__.__name__
                    if n == "MessageDisplayArea":
                        p.keyPressEvent(event)
                    if (
                        n == "DelayedWrapper"
                        and p.original_class_name == "MessageWidget"
                    ):
                        p.keyPressEvent(event)
        # 默认处理
        return super().eventFilter(obj, event)

    def find_scroll_parent(self, widget):
        """查找部件的父级中是否有QScrollArea"""
        current = widget
        while current:
            if isinstance(current, QScrollArea):
                return current
            # 检查部件是否有垂直滚动条
            if hasattr(current, "verticalScrollBar"):
                return current
            current = current.parentWidget()
        return None


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
    QFontDatabase.addApplicationFont(
        resource_path("resources/font/1642322874985804.ttf")
    )
    font_id = QFontDatabase.addApplicationFont(
        resource_path("resources/font/字小魂丹青行书.ttf")
    )

    if font_id == -1:
        print("无法加载字体文件")
        return None

    # 通过字体ID获取字体家族名称
    font_families = QFontDatabase.applicationFontFamilies(font_id)

    print(font_families)

    # 创建滚动速度过滤器
    scroll_filter = ScrollSpeedFilter()

    # 为整个应用程序安装事件过滤器
    app.installEventFilter(scroll_filter)

    # 设置全局滚轮速率
    app.setWheelScrollLines(get_config("speed_slider"))

    # 创建主窗口
    window = MainWindow()

    # 设置应用图标
    icon_sizes = [
        "icon.ico",
        #     "icon.png",  # 通用格式
        #     "icon.jpg",  # 备用格式
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
