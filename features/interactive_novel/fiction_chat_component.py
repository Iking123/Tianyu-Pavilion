from PyQt6.QtWidgets import QMessageBox
from features.chat.chat_component import ChatComponent
from funcs import resource_path
from ui.components import ImageWidget
from .fiction_parser import FictionParser
from core.character_manager import find_character_id
import time


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
        self.current_options = []
        self.option_buttons = []
        self.page = parent
        self.over = False
        self.parser = FictionParser(self.page, main_window)  # 创建解析器实例

    def add_message_content(self, role, content, is_thinking=False):
        """添加消息内容方法"""
        if role and role.startswith("assistant") and not is_thinking:
            # 使用解析器处理内容
            messages = self.parser.parse(content)
            scrollbar = self.message_display.scroll_area.verticalScrollBar()
            at_bottom = bool(scrollbar) and scrollbar.value() == scrollbar.maximum()
            for msg in messages:
                t = msg["type"]
                match (t):
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
        else:
            # 其他情况使用默认处理
            super().add_message_content(role, content, is_thinking)

        self.message_display.finish_last_message()

    def start_thinking(self, role):
        """开始思考时重置解析器"""
        self.thinking_widget = self.message_display.add_message_by_role(
            role, "", is_thinking=True
        )
        self.parser = FictionParser(self.page, self.main_window)

    def start_replying(self, role):
        """开始回复时重置解析器，但并不创建助手回复控件"""
        # 如果思考消息存在，完成它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        self.parser = FictionParser(self.page, self.main_window)

    def show_options(self):
        """显示选项消息"""
        # 清除现有选项
        self.clear_options()
        scrollbar = self.message_display.scroll_area.verticalScrollBar()
        at_bottom = bool(scrollbar) and scrollbar.value() == scrollbar.maximum()
        # 创建选项消息
        for option in self.current_options:
            # 添加选项消息，role设为"option"
            option_widget = self.message_display.add_message_by_role(
                "option", option, auto_scroll=at_bottom
            )
            # 连接选项点击信号
            option_widget.option_clicked.connect(self.on_option_message_clicked)

    def clear_options(self):
        """
        清除所有选项消息\\
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

    def on_option_message_clicked(self, option_text):
        """处理选项消息点击"""
        # 发送选择的选项
        self.send_message(option_text)
        # 清除所有选项消息
        self.clear_options()

    def send_message(self, message: str, role="user", display=True):
        """发送消息前清除选项"""
        self.clear_options()
        super().send_message(message, role, display)

    def parse_option_block(self, option_block):
        """解析选项块内容"""
        # 按行处理选项
        for line in option_block.splitlines():
            line = line.strip()
            if not line:
                continue

            # 检查选项格式
            if "." in line:
                # 提取选项文本
                option_text = line.split(".", 1)[1].strip()
                self.current_options.append(option_text)

    def on_worker_finished(self, full_response: str):
        """工作线程结束时，处理选项、结局等逻辑"""
        self.current_options = []

        if "<OPTIONS>" in full_response:
            self.main_window.set_status("🔲正在构建选项...")
            from funcs import split_reserve_sep

            _, op = split_reserve_sep(full_response, "<OPTIONS>")
            self.parse_option_block(op)
            self.show_options()

        self.previous_response_id = (
            self.worker.previous_response_id if self.worker else "start"
        )
        self.input_panel.set_send_enabled(True)
        self.worker_active = False

        # 完成当前助手消息
        self.message_display.finish_assistant_message()

        # 如果思考控件还存在，强制渲染它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        if hasattr(self, "current_options") and len(self.current_options) > 0:
            self.main_window.set_status("就绪")
        elif "<FIN>" in full_response:
            # 结束
            self.main_window.set_status("🔚 小说已结局")
            self.input_panel.setVisible(False)
            e = ImageWidget(resource_path("resources/images/fin.png"))
            self.message_display.add_widget(e)
            self.over = True
            if self.page:
                self.page.over = True
        elif "<SUCCEED>" in full_response:
            self.main_window.set_status("🏆 已获胜！")
            self.input_panel.setVisible(False)
            e = ImageWidget(resource_path("resources/images/succeed.png"))
            self.message_display.add_widget(e)
            self.over = True
            if self.page:
                self.page.over = True
                self.page.setBackgroundColor("#FFEE9D")
                self.page.toolbar.setStyleSheet(
                    "background-color: #FFE875; padding: 10px;"
                )
            self.message_display.setStyleSheet("background-color: #FFEE9D")
            self.message_display.set_all_message_background("lemonchiffon")
        elif "<FAIL>" in full_response:
            self.main_window.set_status("😭 你输了...")
            self.input_panel.setVisible(False)
            e = ImageWidget(resource_path("resources/images/fail.png"))
            self.message_display.add_widget(e)
            self.over = True
            if self.page:
                self.page.over = True
                self.page.setBackgroundColor("#E4E4E4")
                self.page.toolbar.setStyleSheet(
                    "background-color: dimgray; padding: 10px;"
                )
            self.message_display.setStyleSheet("background-color: #E4E4E4")
            self.message_display.set_all_message_background("gainsboro")
        elif (
            (la := self.message_display.get_last_message())
            and hasattr(la, "role")
            and isinstance(la.role, str)
            and (
                la.role.startswith("assistant_")
                or la.role.startswith("character_")
                or la.role == ""
            )
        ):
            self.message_display.get_last_message()
            sp = """系统提示：你上一次输出时，既未以正确格式输出选项，也未输出结局符！
正确的选项格式：
<OPTIONS>
1. 选项一
2. 选项二
3. 选项三

正确的结局符：
- 结束标签：<FIN>
"""
            if self.page and self.page.clearance_condition:
                sp += """- 通关标签：<SUCCEED>
- 失败标签：<FAIL>
"""
            sp += """
你无需重写上一轮小说片段，但请绝对恪守格式规范，补充上选项或结局符！"""
            self.send_message(sp, "system", False)
            print("好好写！", flush=True)
