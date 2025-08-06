import re
import json
import requests
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from core.config_manager import *
from core.search_utils import baidu_search, tavily_search


class Worker(QThread):
    """后台工作线程，用于处理搜索和API调用"""

    update_signal = pyqtSignal(str, str, bool)  # 角色, 内容, 是否是思考内容
    status_signal = pyqtSignal(str)
    search_complete = pyqtSignal(str)  # 结果
    start_thinking = pyqtSignal(str)  # 开始思考信号
    start_replying = pyqtSignal(str)  # 开始回复信号

    def __init__(self, user_input, conversation_history, pageIndex=None):
        super().__init__()
        self.user_input = user_input
        self.conversation_history = conversation_history
        self.pageIndex = pageIndex
        self.running = True
        self.response = None
        self.max_function_calls = 3  # 最大函数调用次数
        self.function_call_count = 0  # 当前函数调用次数

    def run(self):
        try:
            # 根据配置选择模型
            model_name = get_model()

            # 若是聊天页面，更新系统提示（包含当前时间和用户名）
            if self.pageIndex == 1:
                if (
                    self.conversation_history
                    and self.conversation_history[0]["role"] == "system"
                ):
                    self.conversation_history[0]["content"] = get_system_prompt()
                else:
                    self.conversation_history.insert(
                        0, {"role": "system", "content": get_system_prompt()}
                    )

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
            if need_search:
                self.status_signal.emit("🔍 正在通过百度搜索并提取内容...")
                search_results = baidu_search(self.user_input)
                if search_results:
                    self.search_complete.emit(search_results)
                    self.conversation_history.append(
                        {"role": "system", "content": search_results}
                    )

            # ========== 定义可调用的函数 ==========
            tools = []
            if get_config("enable_tavily"):
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": "tavily_search",
                            "description": "使用Tavily搜索引擎进行深度网络搜索",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "搜索要调查的主题，尽量用英文",
                                    }
                                },
                                "required": ["query"],
                            },
                        },
                    }
                )

            # ========== 处理对话流 ==========
            self.process_conversation(model_name, tools)

        except Exception as e:
            logging.exception("Worker线程崩溃")
            self.update_signal.emit("system", f"处理错误: {str(e)}", False)

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
                "Authorization": f"Bearer {get_api_key()}",
                "Content-Type": "application/json",
            }

            try:
                # 发送请求
                self.response = requests.post(
                    f"{get_base_url()}/chat/completions",
                    json=payload,
                    headers=headers,
                    stream=True,
                )

                if self.response.status_code != 200:
                    error_msg = f"请求失败 (状态码 {self.response.status_code}): {self.response.text}"
                    self.update_signal.emit("system", error_msg, False)
                    return

                # 处理流式响应
                tool_calls = []
                current_tool_call = None
                full_response = ""
                assist = get_assist()

                # 状态跟踪变量
                has_received_reasoning = False  # 是否收到过思考内容
                has_started_replying = False  # 是否已开始回复
                reasoning_content = ""
                try:
                    lines = self.response.iter_lines()
                except:
                    lines = []
                for line in lines:
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

                                        # 如果是第一次收到思考内容，触发思考信号
                                        if not has_received_reasoning:
                                            self.start_thinking.emit(assist)
                                            self.status_signal.emit("🤔 正在思考...")
                                            has_received_reasoning = True

                                        self.update_signal.emit(assist, reasoning, True)

                                    # 处理回复内容
                                    content = delta.get("content", "")
                                    if content:
                                        # 如果是第一次收到回复内容，触发回复信号
                                        if not has_started_replying:
                                            self.start_replying.emit(assist)
                                            self.status_signal.emit(
                                                "💬 正在生成回复..."
                                            )
                                            has_started_replying = True

                                        self.update_signal.emit(assist, content, False)
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
                    self.status_signal.emit("🔍 正在执行Tavily搜索并提取内容...")

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
                        if function_name == "tavily_search":
                            result, formatted = tavily_search(
                                function_args.get("query", "")
                            )
                        else:
                            result, formatted = f"⚠️ 未知函数: {function_name}", ""

                        # 发送格式化后的搜索结果
                        self.search_complete.emit(formatted)

                        # 将函数结果添加到对话历史
                        self.conversation_history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": function_name,
                                "content": json.dumps(result, ensure_ascii=False),
                            }
                        )

                    # 继续对话
                    continue
                else:
                    # 没有函数调用，结束对话
                    self.status_signal.emit("✅ 回复生成完成")
                    return

            except requests.exceptions.RequestException as e:
                if self.running:  # 仅报告非主动停止的错误
                    self.update_signal.emit("system", f"网络错误: {str(e)}", False)

    def stop(self):
        self.running = False
        if self.response:
            try:
                self.response.close()  # 强制关闭连接
            except:
                pass

    def __del__(self):
        self.stop()
