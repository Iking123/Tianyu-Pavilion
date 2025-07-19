import json
import os
import time
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 配置文件路径（加密后）
CONFIG_ENC_PATH = "config.enc"
# 密钥文件路径（安全存储）
KEY_PATH = "config.key"

# 默认配置
DEFAULT_CONFIG = {
    "version": "1.0",
    "deepseek_api_key": "",
    "volcengine_api_key": "",
    "tavily_api_key": "",
    "username": "",
    "enable_r1": False,
    "enable_tavily": False,
    "enable_baidu": True,
    "speed_slider": 8,
    "model": "deepseek-chat",
}

# 真正的版本
VERSION = "1.0"

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

    # 检查配置是否需要更新
    if _config and _config["version"] != VERSION:
        _config = None

    # 加载配置
    if _config is None:
        # 如果加密配置文件不存在，创建默认配置
        if not os.path.exists(CONFIG_ENC_PATH):
            _init_default_config()

        # 读取并解密配置
        with open(CONFIG_ENC_PATH, "rb") as f:
            encrypted_data = f.read()
            _config = _decrypt_config(encrypted_data)

    return _config if key is None else _config.get(key, None)


def get_username(show_developer=True):
    """获取用户名，若为Iking则显示开发者"""
    name = get_config("username")
    return (
        f"{name}（此用户为本平台开发者）"
        if name == "Iking" and show_developer
        else name
    )


def get_model():
    """获取现在的模型"""
    return get_config("model")


def get_assist():
    """获取现在的助手名"""
    model = get_model()
    if model == "deepseek-reasoner":
        return "assistant_DeepSeek-R1"
    elif model == "deepseek-chat":
        return "assistant_DeepSeek-V3"
    elif model == "doubao-seed-1-6-thinking-250715":
        return "assistant_豆包1.6 Thinking"
    elif model == "doubao-seed-1-6-250615":
        return "assistant_豆包1.6"


def get_base_url():
    """获取现在的base_url"""
    model = get_model()
    if model.startswith("deepseek"):
        return "https://api.deepseek.com/v1"
    return "https://ark.cn-beijing.volces.com/api/v3"


def get_api_key():
    """获取现在的api_key"""
    model = get_model()
    if model.startswith("deepseek"):
        return get_config("deepseek_api_key")
    return get_config("volcengine_api_key")


def get_system_prompt():
    """获取聊天页面系统提示，包含时间、用户名和函数调用说明"""
    # 基础系统提示
    prompt = "你是一个智能助手，在一个个人平台上与用户交流。"

    # 根据配置添加百度搜索说明
    if get_config("enable_baidu"):
        prompt += "若用户提问涉及最新信息，则平台可能会为你提供百度搜索的简要结果。"

    # 根据配置添加Tavily搜索说明
    if get_config("enable_tavily"):
        prompt += "Tavily是一个联网搜索API，你可用tavily_search函数进行深度调查。调用函数时必须严格写有效JSON格式。"

    # 添加当前时间
    prompt += f"\n\n当前时间：{time.asctime()}"

    # 添加用户名
    name = get_username()
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
