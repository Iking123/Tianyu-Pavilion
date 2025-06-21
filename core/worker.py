import re
import time
import json
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from core.config_manager import *
from core.search_utils import baidu_search, SearchAssistant


class Worker(QThread):
    """后台工作线程，用于处理搜索和API调用"""

    update_signal = pyqtSignal(str, str, bool)  # 角色, 内容, 是否是思考内容
    status_signal = pyqtSignal(str)
    search_complete = pyqtSignal(str)  # 结果
    start_thinking = pyqtSignal()  # 开始思考信号
    start_replying = pyqtSignal(str)  # 开始回复信号

    def __init__(self, user_input, conversation_history, pageIndex):
        super().__init__()
        self.user_input = user_input
        self.conversation_history = conversation_history
        self.pageIndex = pageIndex
        self.running = True

    def run(self):
        # 判断是否需要百度联网搜索
        need_search = False
        search_triggers = [
            "最新",
            "新闻",
            "最近",
            "搜索",
            "搜一下",
            "查一下",
            "实时",
            "当前",
            "2025",
            "今年",
            "股价",
            "价格",
            "行情",
            "比赛",
            "比分",
            "百度一下",
        ]
        question_types = [
            "是谁",
            "哪年",
            "什么时候",
            "在哪里",
            "为什么",
            "怎么样",
            "如何",
        ]

        if any(trigger in self.user_input for trigger in search_triggers):
            need_search = True
        elif any(q_type in self.user_input for q_type in question_types):
            need_search = True
        elif re.search(r"20[2-9][0-9]|今年|本月|上周", self.user_input):
            need_search = True

        # ========== 百度搜索处理 ==========
        search_context = ""
        if need_search:
            self.status_signal.emit("🔍 正在通过百度搜索并提取内容...")
            search_results = baidu_search(self.user_input)
            if search_results:
                search_context = search_results
                self.search_complete.emit(search_results)

        # ========== Tavily搜索处理 ==========
        if get_config("enable_tavily"):  # 只在启用 Tavily 时执行
            self.status_signal.emit("🔍 正在通过Tavily进行深度搜索...")
            assistant = SearchAssistant(search_context)
            findings = assistant.search(depth=3, user_input=self.user_input)
            if findings:
                self.search_complete.emit(findings)
                search_context += findings

        # ========== DeepSeek API请求 ==========
        role = "assistant"
        # 根据配置选择模型
        if get_config("enable_r1"):
            model_name = "deepseek-reasoner"
        else:
            model_name = "deepseek-chat"
            role += "-v3"
            # 若是V3则直接开始回复
            self.start_replying.emit(role)
            self.status_signal.emit("💬 正在生成回复...")

        if search_context:
            self.conversation_history.append(
                {"role": "system", "content": search_context}
            )

        # 更新系统提示时间
        self.conversation_history[0]["content"] = get_system_prompt(self.pageIndex)

        payload = {
            "model": model_name,
            "messages": self.conversation_history,
            "stream": True,
        }

        try:
            # 发送流式请求
            headers = {
                "Authorization": f"Bearer {get_config('api_key')}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                f"{get_config('base_url')}/chat/completions",
                json=payload,
                headers=headers,
                stream=True,
            )

            if response.status_code != 200:
                error_msg = f"请求失败 (状态码 {response.status_code}): {response.text}"
                self.update_signal.emit("system", error_msg, False)
                return

            full_response = ""
            in_thinking = False

            # 处理流式响应
            for line in response.iter_lines():
                if not self.running:
                    break

                if line and b"data: [DONE]" not in line:
                    if line.startswith(b"data: "):
                        json_data = line[6:]
                        try:
                            chunk = json.loads(json_data)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                reasoning = delta.get("reasoning_content", "")
                                content = delta.get("content", "")

                                if reasoning:
                                    # 处理思考内容
                                    if not in_thinking:
                                        # 发送开始思考信号
                                        self.start_thinking.emit()
                                        self.status_signal.emit("🤔 正在思考...")
                                        in_thinking = True
                                    # 发送思考内容
                                    self.update_signal.emit(role, reasoning, True)

                                elif content:
                                    # 处理回复内容
                                    if in_thinking:
                                        # 发送开始回复信号
                                        self.start_replying.emit(role)
                                        self.status_signal.emit("💬 正在生成回复...")
                                        in_thinking = False
                                    # 发送回复内容
                                    self.update_signal.emit(role, content, False)
                                    full_response += content
                        except json.JSONDecodeError:
                            continue

            self.conversation_history.append(
                {"role": "assistant", "content": full_response}
            )
            self.status_signal.emit("✅ 回复生成完成")

        except requests.exceptions.RequestException as e:
            self.update_signal.emit("system", f"\n网络请求错误: {str(e)}", False)

    def stop(self):
        self.running = False
