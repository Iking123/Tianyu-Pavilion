# chat_component.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QSizePolicy,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer, QObject
from PyQt5.QtGui import QFont
from core.worker import Worker
from core.config_manager import *
from ui.styles import *
from ui.search_toolbar import SearchToolbar
from ui.message_display import MessageDisplayArea
from ui.input_panel import InputPanel  # 导入新的输入面板组件


class ChatComponent(QWidget):
    """聊天功能组件，修复流式回复问题"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.conversation_history = [{"role": "system", "content": get_system_prompt()}]
        self.worker = None
        self.timer = None
        self.worker_active = False
        self.thinking_widget = None
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 使用搜索工具栏组件
        self.search_toolbar = SearchToolbar()
        self.search_toolbar.connect_signals(
            self.initiate_search, self.search_prev, self.search_next, self.close_search
        )
        main_layout.addWidget(self.search_toolbar)

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)

        # 使用新的消息显示区域组件
        self.message_display = MessageDisplayArea()
        splitter.addWidget(self.message_display)

        # 添加初始系统消息
        self.initial_msg = self.message_display.add_message_by_role(
            "system", self.conversation_history[0]["content"]
        )

        # 创建定时器更新初始系统消息的时间
        self.timer = QTimer()
        self.timer.setParent(self)
        self.timer.timeout.connect(self.safe_update_time)
        self.timer.start(1000)
        self.safe_update_time()

        # 使用新的输入面板组件
        self.input_panel = InputPanel(
            send_callback=self.send_message,
            clear_callback=self.clear_conversation,
            show_clear_button=True,
        )
        splitter.addWidget(self.input_panel)

        # 设置分割器大小
        splitter.setSizes([1200, 400])
        main_layout.addWidget(splitter)

        # 连接滚动到底部按钮
        scroll_button = self.main_window.get_scroll_button()
        scroll_button.clicked.connect(self.message_display.scroll_to_bottom)

        # 搜索定时器
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        # 渲染测试
        self.start_replying("assistant")
        self.add_message_content("assistant", "**渲染测试**\n")
        self.add_message_content("assistant", "# 标题\n")
        self.add_message_content("assistant", "- 列表1\n")
        self.add_message_content("assistant", "- 列表2\n")
        self.add_message_content("assistant", "* 列表3\n")
        self.start_replying("assistant-v3")
        self.add_message_content(
            "assistant-v3",
            """
确实存在不少常被误认为成语、实则并非成语的词语或短语。这些表达因结构类似成语（四字居多）、流传广泛或语义凝练，常被混淆。以下整理几类典型例子：

------

### 一、被误用的「真成语」

（本身是成语，但现代用法偏离本义）

1. 空穴来风

    - 本义：有空穴才有风 → 消息有根据（《文选·宋玉》）
    - 误用：常被当作“毫无根据的谣言”。 

2. 三人成虎
    - 本义：多人重复谎言，假的也变真 → 强调谣言的危害（《战国策》）
    - 误用：常误解为“团结力量大”。 

------

### 二、实为「非成语」的常见误认词

（结构像成语，但未被词典收录）

1. 十动然拒

    - 来源：网络梗（“十分感动，然后拒绝”的缩略），非历史传承的成语。 

2. 人艰不拆
   - 来源：流行语（“人生已如此艰难，有些事就不要拆穿”），属当代生造词。 
3. 细思恐极
   - 来源：网络缩略语（“仔细想想，恐怖至极”），无古籍或文学出处。 
4. 累觉不爱
   - 来源：网络语（“很累，感觉自己不会再爱了”），缺乏成语的典故性。 

------

### 三、易混淆的「典故词」

（出自故事但未固化成语）

1. 守株待兔（实为成语）

    - 对比案例：类似“刻舟求剑”是成语，但“削足适履”“掩耳盗铃”等是成语，需注意区分。
    - 伪例：如“叶公好龙”是成语，但“邯郸学步”“东施效颦”等也是成语，不存在混淆。 

2. 火中取栗
   - 实为成语（出自拉·封丹寓言），但常被误认为“非成语”因是外来典故。 

------

### 四、被篡改的「变体词」

（错误传播后像独立成语）

- 昨日黄花 ❌
  正解：明日黄花（苏轼诗“明日黄花蝶也愁”，指过时之物）。
- 七月流火 ❌（常误指天气炎热）
  正解：出自《诗经》，指农历七月火星西沉，天气转凉。 

------

### 为何会误认？

1. 四字结构误导：汉语习惯将四字短语默认为成语（如“开心麻花”）。 
2. 高频使用固化：网络流行语因重复使用产生“伪成语”错觉。 
3. 语义凝练性：如“人艰不拆”高度概括情绪，接近成语功能。 

