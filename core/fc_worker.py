import re
import time
import json
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from core.config_manager import *
from core.search_utils import baidu_search, tavily_search


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
        self.max_function_calls = 3  # 最大函数调用次数
        self.function_call_count = 0  # 当前函数调用次数

    def run(self):
        # 根据配置选择模型
        if get_config("enable_r1"):
            model_name = "deepseek-reasoner"
        else:
            model_name = "deepseek-chat"

        # 更新系统提示（包含当前时间和用户名）
        if (
            self.conversation_history
            and self.conversation_history[0]["role"] == "system"
        ):
            self.conversation_history[0]["content"] = get_system_prompt(self.pageIndex)
        else:
            self.conversation_history.insert(
                0, {"role": "system", "content": get_system_prompt(self.pageIndex)}
            )

        # 添加用户输入
        self.conversation_history.append({"role": "user", "content": self.user_input})

        # 定义可调用的函数
        tools = []
        if get_config("enable_baidu"):
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "baidu_search",
                        "description": "使用百度搜索引擎进行网络搜索，适用于获取中文网页内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "搜索关键词",
                                }
                            },
                            "required": ["query"],
                        },
                    },
                }
            )

        if get_config("enable_tavily"):
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "tavily_search",
                        "description": "使用Tavily搜索引擎进行深度网络搜索，适用于获取英文内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "搜索关键词",
                                }
                            },
                            "required": ["query"],
                        },
                    },
                }
            )

        # 处理对话流
        self.process_conversation(model_name, tools)

    def process_conversation(self, model_name, tools):
        """处理对话流，支持函数调用"""
        while self.running and self.function_call_count < self.max_function_calls:
            # 准备请求载荷
            payload = {
                "model": model_name,
                "messages": self.conversation_history,
                "stream": True,
            }

            # 只有在还有函数调用次数且配置启用了搜索时才提供工具
            if tools and self.function_call_count < self.max_function_calls:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"

            headers = {
                "Authorization": f"Bearer {get_config('api_key')}",
                "Content-Type": "application/json",
            }

            try:
                # 发送请求
                response = requests.post(
                    f"{get_config('base_url')}/chat/completions",
                    json=payload,
                    headers=headers,
                    stream=True,
                )

                if response.status_code != 200:
                    error_msg = (
                        f"请求失败 (状态码 {response.status_code}): {response.text}"
                    )
                    self.update_signal.emit("system", error_msg, False)
                    return

                # 处理流式响应
                tool_calls = []
                current_tool_call = None
                full_response = ""
                in_thinking = False
                role = "assistant"
                reasoning_content = ""

                for line in response.iter_lines():
                    if not self.running:
                        break

                    if line and b"data: [DONE]" not in line:
                        if line.startswith(b"data: "):
                            json_data = line[6:]
                            try:
                                chunk = json.loads(json_data)
                                if "choices" in chunk and chunk["choices"]:
                                    choice = chunk["choices"][0]
                                    delta = choice.get("delta", {})

                                    # 检查函数调用
                                    if "tool_calls" in delta and delta["tool_calls"]:
                                        for tool_delta in delta["tool_calls"]:
                                            # 新的函数调用
                                            if (
                                                "index" in tool_delta
                                                and tool_delta["index"] == 0
                                                and current_tool_call is None
                                            ):
                                                current_tool_call = {
                                                    "id": "",
                                                    "type": "function",
                                                    "function": {
                                                        "name": "",
                                                        "arguments": "",
                                                    },
                                                }

                                            # 更新函数调用信息
                                            if "id" in tool_delta:
                                                current_tool_call["id"] += tool_delta[
                                                    "id"
                                                ]
                                            if "function" in tool_delta:
                                                func_delta = tool_delta["function"]
                                                if "name" in func_delta:
                                                    current_tool_call["function"][
                                                        "name"
                                                    ] += func_delta["name"]
                                                if "arguments" in func_delta:
                                                    current_tool_call["function"][
                                                        "arguments"
                                                    ] += func_delta["arguments"]

                                    # 处理思考内容
                                    reasoning = delta.get("reasoning_content", "")
                                    if reasoning:
                                        reasoning_content += reasoning
                                        if not in_thinking:
                                            self.start_thinking.emit()
                                            self.status_signal.emit("🤔 正在思考...")
                                            in_thinking = True
                                        self.update_signal.emit(role, reasoning, True)

                                    # 处理回复内容
                                    content = delta.get("content", "")
                                    if content:
                                        if in_thinking:
                                            self.start_replying.emit(role)
                                            self.status_signal.emit(
                                                "💬 正在生成回复..."
                                            )
                                            in_thinking = False
                                        self.update_signal.emit(role, content, False)
                                        full_response += content
                            except json.JSONDecodeError:
                                continue

                # 如果有未完成的函数调用，添加到列表
                if current_tool_call:
                    tool_calls.append(current_tool_call)

                # 保存助手消息到对话历史
                assistant_message = {"role": "assistant", "content": full_response}

                # 如果有函数调用，添加到消息
                if tool_calls:
                    assistant_message["tool_calls"] = tool_calls

                self.conversation_history.append(assistant_message)

                # 如果有函数调用，执行函数
                if tool_calls:
                    self.function_call_count += 1
                    self.status_signal.emit("🔍 正在执行搜索...")

                    # 执行每个函数调用
                    for tool_call in tool_calls:
                        function_name = tool_call["function"]["name"]

                        # 安全解析参数
                        arguments_str = tool_call["function"]["arguments"].strip()
                        try:
                            function_args = json.loads(arguments_str)
                        except:
                            # 如果解析失败，使用默认参数
                            function_args = {"query": arguments_str}

                        # 执行对应的函数
                        if function_name == "baidu_search":
                            result = baidu_search(function_args.get("query", ""))
                        elif function_name == "tavily_search":
                            result = tavily_search(function_args.get("query", ""))
                        else:
                            result = f"⚠️ 未知函数: {function_name}"

                        # 发送搜索结果
                        self.search_complete.emit(result)

                        # 将函数结果添加到对话历史
                        self.conversation_history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": function_name,
                                "content": result,
                            }
                        )

                    # 继续对话
                    continue
                else:
                    # 没有函数调用，结束对话
                    self.status_signal.emit("✅ 回复生成完成")
                    return

            except requests.exceptions.RequestException as e:
                self.update_signal.emit("system", f"\n网络请求错误: {str(e)}", False)
                return

    def stop(self):
        self.running = False
