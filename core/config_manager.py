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
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "tavily_api_key": "",
    "username": "",
    "enable_r1": False,
    "enable_tavily": False,
    "enable_baidu": True,
    "speed_slider": 8,
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


def get_assist():
    """获取现在的助手名"""
    return "assistant" if get_config("enable_r1") else "assistant-v3"


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
    if p == 1:
        prompt = f"你是一个智能助手，在一个个人平台上与用户交流。{SYSTEM_PROMPT[p][get_config('enable_baidu')][get_config('enable_tavily')]}\n当前时间：{time.asctime()}"
        name = get_username()
        return f"{prompt}\n用户名：{name}" if name else prompt
    return ""


def update_config(new_config):
    """更新配置（加密存储）"""
    global _config
    _config = new_config

    # 加密并保存新配置
    encrypted_data = _encrypt_config(new_config)
    with open(CONFIG_ENC_PATH, "wb") as f:
        f.write(encrypted_data)
