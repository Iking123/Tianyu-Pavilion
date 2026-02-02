import json
import os
import time
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from translate import TRANSLATE

DATA_PATH = os.path.join(os.getcwd(), "data")
# 配置文件路径（加密后）
CONFIG_ENC_PATH = os.path.join(DATA_PATH, "config.enc")
# 密钥文件路径（安全存储）
KEY_PATH = os.path.join(DATA_PATH, "config.key")

# 默认配置
DEFAULT_CONFIG = {
    "version": "1.04",
    "deepseek_api_key": "",
    "volcengine_api_key": "",
    "gemini_api_key": "",
    "tavily_api_key": "",
    "username": "",
    "enable_tavily": False,
    "enable_baidu": "自动",
    "model": "deepseek-chat",
    "enable_thinking": False,
    "reasoning_effort": "minimal",
    "speed_slider": 8,
    "ex_scroll_step": 60,
}

# 全局配置变量（单例）
_config = None


def _generate_key():
    """生成并保存加密密钥"""
    # 使用密码派生密钥增强安全性
    password = b"deepseek"
    salt = os.urandom(16)  # 随机盐值

    # 使用PBKDF2派生密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))

    # 保存密钥
    with open(KEY_PATH, "wb") as key_file:
        key_file.write(key)

    return key


def _get_key():
    """获取加密密钥（如果不存在则生成）"""
    os.makedirs(DATA_PATH, mode=0o777, exist_ok=True)

    if not os.path.exists(KEY_PATH):
        return _generate_key()

    with open(KEY_PATH, "rb") as key_file:
        return key_file.read()


def _encrypt_config(config_data):
    """加密配置数据"""
    key = _get_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(config_data).encode())
    return encrypted_data


def _decrypt_config(encrypted_data):
    """解密配置数据"""
    key = _get_key()
    f = Fernet(key)
    try:
        decrypted_data = json.loads(f.decrypt(encrypted_data))
        return decrypted_data
    except:
        # 解密失败时回退到默认配置
        return DEFAULT_CONFIG.copy()


def _init_default_config():
    """初始化默认配置（加密存储）"""
    encrypted_data = _encrypt_config(DEFAULT_CONFIG)
    with open(CONFIG_ENC_PATH, "wb") as f:
        f.write(encrypted_data)


def get_config(key=None):
    """获取配置（支持加密存储）"""
    global _config

    # 加载配置
    if _config is None:
        # 如果加密配置文件不存在，创建默认配置
        if not os.path.exists(CONFIG_ENC_PATH):
            _init_default_config()

        # 读取并解密配置
        with open(CONFIG_ENC_PATH, "rb") as f:
            encrypted_data = f.read()
            _config = _decrypt_config(encrypted_data)

    # 检查是否需要更新（用硬编码的默认值更新）
    if _config["version"] != DEFAULT_CONFIG["version"]:
        _config = {**DEFAULT_CONFIG, **_config}
        _config["version"] = DEFAULT_CONFIG["version"]
        update_config(_config)

    return _config if key is None else _config.get(key, None)


def get_username(show_developer: bool = False) -> str:
    """获取用户名，若为Iking且show_developer=True则显示开发者"""
    name = get_config("username")
    return (
        f"{name}（此用户为本平台开发者）"
        if name == "Iking" and show_developer
        else name
    )


def get_model() -> str:
    """获取现在的模型"""
    return get_config("model") or "deepseek-chat"


def get_model_name2():
    """获取现在的模型的另一种名称"""
    name = ""
    model = get_model()
    if model.startswith("deepseek"):
        name = "DeepSeek-V3.2"
    elif model == "doubao-seed-1-8-251228":
        name = "Doubao-Seed-1.8"
    elif model == "gemini-3-flash-preview":
        name = "Gemini 3 Flash"
    elif model == "gemini-2.5-flash":
        name = "Gemini 2.5 Flash"
    elif model == "gemini-2.5-flash-lite":
        name = "Gemini 2.5 Flash-Lite"
    elif model == "mistral-large-2512":
        name = "Mistral Large 3"
    elif model == "glm-4.7-flash":
        name = "GLM-4.7-Flash"
    return name


def get_assist(nature=False):
    """获取现在的助手名"""
    model = get_model()
    name = TRANSLATE.get(model, "")
    return name[10:] if nature else name


def get_base_url():
    """获取现在的base_url"""
    model = get_model()
    if model.startswith("deepseek"):
        return "https://api.deepseek.com/v1"
    elif model.startswith("doubao"):
        return "https://ark.cn-beijing.volces.com/api/v3"
    elif model.startswith("mistral"):
        return "https://api.mistral.ai/v1"
    elif model.startswith("glm"):
        return "https://open.bigmodel.cn/api/paas/v4"
    return ""


def get_api_key():
    """获取现在的api_key"""
    model = get_model()
    if model.startswith("deepseek"):
        return get_config("deepseek_api_key")
    elif model.startswith("doubao"):
        return get_config("volcengine_api_key")
    elif model.startswith("gemini"):
        return get_config("gemini_api_key")
    elif model.startswith("mistral"):
        return get_config("mistral_api_key")
    elif model.startswith("glm"):
        return get_config("glm_api_key")
    return ""


def get_system_prompt():
    """获取聊天页面系统提示，包含时间、用户名和函数调用说明"""
    # 基础系统提示
    prompt = "你是一个智能助手，在一个个人平台上与用户交流。"

    # 根据配置添加百度搜索说明
    baidu_config = get_config("enable_baidu")
    if baidu_config == "自动":
        prompt += "若用户提问涉及最新信息，则平台可能会为你提供百度搜索的简要结果。"
    elif baidu_config == "开":
        prompt += "对于用户的每次提问，平台都会为你提供百度搜索的简要结果。"

    # 根据配置添加Tavily搜索说明
    if get_config("enable_tavily"):
        prompt += "Tavily是一个联网搜索API，你可用tavily_search函数进行深度调查。调用函数时必须严格写有效JSON格式。"

    # 添加当前时间
    prompt += f"\n\n当前时间：{time.asctime()}"

    # 添加用户名
    name = get_username(True)
    if name:
        prompt += f"\n用户名：{name}"

    return prompt


def update_config(new_config):
    """更新配置（加密存储）"""
    global _config
    _config = new_config

    # 加密并保存新配置
    encrypted_data = _encrypt_config(new_config)
    with open(CONFIG_ENC_PATH, "wb") as f:
        f.write(encrypted_data)
