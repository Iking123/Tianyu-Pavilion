import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QPushButton

app = QApplication(sys.argv)
window = QMainWindow()

status_bar = QStatusBar()
button1 = QPushButton("测试按钮1")
button1.setStyleSheet("background-color: red;")
button1.setFixedSize(100, 30)
status_bar.addWidget(button1)

button2 = QPushButton("测试按钮2")
button2.setStyleSheet("background-color: blue;")
button2.setFixedSize(100, 30)
status_bar.addWidget(button2)

window.setStatusBar(status_bar)
window.show()
sys.exit(app.exec_())
