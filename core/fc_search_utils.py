import re
import time
import requests
from tavily import TavilyClient
from openai import OpenAI
from core.config_manager import *

# 初始化客户端
client = OpenAI(api_key=get_config("api_key"), base_url=get_config("base_url"))


def baidu_search(query, max_results=5):
    """使用百度搜索并获取网页信息"""
    try:
        from baidusearch.baidusearch import search

        # 确保query是字符串
        if not isinstance(query, str):
            query = str(query)

        # 重试逻辑
        for _ in range(3):
            try:
                results = search(query, num_results=max_results)
                if results and len(results) > 0:
                    break
            except Exception as e:
                print(f"百度搜索异常: {str(e)}")
                time.sleep(1)
        else:
            return "⚠️ 百度搜索失败: 无法获取结果"

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

        return formatted.strip()

    except Exception as e:
        return f"⚠️ 百度搜索失败: {str(e)}"


def tavily_search(query):
    """使用Tavily搜索并返回结果"""
    if not get_config("enable_tavily"):
        return "Tavily搜索功能未启用"

    try:
        # 确保每次调用都重新创建客户端
        tavily_client = TavilyClient(api_key=get_config("tavily_api_key"))
        response = tavily_client.search(query)
        results = response.get("results", [])

        # 限制结果数量
        max_results = min(3, len(results))

        # 格式化结果
        formatted = "【Tavily搜索结果】\n"
        for idx in range(max_results):
            item = results[idx]
            title = item.get("title", "无标题")
            url = item.get("url", "#")
            content = item.get("content", "无内容")

            formatted += f"🔍 结果 {idx+1}:\n"
            formatted += f"   - 标题: {title}\n"
            formatted += f"   - 链接: {url}\n"
            formatted += f"   - 内容: {content}...\n"

        return formatted
    except Exception as e:
        return f"⚠️ Tavily搜索失败: {str(e)}"