建议查阅《汉语成语大词典》或权威语料库（如北大CCL）验证。若需具体案例的详细辨析，可告知方向进一步探讨！ 📚 
""",
        )
        self.message_display.finish_assistant_message()

    def safe_update_time(self):
        """安全更新时间显示"""
        try:
            # 直接更新初始消息的内容
            self.initial_msg.set_content(get_system_prompt(), "system")
        except Exception as e:
            print(f"更新时间时出错: {e}")
            self.stop_and_clean_timer()

    def stop_and_clean_timer(self):
        """安全停止并清理定时器"""
        try:
            if self.timer and self.timer.isActive():
                self.timer.stop()
            self.timer = None
        except:
            pass

    def send_message(self, user_input):
        if not user_input:
            return

        # 重要：先停止并清理旧的Worker
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)  # 等待最多3秒
            if self.worker.isRunning():
                self.worker.terminate()  # 强制终止
            self.worker.deleteLater()
            self.worker = None

        # 禁用发送按钮
        self.input_panel.set_send_enabled(False)

        # 设置工作状态
        self.worker_active = True

        # 添加用户消息
        self.message_display.add_message_by_role("user", user_input)
        self.conversation_history.append({"role": "user", "content": user_input})

        # 创建新Worker
        self.worker = Worker(user_input, self.conversation_history, 1)

        # 使用队列连接确保线程安全
        self.worker.start_thinking.connect(self.start_thinking, Qt.QueuedConnection)
        self.worker.start_replying.connect(self.start_replying, Qt.QueuedConnection)
        self.worker.update_signal.connect(self.add_message_content, Qt.QueuedConnection)
        self.worker.status_signal.connect(
            self.main_window.set_status, Qt.QueuedConnection
        )
        self.worker.search_complete.connect(
            self.message_display.add_search_result, Qt.QueuedConnection
        )
        self.worker.finished.connect(self.on_worker_finished, Qt.QueuedConnection)

        self.worker.start()

    def start_thinking(self):
        """开始新的思考消息"""
        self.thinking_widget = self.message_display.add_message_by_role(
            "assistant", "", is_thinking=True
        )
        self.message_display.scroll_to_bottom()

    def start_replying(self, role):
        """开始新的回复消息"""
        # 如果思考消息存在，完成它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        # 开始新的回复消息
        self.message_display.start_assistant_message(role, "")
        self.message_display.scroll_to_bottom()

    def add_message_content(self, role, content, is_thinking=False):
        """添加消息内容到聊天界面"""
        try:
            if role and role.startswith("assistant"):
                if is_thinking:
                    if self.thinking_widget:
                        self.thinking_widget.append_content(content)
                else:
                    self.message_display.append_to_assistant_message(content)
            else:
                self.message_display.add_message_by_role(role, content)
                self.message_display.scroll_to_bottom()
        except Exception as e:
            print(f"添加消息内容时出错: {e}")
            # 不要让异常导致程序崩溃

    def on_worker_finished(self):
        """工作线程完成时调用"""
        self.input_panel.set_send_enabled(True)
        self.worker_active = False

        # 完成当前助手消息
        self.message_display.finish_assistant_message()

        # 如果思考控件还存在，强制渲染它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        # 滚动到底部
        self.message_display.scroll_to_bottom()

    def clear_conversation(self):
        """清除对话历史（带确认弹窗）"""
        # 创建确认对话框
        reply = QMessageBox.question(
            self,
            "确认清除",
            "即将清除对话历史并开启新对话，确定执行吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        # 如果用户选择否，则取消操作
        if reply == QMessageBox.No:
            # 使用主窗口设置状态
            if self.main_window:
                self.main_window.set_status("清除操作已取消")
            return

        # 停止当前工作线程
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        # 清除聊天界面
        self.message_display.clear_messages()

        # 重置对话历史
        self.conversation_history = [{"role": "system", "content": get_system_prompt()}]

        # 添加初始系统消息
        self.initial_msg = self.message_display.add_message_by_role(
            "system", self.conversation_history[0]["content"]
        )

        # 使用主窗口设置状态
        if self.main_window:
            self.main_window.set_status("对话已清除")

    # 以下是搜索功能方法：

    def keyPressEvent(self, event):
        """处理键盘快捷键"""
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
            self.toggle_search_toolbar()
            return
        elif event.key() == Qt.Key_Escape and self.search_toolbar.isVisible():
            self.close_search()
            return
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.search_toolbar.search_input.hasFocus():
                self.search_next()
                return

        super().keyPressEvent(event)

    def toggle_search_toolbar(self):
        """切换搜索工具栏显示状态"""
        visible = not self.search_toolbar.isVisible()
        self.search_toolbar.setVisible(visible)

        if visible:
            self.search_toolbar.focus_search_input()
        else:
            self.message_display.clear_all_highlights()

    def close_search(self):
        """关闭搜索工具栏"""
        self.search_toolbar.setVisible(False)
        self.message_display.clear_all_highlights()

    def initiate_search(self, text):
        """初始化搜索（带延迟）"""
        self.search_timer.start(300)  # 300ms延迟

    def perform_search(self):
        """执行实际搜索"""
        search_term = self.search_toolbar.get_search_term()
        if not search_term:
            self.message_display.clear_all_highlights()
            self.search_toolbar.set_match_count(0, 0)
            return

        # 执行搜索
        total = self.message_display.perform_search(search_term)

        # 更新匹配计数
        self.search_toolbar.set_match_count(0, total)

        # 如果有匹配项，跳转到第一个
        if total > 0:
            self.message_display.current_match_index = 0
            self.message_display.highlight_current_match()
            self.search_toolbar.set_match_count(1, total)

    def search_next(self):
        """跳转到下一个匹配项"""
        if not self.message_display.search_matches:
            return

        current_index = self.message_display.search_next()
        total = len(self.message_display.search_matches)
        self.search_toolbar.set_match_count(current_index, total)

    def search_prev(self):
        """跳转到上一个匹配项"""
        if not self.message_display.search_matches:
            return

        current_index = self.message_display.search_prev()
        total = len(self.message_display.search_matches)
        self.search_toolbar.set_match_count(current_index, total)

    def cleanup(self):
        """清理资源，当组件被移除时调用"""
        # 停止定时器
        self.stop_and_clean_timer()

        # 停止工作线程
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)
            if self.worker.isRunning():
                self.worker.terminate()
            self.worker.deleteLater()
            self.worker = None

        # 清理消息显示区域
        if hasattr(self, "message_display"):
            self.message_display.clear_messages()

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        self.cleanup()
        super().closeEvent(event)
