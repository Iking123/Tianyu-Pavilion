import requests
import time
import random
import string
import re


# 真实浏览器请求头模板（定期更新）
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "v1.hitokoto.cn",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "",
}

# 轮换User-Agent池（定期更新）
USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
]

NAMES = [
    "童溟",
    "洛清河",
    "薄野汰漓",
    "冷雯霏",
    "月光寒",
    "傲圣",
    "鹿目司",
    "童禛",
    "莫白",
    "耿星河",
    "童忻",
    "闵维",
]

HARDCODE_QUOTES = [
    {"content": "学而时习之，不亦说乎？", "from_who": "孔子"},
    {"content": "想象力比知识更重要。", "from_who": "爱因斯坦"},
    {"content": "民有、民治、民享的政府。", "from_who": "亚伯拉罕·林肯"},
    {"content": "以眼还眼，使世界盲目；以爱还爱，使世界光明。", "from_who": "圣雄甘地"},
    {"content": "教育是改变世界最强大的武器。", "from_who": "纳尔逊·曼德拉"},
    {"content": "生活中没有可怕的东西，只有需要理解的东西。", "from_who": "玛丽·居里"},
    {"content": "学习永远不会使心灵疲倦。", "from_who": "列奥纳多·达·芬奇"},
    {
        "content": "To be or not to be, that is the question.",
        "from_who": "威廉·莎士比亚",
    },
    {"content": "我有一个梦想。", "from_who": "马丁·路德·金"},
    {
        "content": "如果我看得远，那是因为我站在巨人的肩膀上。",
        "from_who": "艾萨克·牛顿",
    },
    {
        "content": "天才就是百分之一的灵感加百分之九十九的汗水。",
        "from_who": "托马斯·爱迪生",
    },
    {"content": "早睡早起，使人健康、富有、聪明。", "from_who": "本杰明·富兰克林"},
    {
        "content": "人的生命应该这样度过：当他回首往事时，不因虚度年华而悔恨。",
        "from_who": "尼古拉·奥斯特洛夫斯基",
    },
    {"content": "Stay hungry, stay foolish.", "from_who": "史蒂夫·乔布斯"},
    {"content": "永不放弃。", "from_who": "温斯顿·丘吉尔"},
    {"content": "虽然我看不见世界，但世界可以看见我。", "from_who": "海伦·凯勒"},
    {
        "content": "你可以欺骗所有人一时，但不能欺骗所有人一世。",
        "from_who": "亚伯拉罕·林肯",
    },
    {"content": "真理是神。", "from_who": "圣雄甘地"},
    {"content": "艺术永无止境。", "from_who": "列奥纳多·达·芬奇"},
    {"content": "优秀不是一种行为，而是一种习惯。", "from_who": "亚里士多德"},
    {"content": "智慧的生活是避免不必要的痛苦。", "from_who": "伯特兰·罗素"},
    {"content": "知识就是回忆。", "from_who": "柏拉图"},
    {"content": "我唯一知道的就是我一无所知。", "from_who": "苏格拉底"},
    {"content": "己所不欲，勿施于人。", "from_who": "孔子"},
    {"content": "道可道，非常道。", "from_who": "老子"},
    {"content": "艺术是谎言，让我们认识真理。", "from_who": "巴勃罗·毕加索"},
    {
        "content": "哲学家们只是用不同的方式解释世界，而问题在于改变世界。",
        "from_who": "卡尔·马克思",
    },
    {"content": "以非暴力抵抗不公正。", "from_who": "圣雄甘地"},
    {"content": "自由不仅仅是不被锁链束缚。", "from_who": "纳尔逊·曼德拉"},
    {
        "content": "宇宙中最不可理解的事情是它是可以理解的。",
        "from_who": "阿尔伯特·爱因斯坦",
    },
]


def is_punctuation(char):
    """判断是否是标点"""
    # 检查是否为西文标点
    if char in string.punctuation:
        return True

    # 检查是否为中文标点（使用Unicode范围）
    if re.search(r"[\u3000-\u303F\uFF00-\uFFEF]", char):
        return True

    return False


def get_realistic_headers():
    """生成真实浏览器请求头"""
    headers = HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    return headers


def get_hitokoto_with_speaker():
    """获取一言API的名言金句（带反爬虫绕过，带说话人）"""
    url = "https://v1.hitokoto.cn/?max_length=999"
    result = {"content": "", "from_who": ""}
    # 尝试不同策略
    try:
        # 策略1：使用真实请求头
        headers = get_realistic_headers()
        response = requests.get(url, headers=headers, timeout=5, verify=True)

        # 策略2：若403则尝试备用域名
        if response.status_code == 403:
            url = "https://international.v1.hitokoto.cn/?max_length=999"
            response = requests.get(url, headers=headers, timeout=5, verify=True)

        response.raise_for_status()

        data = response.json()
        result["content"] = data["hitokoto"]
        if not is_punctuation(result["content"][-1]):
            result["content"] += "。"
        if from_who := data.get("from_who"):
            result["from_who"] = from_who

    except requests.exceptions.RequestException as e:
        # 策略3：直接用硬编码
        result = random.choice(HARDCODE_QUOTES)

    who = result.get("from_who")
    if not who or who in ["佚名", "不到啊", "不重要"]:
        result["from_who"] = random.choice(NAMES)
    return result


if __name__ == "__main__":
    print("今日箴言:")
    print(get_hitokoto_with_speaker())
