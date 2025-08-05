from PyQt5.QtWidgets import QMessageBox
from features.chat.chat_component import ChatComponent
from .fiction_parser import FictionParser
from core.character_manager import find_character_id


class FictionChatComponent(ChatComponent):
    """小说聊天组件"""

    def __init__(
        self,
        main_window=None,
        character_ids=[],
        placeholder="输入消息...",
        threshold=3000,
        parent=None,
    ):
        super().__init__(
            main_window, ini_msg=False, placeholder=placeholder, threshold=threshold
        )

        self.character_ids = character_ids

        self.parser = FictionParser(main_window)  # 创建解析器实例
        self.current_options = []
        self.option_buttons = []
        self.page = parent

    def add_message_content(self, role, content, is_thinking=False):
        """添加消息内容方法"""
        if role and role.startswith("assistant") and not is_thinking:
            # 使用解析器处理内容
            messages = self.parser.parse(content)
            scrollbar = self.message_display.scroll_area.verticalScrollBar()
            at_bottom = bool(scrollbar) and scrollbar.value() == scrollbar.maximum()
            for msg in messages:
                match (msg["type"]):
                    case "narration":
                        # 旁白消息 - 若上一条是旁白，则加入到上一条中（换行后加入），否则创建新消息控件
                        last = self.message_display.get_last_message()
                        if last and last.role == "":
                            self.message_display.append_to_last_message(
                                f"\n{msg["content"]}"
                            )
                        else:
                            self.message_display.finish_last_message()
                            self.message_display.add_message_by_role(
                                "", msg["content"], auto_scroll=at_bottom
                            )
                    case "dialogue":
                        # 角色对话 - 创建新消息控件
                        self.message_display.finish_last_message()
                        character = msg["character"]
                        id = find_character_id(self.character_ids, character)
                        dialogue = msg["content"]
                        self.message_display.add_message_by_role(
                            f"character_{id}", dialogue, auto_scroll=at_bottom
                        )
                    case "append":
                        # 追加到上一条消息
                        self.message_display.append_to_last_message(msg["content"])
                    case "options":
                        # 显示选项按钮
                        self.message_display.finish_last_message()
                        self.show_options(msg["options"])
        else:
            # 其他情况使用默认处理
            super().add_message_content(role, content, is_thinking)

        self.message_display.finish_last_message()

    def start_thinking(self, role):
        """开始思考时重置解析器"""
        self.thinking_widget = self.message_display.add_message_by_role(
            role, "", is_thinking=True
        )
        self.parser = FictionParser(self.main_window)

    def start_replying(self, role):
        """开始回复时重置解析器，但并不创建助手回复控件"""
        # 如果思考消息存在，完成它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        self.parser = FictionParser(self.main_window)

    def show_options(self, options):
        """显示选项消息"""
        # 清除现有选项
        self.clear_options()
        self.current_options = options
        scrollbar = self.message_display.scroll_area.verticalScrollBar()
        at_bottom = bool(scrollbar) and scrollbar.value() == scrollbar.maximum()
        # 创建选项消息
        for option in options:
            # 添加选项消息，role设为"option"
            option_widget = self.message_display.add_message_by_role(
                "option", option, auto_scroll=at_bottom
            )
            # 连接选项点击信号
            option_widget.option_clicked.connect(self.on_option_message_clicked)

    def clear_options(self):
        """清除    清除所有选项消息
        移除message_display中所有role为"option"的消息
        """
        if not hasattr(self, "message_display"):
            return

        # 获取所有消息
        all_messages = self.message_display.get_all_messages()
        # 找出所有选项消息
        option_messages = [msg for msg in all_messages if msg.role == "option"]

        # 移除选项消息
        for msg in option_messages:
            self.message_display.container_layout.removeWidget(msg)
            msg.deleteLater()

        self.current_options = []

    def on_option_message_clicked(self, option_text):
        """处理选项消息点击"""
        # 发送选择的选项
        self.send_message(option_text)
        # 清除所有选项消息
        self.clear_options()

    def send_message(self, message, role="user", display=True):
        """发送消息前清除选项"""
        self.clear_options()
        super().send_message(message, role, display)

    def on_worker_finished(self):
        """工作线程完成时调用，附加选项处理和结局处理逻辑"""
        if self.parser and self.parser.state == "option_block" and self.parser.buffer:
            self.parser._parse_option_block(self.parser.buffer)
            self.show_options(self.parser.current_options)

        self.input_panel.set_send_enabled(True)
        self.worker_active = False

        # 完成当前助手消息
        self.message_display.finish_assistant_message()

        # 如果思考控件还存在，强制渲染它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        if not hasattr(self, "current_options") or len(self.current_options) == 0:
            self.input_panel.setVisible(False)
            if self.page:
                self.page.over = True
            self.main_window.set_status("🔚 小说已结局")
        else:
            self.main_window.set_status("就绪")
