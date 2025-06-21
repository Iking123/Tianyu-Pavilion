from PyQt5.QtCore import QObject, pyqtSlot, QTimer
from PyQt5.QtWidgets import QScrollBar


def case_insensitive_find(s, sub, start=None, end=None):
    """不区分大小写的查找"""
    s_lower = s.lower()
    sub_lower = sub.lower()
    return s_lower.find(sub_lower, start, end)


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


def safe_scroll(scrollbar, position):
    """安全的滚动条设置"""
    if (
        scrollbar is not None
        and isinstance(scrollbar, QScrollBar)
        and not is_deleted(scrollbar)
    ):
        try:
            scrollbar.setValue(position)
        except RuntimeError:
            pass  # 二次保险，防止极端情况


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
