import json
import os
import time

# 配置文件路径
CONFIG_PATH = "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "version": "1.0",
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "你的deepseek api",
    "tavily_api_key": "你的tavily api",
    "render_threshold": 0.3,
    "username": "",
    "enable_r1": False,
    "enable_tavily": False,
    "enable_baidu": True,
}


def _init_default_config():
    """初始化默认配置（若文件不存在）"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)


# 真正的版本
VERSION = "1.0"

# 全局配置变量（单例）
_config = None


def get_config(key=None):
    global _config
    if _config and _config["version"] != VERSION:
        _config = None
    if _config is None:
        # 加载配置
        if not os.path.exists(CONFIG_PATH):
            _init_default_config()
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config = json.load(f)
    return _config if key == None else _config[key]


def get_username(show_developer=True):
    """获取用户名，若为Iking则显示开发者"""
    name = get_config("username")
    return (
        f"{name}（此用户为本平台开发者）"
        if name == "Iking" and show_developer
        else name
    )


SYSTEM_PROMPT = [
    "",
    [
        [
            "由于用户的设置，你暂时无法联网。",
            "若用户提问涉及最新信息，则平台可能会为你提供调用Tavily API搜索到的结果，辅助你更好地解答。",
        ],
        [
            "若用户提问涉及最新信息，则平台可能会为你提供百度搜索的简要结果，辅助你更好地解答。",
            "若用户提问涉及最新信息，则平台可能会为你提供百度搜索的简要结果，还可能提供调用Tavily API搜索到的结果，辅助你更好地解答。",
        ],
    ],
]


def get_system_prompt(p=1):
    """获取系统提示，可能含时间与用户名"""
    match p:
        case 1:
            prompt = f"你是一个智能助手，在一个个人平台上与用户交流。{SYSTEM_PROMPT[p][get_config("enable_baidu")][get_config("enable_tavily")]}\n当前时间：{time.asctime()}"
            name = get_username()
            return f"{prompt}\n用户名：{name}" if name else prompt


def update_config(new_config):
    """更新配置"""
    global _config
    _config = new_config
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(_config, f, indent=4, ensure_ascii=False)
