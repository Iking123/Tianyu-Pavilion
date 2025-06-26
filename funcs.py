from PyQt5.QtCore import QObject, pyqtSlot, QTimer, QDateTime
from PyQt5.QtWidgets import QScrollBar, QScrollArea
import sys
import os


def case_insensitive_find(s, sub, start=None, end=None):
    """不区分大小写的查找"""
    s_lower = s.lower()
    sub_lower = sub.lower()
    return s_lower.find(sub_lower, start, end)


def execute_repeatedly(func):
    """在100毫秒内毎10毫秒执行指定函数

    参数:
        func (function): 需要重复执行的函数
    """
    counter = 0
    max_executions = 10  # 100ms / 10ms = 10次

    def wrapper():
        nonlocal counter
        if counter < max_executions:
            func()  # 执行目标函数
            counter += 1
        else:
            timer.stop()  # 达到10次后停止

    # 创建并设置定时器
    timer = QTimer()
    timer.setInterval(10)  # 10毫秒间隔
    timer.timeout.connect(wrapper)
    timer.start()


def is_deleted(obj):
    """判断 Qt 对象是否已被销毁（PyQt5专用版）"""
    try:
        # 尝试访问一个简单属性（如objectName）来触发有效性检查
        _ = obj.objectName()  # 如果对象已被删除，这里会抛出 RuntimeError
        return False
    except RuntimeError:
        return True
    except AttributeError:
        # 处理传入非QObject对象的情况（如None）
        return True


def delay_update(widget_class):
    """为任意QWidget添加延迟更新能力的装饰器"""

    class DelayedWrapper(widget_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._delay_timer = QTimer()
            self._delay_timer.setSingleShot(True)
            self._delay_timer.timeout.connect(self._commit_delayed_update)

        @pyqtSlot()
        def request_delayed_update(self):
            self._delay_timer.start(50)  # 合并50ms内的更新请求

        @pyqtSlot()
        def _commit_delayed_update(self):
            if self.isVisible():
                self.updateGeometry()
                self.update()

    return DelayedWrapper


def resource_path(relative_path):
    """获取资源的绝对路径，支持开发环境和PyInstaller打包环境"""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller打包后的临时目录
        base_path = sys._MEIPASS
    else:
        # 正常开发环境
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
