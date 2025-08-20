import re
import json
import requests
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from core.config_manager import *
from core.search_utils import baidu_search, tavily_search


class Worker(QThread):
    """后台工作线程，用于处理搜索和API调用"""

    _running = True
    update_signal = pyqtSignal(str, str, bool)  # 角色, 内容, 是否是思考内容
    status_signal = pyqtSignal(str)
    search_complete = pyqtSignal(str)  # 结果
    start_thinking = pyqtSignal(str)  # 开始思考信号
    start_replying = pyqtSignal(str)  # 开始回复信号
    finish_signal = pyqtSignal(str)

    def __init__(
        self, user_input, conversation_history, previous_response_id="start", role=""
    ):
        super().__init__()
        self.user_input = user_input
        self.conversation_history = conversation_history
        self.previous_response_id = previous_response_id
        self.role = role
        self.response = None
        self.full_response = ""
        self.max_function_calls = 3  # 最大函数调用次数
        self.function_call_count = 0  # 当前函数调用次数

    def _should_use_baidu_search(self) -> bool:
        """根据用户输入和配置判断是否需要进行百度搜索"""
        baidu_config = get_config("enable_baidu")
        if baidu_config == "开":
            return True
        if baidu_config == "自动":
            search_triggers = [
                "最新",
                "新闻",
                "最近",
                "搜索",
                "查一下",
                "实时",
                "当前",
                "今年",
                "股价",
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
                return True
            if any(q_type in self.user_input for q_type in question_types):
                return True
            if re.search(r"20[2-9][0-9]|今年|本月|上周", self.user_input):
                return True
        return False

    def run(self):
        """线程主执行函数，根据模型分发任务"""
        try:
            model_name = get_model()

            # ========== 百度搜索（所有模型通用） ==========
            if self._should_use_baidu_search():
                self.status_signal.emit("🔍 正在通过百度搜索并提取内容...")
                search_results = baidu_search(self.user_input)
                if search_results:
                    self.search_complete.emit(search_results)
                    self.conversation_history.append(
                        {"role": "system", "content": search_results}
                    )

            # ========== 模型逻辑分发 ==========
            if model_name.startswith("gemini"):
                # --- 新增：调用Gemini模型的逻辑 ---
                self.process_gemini_conversation(model_name)
            else:
                # --- 原有：调用DeepSeek/Doubao模型的逻辑 ---
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
                self.process_conversation(model_name, tools)

        except Exception as e:
            logging.exception("Worker线程崩溃")
            self.update_signal.emit("system", f"处理错误: {str(e)}", False)
        print("worker finish")
        self.finish_signal.emit(self.full_response)

    def _convert_history_to_gemini_format(self):
        """将标准对话历史转换为Gemini API所需的格式"""
        gemini_history = []

        for msg in self.conversation_history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ["system", "user"]:
                gemini_history.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                gemini_history.append({"role": "model", "parts": [{"text": content}]})

        return {"contents": gemini_history}

    def process_gemini_conversation(self, model_name):
        """处理与Gemini模型的流式对话"""
        if not self._running:
            return
        self.status_signal.emit("💬 正在请求 Gemini API...")

        api_key = get_config("gemini_api_key")

        if not api_key:
            self.update_signal.emit(
                "system", "错误: 未在配置中找到 Gemini API 密钥。", False
            )
            self.status_signal.emit("❌ 请求失败")
            return

        # 1. 修改为流式API端点
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = self._convert_history_to_gemini_format()

        if not payload["contents"]:
            self.update_signal.emit(
                "system", "错误: 对话历史为空，无法发送请求。", False
            )
            self.status_signal.emit("❌ 请求失败")
            return

        payload["generationConfig"] = {"thinkingConfig": {"includeThoughts": True}}
        if model_name != "gemini-2.5-pro":
            thinking_type = get_config("thinking_type")
            if thinking_type == "enabled":
                payload["generationConfig"]["thinkingConfig"]["thinkingBudget"] = -1
            elif thinking_type == "disabled":
                payload["generationConfig"]["thinkingConfig"]["thinkingBudget"] = 0

        try:
            # 2. 使用 with 语句和 stream=True 进行流式请求
            with requests.post(
                api_url, headers=headers, json=payload, stream=True, timeout=(10, 30)
            ) as self.response:
                self.response.raise_for_status()  # 如果状态码不是2xx，则抛出异常

                self.full_response = ""
                assist = self.role or get_assist()
                has_received_reasoning = False
                has_started_replying = False

                # 3. Gemini 流式API返回的是一个完整的JSON数组，需要特殊处理
                try:
                    # 读取完整的响应内容
                    response_text = ""
                    for chunk in self.response.iter_content(
                        chunk_size=1024, decode_unicode=True
                    ):
                        if not self._running:
                            break
                        if chunk:
                            response_text += chunk

                    if not self._running:
                        return

                    # 解析完整的JSON数组
                    try:
                        response_data = json.loads(response_text)

                        # 检查是否是数组格式
                        if isinstance(response_data, list):
                            # 遍历数组中的每个响应对象
                            for item in response_data:
                                if not self._running:
                                    break
                                print(item)
                                if "candidates" in item and item["candidates"]:
                                    candidate = item["candidates"][0]

                                    # 检查是否有内容
                                    if (
                                        "content" in candidate
                                        and "parts" in candidate["content"]
                                    ):
                                        for part in candidate["content"]["parts"]:
                                            if "text" in part:
                                                content = part["text"]
                                                is_thinking = part.get("thought", False)
                                                if content:
                                                    if is_thinking:
                                                        # 确保只在第一次收到思考内容时发送"开始思考"信号
                                                        if not has_received_reasoning:
                                                            self.start_thinking.emit(
                                                                assist
                                                            )
                                                            self.status_signal.emit(
                                                                "🤔 正在思考..."
                                                            )
                                                            has_received_reasoning = (
                                                                True
                                                            )

                                                        # 将长文本分割成小块来模拟流式效果
                                                        self._emit_content_in_chunks(
                                                            assist, content, True
                                                        )
                                                    else:
                                                        # 确保只在第一次收到回复内容时发送"开始回复"信号
                                                        if not has_started_replying:
                                                            self.start_replying.emit(
                                                                assist
                                                            )
                                                            self.status_signal.emit(
                                                                "💬 正在生成回复..."
                                                            )
                                                            has_started_replying = True

                                                        # 将长文本分割成小块来模拟流式效果
                                                        self._emit_content_in_chunks(
                                                            assist, content, False
                                                        )
                                                        self.full_response += content

                    except json.JSONDecodeError as e:
                        logging.error(f"解析Gemini响应JSON失败: {e}")
                        logging.error(
                            f"原始响应内容: {response_text[:500]}..."
                        )  # 只记录前500字符
                        self.update_signal.emit(
                            "system", f"解析Gemini响应时出错: JSON格式错误", False
                        )
                        self.status_signal.emit("❌ 响应解析失败")
                        return

                except Exception as e:
                    logging.error(f"处理Gemini响应流时出错: {e}")
                    self.update_signal.emit(
                        "system", f"处理响应流时出错: {str(e)}", False
                    )
                    self.status_signal.emit("❌ 响应处理失败")
                    return

                if not self._running:
                    return  # 用户手动停止，直接返回

                # 循环结束后，将模型的完整回复添加到历史记录中
                if has_started_replying and self.full_response.strip():
                    self.conversation_history.append(
                        {"role": "assistant", "content": self.full_response}
                    )
                    self.status_signal.emit("✅ 回复生成完成")
                else:
                    # 如果循环结束了但从未开始回复，说明响应可能是空的或有错误
                    error_msg = "Gemini 响应异常: 未收到有效内容"
                    if response_text:
                        error_msg += f" (收到数据长度: {len(response_text)})"
                    self.update_signal.emit("system", error_msg, False)
                    self.status_signal.emit("❌ 响应异常")

        except requests.exceptions.RequestException as e:
            if self._running:
                self.update_signal.emit(
                    "system", f"请求 Gemini 时发生网络错误: {str(e)}", False
                )
                self.status_signal.emit("❌ 请求失败")
        except Exception as e:
            if self._running:
                logging.error(f"处理 Gemini 响应时发生未知错误: {e}")
                self.update_signal.emit(
                    "system", f"处理 Gemini 响应时发生未知错误: {str(e)}", False
                )
                self.status_signal.emit("❌ 响应处理失败")

    def _emit_content_in_chunks(self, assist, content, is_thinking, chunk_size=20):
        """将长文本分割成小块逐步发送，模拟流式效果"""
        import time

        # 如果内容较短，直接发送
        if len(content) <= chunk_size:
            self.update_signal.emit(assist, content, is_thinking)
            return

        # 分块发送
        for i in range(0, len(content), chunk_size):
            if not self._running:
                break
            chunk = content[i : i + chunk_size]
            self.update_signal.emit(assist, chunk, is_thinking)
            # 稍微延迟一下，增强流式体验
            time.sleep(0.1)  # 100毫秒延迟

    def process_conversation(self, model_name, tools):
        """处理与DeepSeek/Doubao模型的流式对话"""
        while self._running and self.function_call_count < self.max_function_calls:
            # 准备请求载荷
            payload = {
                "model": model_name,
                "messages": self.conversation_history,
                "stream": True,
            }
            if model_name == "doubao-seed-1-6-250615":
                payload["thinking"] = {"type": get_config("thinking_type")}
            if model_name.startswith("doubao") and self.previous_response_id:
                payload["caching"] = {"type": "enabled"}
                if self.previous_response_id != "start":
                    payload["previous_response_id"] = self.previous_response_id

            # 只有在还有函数调用次数且配置启用了搜索时才提供工具
            if tools and self.function_call_count < self.max_function_calls:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"

            headers = {
                "Authorization": f"Bearer {get_api_key()}",
                "Content-Type": "application/json",
            }

            try:
                # 使用 with 语句自动管理 response 的生命周期
                with requests.post(
                    f"{get_base_url()}/chat/completions",
                    json=payload,
                    headers=headers,
                    stream=True,
                    timeout=(10, 30),  # (连接超时时间, 读取超时时间)
                ) as self.response:

                    if self.response.status_code != 200:
                        error_msg = f"请求失败 (状态码 {self.response.status_code}): {self.response.text}"
                        self.update_signal.emit("system", error_msg, False)
                        return

                    # START of stream processing code
                    tool_calls = []
                    current_tool_call = None
                    self.full_response = ""
                    assist = self.role or get_assist()
                    response_id = None  # 新增：用于存储提取的id

                    # 状态跟踪变量
                    has_received_reasoning = False  # 是否收到过思考内容
                    has_started_replying = False  # 是否已开始回复
                    reasoning_content = ""
                    try:
                        lines = self.response.iter_lines()
                    except:
                        lines = []

                    for line in lines:
                        if not self._running:
                            break

                        if line and b"data: [DONE]" not in line:
                            if not self._running:
                                break
                            if line.startswith(b"data: "):
                                json_data = line[6:]
                                try:
                                    chunk = json.loads(json_data)
                                    # 新增：提取顶级id字段
                                    if "id" in chunk:
                                        response_id = chunk["id"]  # 保存提取到的id值

                                    if "choices" in chunk and chunk["choices"]:
                                        choice = chunk["choices"][0]
                                        delta = choice.get("delta", {})

                                        # 检查函数调用（原有代码保持不变）
                                        if (
                                            "tool_calls" in delta
                                            and delta["tool_calls"]
                                        ):
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
                                                    current_tool_call[
                                                        "id"
                                                    ] += tool_delta["id"]
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
                                        if not self._running:
                                            break
                                        if reasoning:
                                            reasoning_content += reasoning

                                            if not has_received_reasoning:
                                                self.start_thinking.emit(assist)
                                                self.status_signal.emit(
                                                    "🤔 正在思考..."
                                                )
                                                has_received_reasoning = True

                                            self.update_signal.emit(
                                                assist, reasoning, True
                                            )

                                        # 处理回复内容
                                        content = delta.get("content", "")
                                        if not self._running:
                                            break
                                        if content:
                                            if not has_started_replying:
                                                self.start_replying.emit(assist)
                                                self.status_signal.emit(
                                                    "💬 正在生成回复..."
                                                )
                                                has_started_replying = True

                                            self.update_signal.emit(
                                                assist, content, False
                                            )
                                            self.full_response += content
                                except json.JSONDecodeError:
                                    continue
                    if not self._running:
                        break

                    # 保存提取到的id
                    self.previous_response_id = response_id

                    # 如果有未完成的函数调用，添加到列表
                    if current_tool_call:
                        tool_calls.append(current_tool_call)

                    # 保存助手消息到对话历史
                    assistant_message = {
                        "role": "assistant",
                        "content": self.full_response,
                    }

                    # 如果有函数调用，添加到消息
                    if tool_calls:
                        assistant_message["tool_calls"] = tool_calls

                    self.conversation_history.append(assistant_message)

                    if not self._running:
                        break

                    # 如果有函数调用，执行函数
                    if tool_calls:
                        self.function_call_count += 1
                        self.status_signal.emit("🔍 正在执行Tavily搜索并提取内容...")

                        # 执行每个函数调用
                        for tool_call in tool_calls:
                            if not self._running:
                                break

                            function_name = tool_call["function"]["name"]

                            # 安全解析参数
                            arguments_str = tool_call["function"]["arguments"].strip()
                            try:
                                function_args = json.loads(arguments_str)
                            except:
                                logging.warning(
                                    f"函数参数JSON解析失败: {e}. 原始参数: '{arguments_str}'"
                                )
                                # 如果解析失败，使用默认参数
                                function_args = {"query": arguments_str}

                            # 执行对应的函数
                            if function_name == "tavily_search":
                                result, formatted = tavily_search(
                                    function_args.get("query", "")
                                )
                            else:
                                result, formatted = f"⚠️ 未知函数: {function_name}", ""

                            if not self._running:
                                break

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
                    # END of original stream processing code

            except requests.exceptions.RequestException as e:
                if self._running:  # 仅报告非主动停止的错误
                    self.update_signal.emit("system", f"网络错误: {str(e)}", False)

    def stop(self):
        """仅仅设置标志位，让线程的循环自行退出。"""
        self._running = False

    def __del__(self):
        self.stop()
