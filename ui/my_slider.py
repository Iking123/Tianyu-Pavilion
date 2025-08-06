import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QSlider,
    QLabel,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt


class MySlider(QWidget):
    def __init__(
        self,
        parent=None,
        l=0,
        r=100,
        single=1,
        page=5,
        itv=10,
        text="进度调节：",
        fs=11,
        after="",
        ini=None,
    ):
        super().__init__(parent)
        self.after = after

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建滑动条
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(l, r)  # 设置范围为
        self.slider.setSingleStep(single)  # 每次移动步长
        self.slider.setPageStep(page)  # 键盘翻页步长
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)  # 刻度在下方
        self.slider.setTickInterval(itv)
        self.slider.setStyleSheet(
            """
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                stop:0 #B1B1B1, stop:1 #c4c4c4);
                    margin: 2px 0;
                }
                
                QSlider::handle:horizontal {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                                fx:0.5, fy:0.5, stop:0.6 #45a, stop:0.7 #5af);
                    width: 18px;
                    height: 18px;
                    margin: -8px 0;
                    border-radius: 9px;
                }
                
                QSlider::sub-page:horizontal {
                    background: #5af;
                }
            """
        )

        if not ini:
            ini = (l + r) // 2
        self.value = ini
        # 创建显示标签
        self.value_label = QLabel(f"{ini}{after}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"font-size: {fs}pt; font-weight: bold;")

        # 创建带标题的水平布局
        title_layout = QHBoxLayout()
        title = QLabel(text)
        title.setStyleSheet(f"font-size: {fs}pt;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.value_label)

        # 添加到主布局
        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.slider)

        # 设置初始值
        self.slider.setValue(ini)

        # 连接信号
        self.slider.valueChanged.connect(self.update_label)

        self.setLayout(main_layout)

    def update_label(self, value):
        """更新标签显示"""
        self.value = value
        self.value_label.setText(f"{value}{self.after}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MySlider()
    ex.show()
    sys.exit(app.exec())
