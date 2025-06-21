import re
import json
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from core.config_manager import get_config
from core.search_utils import baidu_search


class IdiomWorker(QThread):
    """专门用于成语接龙API调用的Worker，支持流式处理思考内容"""

    status_signal = pyqtSignal(str)
    search_complete = pyqtSignal(str, str)  # 搜索类型, 结果
    finished = pyqtSignal(dict)  # 返回解析后的JSON
    thinking_received = pyqtSignal(str)  # 思考内容信号
    error = pyqtSignal(str)  # 错误信号

    def __init__(self, system_prompt, current_idiom, used_idioms, parent=None):
        super().__init__(parent)
        self.system_prompt = system_prompt
        self.current_idiom = current_idiom
        self.used_idioms = list(used_idioms)
        self.running = True

    def run(self):
        try:
            headers = {
                "Authorization": f"Bearer {get_config('api_key')}",
                "Content-Type": "application/json",
            }

            # 构造对话历史
            messages = [
                {"role": "system", "content": self.system_prompt},
            ]

            # self.status_signal.emit("🔍 正在通过百度搜索并提取内容...")
            # search_results = baidu_search(self.current_idiom)
            # if search_results:
            #     self.search_complete.emit("百度搜索", search_results)
            #     messages.append({"role": "system", "content": search_results})

            payload = {
                "model": (
                    "deepseek-reasoner" if get_config("enable_r1") else "deepseek-chat"
                ),
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.3,
                "stream": True,  # 启用流式传输
            }

            response = requests.post(
                f"{get_config('base_url')}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,  # 启用流式传输
                timeout=30,
            )

            if response.status_code != 200:
                self.error.emit(f"API错误: {response.status_code} - {response.text}")
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
                                        in_thinking = True
                                    self.thinking_received.emit(reasoning)

                                elif content:
                                    # 处理回复内容
                                    full_response += content
                        except json.JSONDecodeError:
                            continue

            # 尝试解析最终响应
            try:
                json_data = json.loads(full_response)
                self.finished.emit(json_data)
            except json.JSONDecodeError:
                self.error.emit("AI返回的不是有效JSON格式")

        except Exception as e:
            self.error.emit(f"请求异常: {str(e)}")

    def stop(self):
        self.running = False
