from PyQt6.QtWidgets import QMessageBox
from core.config_manager import get_model
from core.network_check import check_internet_comprehensive_china
from features.chat.chat_component import ChatComponent
from funcs import resource_path
from ui.components import ImageWidget
from ui.message_display import MessageWidget
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
        forced_options: list[list[int | str]] = [],
        parent=None,
    ):
        super().__init__(
            main_window, ini_msg=False, placeholder=placeholder, threshold=threshold
        )

        self.character_ids = character_ids
        self.forced_options = forced_options
        self.current_options: list[str] = []
        self.page = parent
        self.over = False
        self.parser = FictionParser(self.page, main_window)  # 创建解析器实例
        self.shit_times = 0
        self.last_chara = ""
        self.round = 0

    def add_message_content(self, role, content, is_thinking=False):
        """添加消息内容方法"""
        if role and role.startswith("assistant") and not is_thinking:
            # 使用解析器处理内容
            messages = self.parser.parse(content)
            scrollbar = self.message_display.scroll_area.verticalScrollBar()
            at_bottom = bool(scrollbar) and scrollbar.value() == scrollbar.maximum()
            for msg in messages:
                t = msg["type"]
                c = msg["content"]
                match (t):
                    case "narration":
                        # 旁白消息 - 若上一条是旁白，则加入到上一条中，否则创建新消息控件
                        last = self.message_display.get_last_widget()
                        if last and isinstance(last, MessageWidget) and last.role == "":
                            self.message_display.append_to_last_message(c)
                        elif c and c != "\n":
                            self.message_display.finish_last_message()
                            self.message_display.add_message_by_role(
                                "", c, auto_scroll=at_bottom
                            )
                    case "dialogue":
                        # 语言描写 - 若上一条是同一角色的语言，则换行加入上一条中，否则创建新消息控件
                        character = msg["character"]
                        id = (
                            find_character_id(self.character_ids, character)
                            if character
                            else self.last_chara
                        )
                        last = self.message_display.get_last_widget()
                        if (
                            last
                            and isinstance(last, MessageWidget)
                            and last.raw_role == f"character_{id}"
                        ):
                            self.message_display.append_to_last_message(c)
                        else:
                            self.message_display.finish_last_message()
                            self.message_display.add_message_by_role(
                                f"character_{id}", c, auto_scroll=at_bottom
                            )
                        self.last_chara = id
                    case "append":
                        # 追加到上一条消息
                        self.message_display.append_to_last_message(c)
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
            self.thinking_widget.finish_thinking()
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
        # 焦点设置回消息区域
        self.message_display.scroll_area.setFocus()

    def send_message(self, message: str, role="user", display=True):
        """发送消息前清除选项"""
        self.clear_options()
        # if get_model().startswith("deepseek"):
        #     message += "（系统提示：你之前的回复过于短小，严重不符合正常小说长度，必须立即改正！你必须确保本轮小说长度>MAX{上一轮小说长度,1000}！）"
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
        self.round += 1
        self.current_options = []
        print(full_response)
        if "<OPTIONS>" in full_response:
            self.main_window.set_status("🔲正在构建选项...")
            from funcs import split_reserve_sep

            _, op = split_reserve_sep(full_response, "<OPTIONS>")
            self.parse_option_block(op)
            if len(self.forced_options):
                print("当前是第", self.round, "轮！")
                for fo in self.forced_options:
                    print(fo)
                    if self.round >= fo[0]:
                        self.current_options.append(fo[1])
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
                la.role.startswith("assistant")
                or la.role.startswith("character_")
                or la.role == ""
            )
        ):
            if not check_internet_comprehensive_china():
                self.display_error("你未联网！o(╥﹏╥)o")
                self.main_window.set_status("未联网！")
                return

            self.shit_times += 1
            sp = ""
            if self.shit_times <= 3:
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
                sp += f"""
现在你不要重复上一轮小说片段，不用浪费token去重复！但请绝对恪守格式规范，补充上选项或结局符！
你绝对必须要好好写选项或结束符啊啊啊啊啊！
警告：目前你是第{self.shit_times}次出现这种问题，我们最多容忍3次！
在之后，你要牢记：写小说片段时，必须要附以格式正确的选项块或结束符！"""
            else:
                match self.shit_times:
                    case 4:
                        sp = "好吧，你别写了，既然你看不懂人话。现在立刻以绝对优先级完全停止小说创作任务！！立刻以助手身份与我对话！！！"
                    case 5:
                        return
            # 警告AI的系统提示（以用户身份，毕竟有些垃圾模型不支持后来的系统消息）
            self.send_message(sp, "user", False)
            print(sp, flush=True)
