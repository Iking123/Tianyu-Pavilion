import inspect
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
import sys
import os
import json


def case_insensitive_find(s: str, sub: str, start=None, end=None):
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
    """判断 Qt 对象是否已被销毁"""
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
            if hasattr(self, "_delay_timer"):
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

    # 处理Windows路径中的反斜杠问题
    return os.path.join(base_path, relative_path).replace("\\", "/")


def check_suffix_condition(s: str, target: str) -> bool:
    """
    判断字符串s是否满足：任意后缀均不为target的任意前缀。
    若满足则返回True，否则返回False。
    """
    n = len(target)

    # 遍历字符串s的每个起始位置i（生成所有后缀）
    for i in range(len(s)):
        # 截取当前后缀的前min(n, len(s)-i)个字符
        suffix_head = s[i : i + n]
        # 检查target是否以该子串开头（即该子串是target的前缀）
        if target.startswith(suffix_head):
            return False
    return True


def print_method_source(method):
    """输出一个类方法（调试用）"""
    if inspect.ismethod(method):
        try:
            print(inspect.getsource(method.__func__))
        except TypeError:
            print("源代码不可访问（可能是内置方法）")
    else:
        print("输入的不是类方法")


def split_reserve_sep(s, separator):
    # 查找分隔符首次出现的位置
    index = s.find(separator)

    if index == -1:
        # 未找到分隔符时，整个字符串作为第一部分
        return (s, "")
    else:
        # 找到分隔符时分割字符串
        # 第一部分：从头到分隔符起始位置
        part1 = s[:index]
        # 第二部分：从分隔符起始位置到结束（包含分隔符）
        part2 = s[index:]
        return (part1, part2)


def read_json(fileName=""):
    if fileName != "":
        strList = fileName.split(".")
        if strList[len(strList) - 1].lower() == "json":
            with open(fileName, mode="r", encoding="utf-8") as file:
                return json.loads(file.read())


def create_circular_icon(icon_path):
    # 加载原始图标
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        return QIcon()

    # 创建透明画布
    result = QPixmap(pixmap.size())
    result.fill(Qt.GlobalColor.transparent)

    # 设置圆形蒙版
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 创建圆形路径 (顶着上边界+水平居中)
    diameter = min(pixmap.width(), pixmap.height())
    x = (pixmap.width() - diameter) / 2
    path = QPainterPath()
    path.addEllipse(x, 0, diameter, diameter)  # y=0 确保顶着上边界

    # 应用圆形蒙版
    painter.setClipPath(path)

    # 绘制原始图像
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return QIcon(result)


def update_or_add_style_property(style_parts, prefix, new_line):
    """一个辅助函数，用于更新或添加样式属性"""
    for i, part in enumerate(style_parts):
        if part.strip().startswith(prefix):
            style_parts[i] = new_line
            return  # 找到并更新后直接返回
    style_parts.insert(0, new_line)  # 如果没找到，就添加到列表开头
