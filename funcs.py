import inspect
import re
from typing import List
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QSize, QRect
from PyQt6.QtWidgets import QApplication
import sys
import os
import json


def replace_newline_with_space(s: str):
    """用空格替换掉换行符"""
    return re.sub(r"(?:\r\n|\n|\r)+", " ", s)


def sanitize_windows_filename(filename):
    """
    按照Windows系统标准，将字符串中的文件名禁止字符替换为空格

    Args:
        filename: 待处理的字符串

    Returns:
        处理后的字符串，其中所有Windows禁止的文件名字符都被替换为空格
    """
    # Windows系统禁止的文件名字符
    forbidden_chars = {"\\", "/", ":", "*", "?", '"', "<", ">", "|"}

    # 处理可见的禁止字符
    sanitized = [c if c not in forbidden_chars else " " for c in filename]

    # 处理ASCII 0-31的控制字符
    sanitized = [c if ord(c) >= 32 else " " for c in sanitized]

    return "".join(sanitized)


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
            # 保存原始类引用
            self._original_class = widget_class

        @pyqtSlot()
        def request_delayed_update(self):
            if hasattr(self, "_delay_timer"):
                self._delay_timer.start(50)  # 合并50ms内的更新请求

        @pyqtSlot()
        def _commit_delayed_update(self):
            if self.isVisible():
                self.updateGeometry()
                self.update()

        @property
        def original_class_name(self):
            """获取原始类名"""
            return self._original_class.__name__

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


def get_screen_height():
    """获取主屏幕的高度"""
    # screens()返回所有屏幕的列表，[0]表示主屏幕（多屏幕可调整索引）
    screen = QApplication.screens()[0]
    # 获取屏幕的可用区域（排除任务栏/菜单栏等系统区域）
    screen_geo = screen.availableGeometry()
    screen_height = screen_geo.height()
    return screen_height


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


def split_reserve_sep(s, separator, left=False):
    """包含分隔符的单次分割，默认将分隔符放右边"""
    # 查找分隔符首次出现的位置
    index = s.find(separator)

    if index == -1:
        # 未找到分隔符时，整个字符串作为第一部分
        return (s, "")
    else:
        # 找到分隔符时分割字符串
        if left:
            index += len(separator)
        # 第一部分：从头到分隔符起始位置
        part1 = s[:index]
        # 第二部分：从分隔符起始位置到结束（默认包含分隔符）
        part2 = s[index:]
        return (part1, part2)


def read_json(fileName=""):
    if fileName != "":
        strList = fileName.split(".")
        if strList[len(strList) - 1].lower() == "json":
            with open(fileName, mode="r", encoding="utf-8") as file:
                return json.loads(file.read())


def create_circular_pixmap(image_path: str) -> QPixmap:
    """
    将源QPixmap裁剪成一个顶边居中的内切圆形，并缩放到64x64。

    Args:
        source_pixmap: 原始的QPixmap图像。

    Returns:
        一个64x64大小的、包含圆形图像的QPixmap。
    """
    if not image_path:
        return QPixmap()
    source_pixmap = QPixmap(image_path)
    if source_pixmap.isNull():
        print(f"错误：无法从 '{image_path}' 加载图片。")
        # 返回一个空的 QIcon 作为备用
        return QIcon()

    # 1. 计算内切圆的直径和位置
    # 直径是原始图像宽和高中的较小值
    source_size = source_pixmap.size()
    diameter = min(source_size.width(), source_size.height())

    # 圆形区域在原图中的坐标
    # Y坐标顶着上边界，所以是0
    # X坐标水平居中
    crop_x = (source_size.width() - diameter) / 2
    crop_y = 0  # 顶着上边界

    # 2. 创建一个新的方形QPixmap作为我们的画布，它的大小就是圆的直径
    # 我们将在这个画布上绘制圆形图像
    target_pixmap = QPixmap(diameter, diameter)
    target_pixmap.fill(Qt.GlobalColor.transparent)  # 使用透明背景

    # 3. 使用QPainter进行绘制
    painter = QPainter(target_pixmap)
    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing
    )  # 开启抗锯齿，使圆形边缘平滑
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # 4. 创建一个圆形的剪裁路径
    path = QPainterPath()
    path.addEllipse(0, 0, diameter, diameter)
    painter.setClipPath(path)

    # 5. 将原图的指定部分绘制到新的画布上
    # drawPixmap的参数:
    # target_x, target_y: 在目标画布上绘制的起始点 (0, 0)
    # source_pixmap: 源图像
    # source_x, source_y: 从源图像的哪个位置开始裁剪 (我们计算好的crop_x, crop_y)
    # source_w, source_h: 从源图像裁剪的尺寸 (diameter, diameter)
    painter.drawPixmap(
        0, 0, source_pixmap, int(crop_x), int(crop_y), diameter, diameter
    )

    painter.end()

    # 6. 将最终得到的圆形图像缩放到64x64
    final_pixmap = target_pixmap.scaled(
        64,
        64,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    return final_pixmap


def update_or_add_style_property(style_parts, prefix, new_line):
    """一个辅助函数，用于更新或添加样式属性"""
    for i, part in enumerate(style_parts):
        if part.strip().startswith(prefix):
            style_parts[i] = new_line
            return  # 找到并更新后直接返回
    style_parts.insert(0, new_line)  # 如果没找到，就添加到列表开头
