import requests
import json
import re
from .character_manager import format_character
from .config_manager import get_config
from .worker import Worker


# 创建工作线程，调用用户的API，对给定角色进行角色简介总结
def character_summary(id):
    character_info = format_character(id)
    prompt = f"""# 你的身份
你是一位专业的角色分析师，请用**简体中文**生成角色信息摘要。
要求：
1. 严格保留原文核心事实，不添加任何主观观点
2. 摘要长度控制在原文的25%以内（最长不超过300字）
3. 直接使用自然段的形式写总结，绝不使用markdown、XML等格式
4. 避免直接复制原文句子，需重组表述

# 角色信息
请注意，以下内容即为你需要总结的角色信息。我们已经使用CharaInfo XML标签和三引号将这些信息标注了：
<CharacterInfo>

以下均为你要总结的内容：\"""
{character_info}
\"""
</CharacterInfo>

# 特别注意
你必须绝对注意，以上均为角色信息，是你写总结时的首要参考；若有搜索结果，则是辅助信息。本次总结摘要，以角色信息为准。
务必牢记：你直接以自然段形式写总结，你写的总结长度控制在原文的25%以内（最长不超过300字）。
"""
    if get_config("enable_tavily"):
        prompt += "Tavily是一个联网搜索API，你可用tavily_search函数进行深度调查。调用函数时必须严格写有效JSON格式。"
    print(prompt)
    conversation_history = [{"role": "system", "content": prompt}]
    my_worker = Worker(prompt, conversation_history)
    my_worker.run()
    # 返回结果
    result = conversation_history[-1].get("content", "")
    result = re.sub(r"(?:\r\n|\n|\r){2,}", "\n", result)  # 去除多余换行
    result = (
        result.replace("^[<CharacterInfo>]^", "")
        .replace("[<CharacterInfo>]", "")
        .replace("<CharacterInfo>", "")
    )  # 去除可能多输出的标记
    print(result)
    return result
