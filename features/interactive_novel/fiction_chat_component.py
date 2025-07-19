from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QButtonGroup,
    QSplitter,
)
from core.worker import Worker
from features.chat.chat_component import ChatComponent
from .fiction_parser import FictionParser
from ui.styles import BUTTON_STYLES
from core.character_manager import find_character_id


class FictionChatComponent(ChatComponent):
    """小说聊天组件"""

    def __init__(
        self,
        main_window=None,
        character_ids=[],
        placeholder="输入消息...",
        threshold=3000,
    ):
        super().__init__(
            main_window, ini_msg=False, placeholder=placeholder, threshold=threshold
        )

        self.character_ids = character_ids

        self.parser = FictionParser()  # 创建解析器实例
        self.current_options = []
        self.option_buttons = []
        self.option_button_group = QButtonGroup(self)
        self.option_button_group.buttonClicked.connect(self.on_option_selected)

        # 将选项区域直接插入到输入面板上方
        self.options_widget = QWidget()
        self.options_layout = QHBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(0, 0, 0, 0)  # 上下左右无间距
        self.options_layout.setSpacing(10)
        self.options_widget.setVisible(False)

        # 直接插入到输入面板上方（利用父类布局结构）
        splitter = self.findChild(QSplitter)  # 获取父类的分割器
        splitter.insertWidget(1, self.options_widget)  # 插入到输入面板前

        # # 开局选项
        # self.show_options(["开局", "开局。", "开局！"])

    def add_message_content(self, role, content, is_thinking=False):
        """添加消息内容方法"""
        if role and role.startswith("assistant") and not is_thinking:
            # 使用解析器处理内容
            messages = self.parser.parse(content)

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
                            self.message_display.add_message_by_role("", msg["content"])
                    case "dialogue":
                        # 角色对话 - 创建新消息控件
                        self.message_display.finish_last_message()
                        character = msg["character"]
                        id = find_character_id(self.character_ids, character)
                        dialogue = msg["content"]
                        self.message_display.add_message_by_role(
                            f"character_{id}",
                            dialogue,
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
        super().start_thinking(role)
        self.parser = FictionParser()

    def start_replying(self, role):
        """开始回复时重置解析器，但并不创建助手回复控件"""
        # 如果思考消息存在，完成它
        if self.thinking_widget:
            self.thinking_widget.force_render()
            self.thinking_widget.adjust_height()
            self.thinking_widget = None

        self.parser = FictionParser()

    def show_options(self, options):
        """显示选项按钮"""
        # 清除现有选项
        self.clear_options()
        self.current_options = options

        # 创建选项按钮
        for i, option in enumerate(options):
            btn = QPushButton(f"[{i+1}] {option}")
            btn.setStyleSheet(BUTTON_STYLES["option"])
            btn.setFixedHeight(50)
            self.options_layout.addWidget(btn)
            self.option_buttons.append(btn)
            self.option_button_group.addButton(btn, i)

        # 显示选项区域
        self.options_widget.setVisible(True)

    def clear_options(self):
        """清除当前选项"""
        for btn in self.option_buttons:
            self.options_layout.removeWidget(btn)
            btn.deleteLater()
        self.option_buttons = []
        self.current_options = []
        self.options_widget.setVisible(False)

    def on_option_selected(self, button):
        """处理选项选择"""
        index = self.option_button_group.id(button)
        if 0 <= index < len(self.current_options):
            # 发送选择的选项
            option_text = self.current_options[index]
            self.send_message(option_text)
            self.clear_options()

    def send_message(self, message, role="user", display=True):
        """发送消息前清除选项"""
        self.clear_options()
        super().send_message(message, role, display)

    def clear_conversation(self, force=False):
        """清除对话时同时清除选项"""
        self.clear_options()
        self.parser = FictionParser()  # 重置解析器
        super().clear_conversation(force)

    def on_worker_finished(self):
        """工作线程完成时调用，附加结局处理逻辑"""
        super().on_worker_finished()
        if not hasattr(self, "current_options") or len(self.current_options) == 0:
            self.input_panel.setVisible(False)
