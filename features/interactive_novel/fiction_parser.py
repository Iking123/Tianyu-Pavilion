import re
from funcs import check_suffix_condition


class FictionParser:
    """智能解析交互小说格式的文本（支持流式处理）"""

    def __init__(self):
        self.buffer = ""
        self.state = "normal"  # normal, option_block
        self.current_options = []
        self.in_para = False

    def parse(self, new_content):
        """解析新内容，返回结构化消息列表"""
        self.buffer += new_content
        messages = []

        # 状态机处理缓冲区内容
        while self.buffer:
            if self.state == "normal":
                # 检查是否进入选项块
                if "<|OPTIONS|>" in self.buffer:
                    # 分割选项块之前的内容
                    before, self.buffer = self.buffer.split("<|OPTIONS|>", 1)

                    # 处理选项块之前的内容
                    if before:
                        messages.extend(self._parse_normal_content(before))

                    # 进入选项块状态
                    self.state = "option_block"
                    self.current_options = []
                    continue

                # 检查是否有段落结束
                if "\n" in self.buffer:
                    res, self.buffer = self.buffer.split("\n", 1)
                    messages.extend(self._parse_normal_content(res))
                    self.in_para = False
                    continue

                # 若当前内容的任意后缀均不为<|OPTIONS|>的前缀，说明当前所有内容均不在选项块；
                # 若self.in_para=False，说明当前内容为一段的开头；若为True，则不为一段开头；
                # 若是一段开头，且开头没有@，说明当前内容不是角色对话；
                # 若是一段开头，且开头有@，且已出现了|，说明角色名称已被输出，可以解析
                if check_suffix_condition(self.buffer, "<|OPTIONS|>") and (
                    self.in_para == True
                    or not self.buffer.startswith("@")
                    or "|" in self.buffer
                ):
                    messages.extend(self._parse_normal_content(self.buffer))
                    self.buffer = ""
                    continue

                # 等待更多内容
                break

            elif self.state == "option_block":
                # 检查是否结束选项块
                if "<|END_OPTIONS|>" in self.buffer:
                    option_block, self.buffer = self.buffer.split("<|END_OPTIONS|>", 1)

                    # 处理选项块内容
                    self._parse_option_block(option_block)
                    messages.append(
                        {"type": "options", "options": self.current_options}
                    )

                    # 返回正常状态
                    self.state = "normal"
                    self.current_options = []
                    continue
                else:
                    # 等待完整的结束标记
                    break

        return messages

    def _parse_normal_content(self, content):
        """解析普通内容（旁白和对话）"""
        messages = []

        # 按段落分割处理
        paragraphs = content.split("\n")
        num = len(paragraphs)
        for para in paragraphs:
            para = para
            if not para:
                continue

            # 如果当前有段落，则追加到当前段落中
            if self.in_para:
                messages.append({"type": "append", "content": para})
                if num > 1:
                    self.in_para = False
                continue

            # 检查是否是角色对话
            if para.startswith("@"):
                parts = para[1:].split("|", 1)
                if len(parts) == 2:
                    character = parts[0]
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

    def _parse_option_block(self, option_block):
        """解析选项块内容"""
        # 按行处理选项
        for line in option_block.splitlines():
            line = line.strip()
            if not line:
                continue

            # 检查选项格式
            if line.startswith("[") and "]" in line:
                # 提取选项文本
                option_text = line.split("]", 1)[1].strip()
                self.current_options.append(option_text)
