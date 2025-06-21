from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QTextEdit,
    QFrame,
    QScrollArea,
)
from PyQt5.QtGui import QIcon, QFont, QColor, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
from ui.message_display import MessageDisplayArea
from ui.input_panel import InputPanel
from core.config_manager import get_assist


class IdiomSolitairePage(QWidget):
    """成语接龙游戏页面"""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.game_history = []
        self.current_idiom = ""
        self.game_active = True
        # 当前助手消息控件
        self.current_assistant_message = None

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F0F2F5; padding: 10px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 返回按钮
        self.back_button = QPushButton("← 返回游戏列表")
        self.back_button.setIcon(QIcon.fromTheme("go-previous"))
        self.back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 8pt;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #2E944B;
            }
        """
        )
        self.back_button.clicked.connect(self.go_back)

        # 页面标题
        title_label = QLabel("成语接龙")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;")

        # 重新开始按钮
        self.restart_button = QPushButton("重新开始")
        self.restart_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 8pt;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #3A7BC8;
            }
        """
        )
        self.restart_button.clicked.connect(self.restart_game)

        toolbar_layout.addWidget(self.back_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.restart_button)

        layout.addWidget(toolbar)

        # 游戏说明区域
        instructions = QLabel(
            """
        <b>游戏规则：</b>根据上一个成语的最后一个字，接一个新的四字成语。
        <br>如果有一方无法接龙、使用非四字成语或接龙错误，游戏结束。
        """
        )
        instructions.setStyleSheet(
            """
            background-color: #FFF3CD;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            margin: 10px;
        """
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # 主内容区域
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        # 左侧游戏区域
        game_frame = QFrame()
        game_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        game_layout = QVBoxLayout(game_frame)
        game_layout.setContentsMargins(15, 15, 15, 15)

        # 当前状态
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("<b>当前成语：</b>"))
        self.current_idiom_label = QLabel("游戏即将开始...")
        self.current_idiom_label.setFont(QFont("Arial", 14))
        status_layout.addWidget(self.current_idiom_label)
        status_layout.addStretch()

        self.status_label = QLabel("等待开始")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        game_layout.addLayout(status_layout)
        self.used_idioms = set()  # 用于记录已使用的成语

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #E0E0E0;")
        game_layout.addWidget(separator)

        # 聊天显示区域
        self.message_display = MessageDisplayArea()
        game_layout.addWidget(self.message_display, 1)

        # 输入区域
        self.input_panel = InputPanel(
            send_callback=self.handle_player_input, threshold=4
        )
        self.input_panel.setStyleSheet(
            "background-color: #F8F9FA; border-radius: 10px;"
        )
        game_layout.addWidget(self.input_panel)

        content_layout.addWidget(game_frame, 3)

        # 右侧信息区域
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: white; border-radius: 10px; padding: 15px;"
        )
        info_layout = QVBoxLayout(info_frame)

        info_label = QLabel("<b>游戏信息</b>")
        info_label.setFont(QFont("Microsoft Yahei", 14, QFont.Bold))
        info_layout.addWidget(info_label)

        # 历史记录
        history_label = QLabel("<b>历史记录：</b>")
        history_label.setStyleSheet("margin-top: 15px;")
        info_layout.addWidget(history_label)

        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setStyleSheet("border: none; background-color: #F8F9FA;")

        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setAlignment(Qt.AlignTop)

        self.history_scroll.setWidget(self.history_container)
        info_layout.addWidget(self.history_scroll, 1)

        # 提示区域
        tips_label = QLabel("<b>小贴士：</b>")
        tips_label.setStyleSheet("margin-top: 15px;")
        info_layout.addWidget(tips_label)

        tips_content = QLabel(
            "• 接龙时可以使用同音字（发音完全相同，包括音调）\n"
            "• 成语必须是四字词语\n"
            "• 避免重复使用相同成语\n"
            "• 如果你发现AI错了，请回复“你错啦！”\n（也可以更具体地说“音调错了”之类）"
        )
        tips_content.setStyleSheet("color: #7F8C8D;")
        info_layout.addWidget(tips_content)

        content_layout.addWidget(info_frame, 1)
        layout.addLayout(content_layout, 1)

        # 启动游戏
        self.start_game()

    def go_back(self):
        """返回游戏列表"""
        if self.main_window:
            self.main_window.switch_to_game_list()

    def start_game(self):
        """开始新游戏"""
        self.game_history = []
        self.used_idioms = set()  # 重置已使用成语记录
        self.game_active = True
        self.input_panel.set_send_enabled(True)
        self.status_label.setText("游戏进行中")
        self.status_label.setStyleSheet("color: #2ECC71; font-weight: bold;")

        # 添加欢迎消息
        self.message_display.clear_messages()
        self.message_display.add_message_by_role(
            "", "欢迎来到成语接龙游戏！请你说出第一个四字成语开始游戏。"
        )

        # 不再由AI先开始，等待用户输入

    def restart_game(self):
        """重新开始游戏"""
        self.start_game()
        self.update_history()
        self.current_idiom = ""
        self.current_idiom_label.setText("游戏即将开始...")

    def handle_player_input(self, text):
        """处理玩家输入"""
        if not self.game_active:
            return

        text = text.strip()

        # 1. 验证输入长度 (应该已经被输入框限制，双重检查)
        if len(text) != 4:
            self.message_display.add_message_by_role(
                get_assist(), "⚠️ 成语必须是四个字！请重新输入。"
            )
            return

        # 2. 检查是否重复
        if text in self.used_idioms:
            self.end_game(False, f"⚠️ 成语 '{text}' 已经使用过了！")
            return

        # 3. 添加到已使用列表
        self.used_idioms.add(text)
        self.game_history.append(("玩家", f'"{text}"'))
        self.update_history()

        # 显示玩家的消息
        self.message_display.add_message_by_role("user", f"我接：{text}")
        self.current_idiom = text
        self.current_idiom_label.setText(
            f"<b style='font-size: 14pt; font-family: Microsoft Yahei; color: #27AE60;'>{text}</b>"
        )

        # 禁用输入框，等待AI响应
        self.input_panel.set_send_enabled(False)

        # 启动AI回合
        self.ai_turn()

    def ai_turn(self):
        """AI的回合 - 调用API获取响应"""
        if not self.game_active:
            return

        # 构造系统提示
        system_prompt = f"""
        你正在与玩家进行成语接龙，规则如下：
        - 只能用四字成语，必须确保是成语
        - 成语的首字必须接上一个成语的末字（可用同音字，发音完全相同，包括音调）
        - 不能重复使用已用过的成语
        
        当前接龙记录：
        {self.format_history()}
        
        请严格按照以下JSON格式回应：
        {{
            "respondentIdiom": "你接龙的成语（四字，或空字符串）",
            "conclusions": "结束语（如果游戏应结束，否则空字符串）",
            "playerWin": bool,
        }}
        
        回应规则：
        ⒈若你发现上一次用户回复是指出AI错误，则你必须检查AI最后一次是否错了，如果确实错了，则玩家获胜，respondentIdiom留空，conclusions承认错误，playerWin填true；如果其实没错，则在conclusions中说明玩家乱说，playerWin填false
        ⒉若你能接龙，请填写respondentIdiom字段（四字成语），conclusions留空，playerWin填false
        ⒊若你认为玩家输了（你发现玩家回复并非成语、没有接上等等），respondentIdiom留空，conclusions解释玩家的错误所在，playerWin填false
        ⒋若你无法接龙，respondentIdiom留空，conclusions填写认输语，playerWin填true
        ⒌你必须尽快回复，别让玩家久等
        """

        # 调用API
        self.call_idiom_api(system_prompt)

    def call_idiom_api(self, system_prompt):
        """调用DeepSeek API获取成语接龙响应"""
        from PyQt5.QtCore import QThread
        from .idiom_worker import IdiomWorker

        # 创建并启动工作线程
        self.worker = IdiomWorker(system_prompt, self.current_idiom, self.used_idioms)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.thinking_received.connect(self.handle_thinking_content)
        self.worker.error.connect(self.handle_ai_error)
        self.worker.start()

        # 显示初始思考消息
        self.current_assistant_message = self.message_display.add_message_by_role(
            get_assist(), "🤔 正在思考接龙方案..."
        )
        self.message_display.scroll_to_bottom()

    def handle_thinking_content(self, new_content):
        """处理流式接收到的思考内容"""
        if self.current_assistant_message:
            if self.current_assistant_message.raw_content == "🤔 正在思考接龙方案...":
                self.message_display.remove_last_n_messages(1)
                self.current_assistant_message = (
                    self.message_display.start_assistant_message(
                        get_assist(), "🤔 ", True
                    )
                )
            self.current_assistant_message.append_content(new_content)

    def handle_ai_response(self, response):
        """处理AI的JSON响应"""
        try:
            # 解析JSON响应
            respondent_idiom = response.get("respondentIdiom", "").strip()
            conclusions = response.get("conclusions", "").strip()
            player_win = response.get("playerWin", False)

            # 完成当前助手消息
            self.finish_assistant_message()

            if conclusions:
                # 游戏结束
                if respondent_idiom:
                    # 错误情况：两者都有值
                    self.end_game(False, "AI响应格式错误")
                else:
                    # AI认输或指出玩家错误
                    self.end_game(player_win, conclusions)
            elif respondent_idiom:
                # AI正常接龙
                if len(respondent_idiom) != 4:
                    self.end_game(True, f"AI返回的成语'{respondent_idiom}'不是四字")
                    return

                if respondent_idiom in self.used_idioms:
                    self.end_game(True, f"AI重复使用了成语'{respondent_idiom}'")
                    return

                # 添加到历史记录
                self.used_idioms.add(respondent_idiom)
                self.game_history.append(("AI", f'"{respondent_idiom}"'))
                self.update_history()

                # 显示AI的消息
                self.message_display.add_message_by_role(
                    get_assist(),
                    f"我接：<b>{respondent_idiom}</b>\n\n"
                    f"该成语的最后一个字是'<b>{respondent_idiom[-1]}</b>'，"
                    f"请接一个以'<b>{respondent_idiom[-1]}</b>'开头的成语。",
                )

                # 更新当前成语
                self.current_idiom = respondent_idiom
                self.current_idiom_label.setText(
                    f"<b style='font-size: 14pt; font-family: Microsoft Yahei; color: #2980B9;'>{respondent_idiom}</b>"
                )

                # 滚动到底并启用用户输入
                self.message_display.scroll_to_bottom()
                self.input_panel.set_send_enabled(True)
            else:
                # 无效响应
                self.end_game(True, "AI返回了无效响应")

        except Exception as e:
            self.handle_ai_error(e)

    def finish_assistant_message(self):
        """完成当前助手消息"""
        # 如果思考消息存在，清除或完成它
        if self.current_assistant_message:
            if self.current_assistant_message.raw_content == "🤔 正在思考接龙方案...":
                self.message_display.remove_last_n_messages(1)
            else:
                self.current_assistant_message.force_render()
                self.current_assistant_message.adjust_height()
        self.current_assistant_message = None
        self.message_display.scroll_to_bottom()

    def handle_ai_error(self, error_msg):
        """处理API错误 - 恢复状态并允许用户重试"""
        # 移除最后1~2条消息：用户消息和AI的等待消息（若有）
        self.message_display.remove_last_n_messages()
        last_message = self.message_display.get_last_message()
        if last_message and last_message.role == "user":
            self.message_display.remove_last_n_messages()

        # 完成当前助手消息
        self.finish_assistant_message()

        # 从已使用成语中移除用户最新输入的成语
        if self.game_history and self.game_history[-1][0] == "玩家":
            last_player_idiom = self.game_history[-1][1]
            if last_player_idiom in self.used_idioms:
                self.used_idioms.remove(last_player_idiom)

            # 从游戏历史中移除玩家最新输入
            self.game_history.pop()

        # 更新历史显示
        self.update_history()

        # 恢复当前成语
        if self.game_history:
            # 取历史中最后一个成语（可能是AI的）
            last_idiom = self.game_history[-1][1]
            self.current_idiom = last_idiom
            self.current_idiom_label.setText(
                f"<b style='font-size: 14pt; font-family: Microsoft Yahei; color: #2980B9;'>{last_idiom}</b>"
            )
        else:
            # 如果没有历史记录，重置为初始状态
            self.current_idiom = ""
            self.current_idiom_label.setText("游戏即将开始...")

        # 显示错误消息并重新启用输入
        self.message_display.add_message_by_role(
            get_assist(),
            f"⚠️ 请求失败: {error_msg}\n" "已撤销您的最新操作，请重新尝试输入成语。",
        )
        self.input_panel.set_send_enabled(True)

        # 滚动到底部
        self.message_display.scroll_to_bottom()

    def end_game(self, player_wins, message=None):
        """结束游戏并显示结果"""
        self.game_active = False
        self.input_panel.set_send_enabled(False)

        if player_wins:
            self.status_label.setText("你赢了！")
            self.status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            end_message = (
                "🎉 <b>恭喜你赢了！</b> 🎉\n\n"
                f"{message or ''}\n"
                "点击'重新开始'按钮再来一局。"
            )
        else:
            self.current_idiom = ""
            self.current_idiom_label.setText("")
            self.status_label.setText("你输了")
            self.status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
            end_message = (
                "😅 <b>很遗憾，你输了！</b>\n\n"
                f"{message or '未知错误'}\n"
                "点击'重新开始'按钮再试一次！"
            )

        self.message_display.add_message_by_role(get_assist(), end_message)
        self.message_display.scroll_to_bottom()

    def format_history(self):
        """格式化历史记录用于系统提示"""
        return "\n".join(
            [
                f"{i+1}. {player}: {idiom}"
                for i, (player, idiom) in enumerate(self.game_history)
            ]
        )

    def update_history(self):
        """更新历史记录"""
        # 清除现有历史
        for i in reversed(range(self.history_layout.count())):
            widget = self.history_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 添加新历史
        for i, (player, idiom) in enumerate(self.game_history):
            label = QLabel(f"{i+1}. <b>{player}</b>: {idiom}")
            label.setStyleSheet("padding: 5px; border-bottom: 1px dotted #E0E0E0;")
            self.history_layout.addWidget(label)
