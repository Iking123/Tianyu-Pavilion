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
    "original_system_prompt": "你是一个智能助手，在一个个人平台上与用户交流。若用户提问涉及最新信息，则平台可能会为你提供百度搜索的简要结果，还可能提供调用Tavily API搜索到的结果，辅助你更好地解答。",
    "render_threshold": 2,
    "username": "",
    "enable_r1": False,
    "enable_tavily": False,
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


def get_system_prompt():
    """获取系统提示，带时间，也可能带用户名"""
    prompt = f"{get_config("original_system_prompt")}\n当前时间：{time.asctime()}"
    name = get_username()
    return f"{prompt}\n用户名：{name}" if name else prompt


def update_config(new_config):
    """更新配置"""
    global _config
    _config = new_config
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(_config, f, indent=4, ensure_ascii=False)
