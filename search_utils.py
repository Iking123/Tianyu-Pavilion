import re
import time
import requests
from tavily import TavilyClient
from openai import OpenAI
from config_manager import *

# 初始化客户端
client = OpenAI(api_key=get_config("api_key"), base_url=get_config("base_url"))
tavily_client = TavilyClient(api_key=get_config("tavily_api_key"))
headers = {
    "Authorization": f"Bearer {get_config("api_key")}",
    "Content-Type": "application/json",
}


class SearchAssistant:
    def __init__(self, prefindings=""):
        self.topics = ""
        self.findings = ""
        self.prefindings = prefindings

    def llm_search(self, query, findings, topics):
        system_role = """
        你是一个智能助手，在一个个人平台上进行搜索调查，你懂得节约API调用次数。
        你正在调查以下主题，如果你觉得当前信息结合你的知识，已经够用（勉强也行），那就停止搜索；否则继续搜索（调查你还很不确定的方面）。

        输出内容
        你必须以JSON格式输出；绝对不要输出与已搜索主题完全相同的主题。
        如果需要进一步搜索信息，请设置 "nextSearchTopic"（下次搜索主题）。
        如果信息已够用，请将 "break"（退出搜索）设置为 true。
        
        示例输出1
        {
            "nextSearchTopic": "2025年热点事件",
            "break": false   
        }
        
        示例输出2
        {
            "nextSearchTopic": "2024年诺贝尔奖与AI相关的获奖者及其贡献",
            "break": false
        }
        
        示例输出3
        {
            "nextSearchTopic": null,
            "break": true
        }
        
        特别地，如果要调查的主题涉及你自己或者本平台，则你已知，此时你必须直接按示例输出3输出。
        """

        system_input = f"""
        # 主题
        {query}

        # 当前发现
        {findings}

        # 已搜索的主题
        {topics}
        
        # 当前时间
        {time.asctime()}
        """
        name = get_username()
        if name:
            system_input += f"\n# 当前用户\n{name}"

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "system", "content": system_input},
            ],
            model="deepseek-chat",
            response_format={"type": "json_object"},
        )
        return chat_completion.choices[0].message.content

    def tavily_search(self, user_input):
        response = tavily_client.search(user_input)
        return str(response.get("results"))

    def extract_value_from_str(self, str_data, key):
        pattern = rf'"{re.escape(key)}":\s*((".*?")|([^,}}]+))'
        match = re.search(pattern, str_data)
        if match:
            value = match.group(1).strip().strip('"')
            return value
        print(f"未找到键 '{key}' 对应的匹配项。")
        return None

    def search(self, depth, user_input):
        index = 0
        while index < depth:
            text = self.llm_search(
                user_input, "\n".join([self.prefindings, self.findings]), self.topics
            )
            print(f"\n模型响应: {text}")

            nextSearchTopic = self.extract_value_from_str(text, "nextSearchTopic")
            shouldBreak = self.extract_value_from_str(text, "break")

            if shouldBreak and shouldBreak.lower() == "false":
                if index == 0:
                    self.findings += "【Tavily搜索结果】\n"
                self.topics = nextSearchTopic
                print(f"\n执行搜索: {nextSearchTopic}")
                search_results = self.tavily_search(nextSearchTopic)
                self.findings += search_results
                print(f"第{index + 1}/{depth}次搜索完成，结果已添加到发现中")
                print(f"{search_results}\n")
                index += 1
            else:
                print("\n模型指示停止搜索")
                break

        print("\n所有搜索结果汇总:")
        print(
            self.findings[:500] + "..." if len(self.findings) > 500 else self.findings
        )
        return self.findings


def baidu_search(query, max_results=5):
    """使用百度搜索并获取网页信息"""
    try:
        from baidusearch.baidusearch import search

        tried_nums = 0
        results = []
        while tried_nums < 5 and len(results) < max_results:
            tried_nums += 1
            # 执行百度搜索
            results = search(query, num_results=max_results)

        # 格式化结果
        formatted = "【百度搜索结果】\n"
        for idx, item in enumerate(results):
            title = item.get("title", "无标题")
            url = item.get("url", "#")
            abstract = item.get("abstract", "无摘要")

            # 清理摘要
            abstract = re.sub(r"<[^>]+>", "", abstract)  # 清除HTML标签
            abstract = re.sub(r"(?:\r\n|\n|\r){2,}", "\n", abstract)  # 减少多余换行

            formatted += f"🔍 结果 {idx+1}:\n"
            formatted += f"   - 标题: {title}\n"
            formatted += f"   - 链接: {url}\n"
            formatted += f"   - 摘要: {abstract}\n"

        formatted = formatted.strip()
        print("\n")
        print(formatted)
        return formatted

    except Exception as e:
        return f"⚠️ 百度搜索失败: {str(e)}"
