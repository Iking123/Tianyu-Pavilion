import re
from funcs import check_suffix_condition, split_reserve_sep


class FictionParser:
    """智能解析交互小说格式的文本（支持流式处理）"""

    def __init__(self, page=None, main_window=None):
        self.page = page
        self.main_window = main_window
        self.buffer = ""
        self.current_options = []
        self.in_para = False

    def parse(self, new_content):
        """
        解析新内容，返回结构化消息列表\\
        简便起见（也为了防BUG），这里只处理旁白和语言描写\\
        对于选项块、结束符，则交给ChatComponent去解析
        """
        self.buffer += new_content
        messages = []

        # 处理缓冲区内容
        while self.buffer:

            # 检查选项块是否出现
            if "<OPTIONS>" in self.buffer:
                if self.main_window:
                    self.main_window.set_status("🔲正在构建选项...")
                # 分割选项块之前的内容
                before, self.buffer = split_reserve_sep(self.buffer, "<OPTIONS>")
                # 处理选项块之前的内容
                if before:
                    messages.extend(self._parse_normal_content(before))

            # 若以选项标签或结束符开头，则直接退出
            if (
                self.buffer.startswith("<OPTIONS>")
                or self.buffer.startswith("<FIN>")
                or self.buffer.startswith("<SUCCEED>")
                or self.buffer.startswith("<FAIL>")
            ):
                break

            # 检查结束符是否出现
            if "<FIN>" in self.buffer:
                before, self.buffer = split_reserve_sep(self.buffer, "<FIN>")
                if before:
                    messages.extend(self._parse_normal_content(before))
            if "<SUCCEED>" in self.buffer:
                before, self.buffer = split_reserve_sep(self.buffer, "<SUCCEED>")
                if before:
                    messages.extend(self._parse_normal_content(before))
            if "<FAIL>" in self.buffer:
                before, self.buffer = split_reserve_sep(self.buffer, "<FAIL>")
                if before:
                    messages.extend(self._parse_normal_content(before))

            # 检查是否有段落结束
            if "\n" in self.buffer:
                res, self.buffer = split_reserve_sep(self.buffer, "\n", True)
                messages.extend(self._parse_normal_content(res))
                self.in_para = False
                continue

            # 若当前内容的任意后缀均不为<OPTIONS>的前缀，说明当前所有内容均不在选项块；
            # 结束符同上理；
            # 若self.in_para=False，说明当前内容为一段的开头；若为True，则不为一段开头；
            # 若是一段开头，且开头没有@，说明当前内容不是角色对话；
            # 若是一段开头，且开头有@，且已出现了|，说明角色名称已被输出，可以解析
            if (
                check_suffix_condition(self.buffer, "<OPTIONS>")
                and self.no_ending()
                and (
                    self.in_para == True
                    or not self.buffer.startswith("@")
                    or "|" in self.buffer
                )
            ):
                messages.extend(self._parse_normal_content(self.buffer))
                self.buffer = ""
                continue

            # 等待更多内容
            break

        return messages

    def no_ending(self):
        """检查当前是否不可能已出现结束符"""
        return (
            check_suffix_condition(self.buffer, "<FIN>")
            and check_suffix_condition(self.buffer, "<SUCCEED>")
            and check_suffix_condition(self.buffer, "<FAIL>")
        )

    def _parse_normal_content(self, content: str):
        """解析普通内容（旁白和对话）"""
        if not content:
            return

        messages = []

        # 按段落分割处理
        paragraphs = re.split(r"(\n)", content)
        num = len(paragraphs)
        for p in paragraphs:
            para = p
            if not para:
                continue

            # 如果当前有段落，则追加到当前段落中
            if self.in_para:
                messages.append({"type": "append", "content": para})
                if para.endswith("\n"):
                    self.in_para = False
                continue

            # 检查是否是角色对话
            if para.startswith("@"):
                parts = para[1:].split("|", 1)
                if len(parts) == 2:
                    character = parts[0].strip()
                    dialogue = parts[1]
                    messages.append(
                        {
                            "type": "dialogue",
                            "character": character,
                            "content": dialogue,
                        }
                    )
                    if num == 1:
                        self.in_para = True
                    continue

            # 新开一段旁白
            messages.append({"type": "narration", "content": para})
            if num == 1:
                self.in_para = True

        return messages
