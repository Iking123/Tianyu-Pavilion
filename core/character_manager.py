import json
import os
import threading
import uuid
import re
from .config_manager import _encrypt_config, _decrypt_config, get_username
from funcs import replace_newline_with_space, resource_path

if os.path.exists(resource_path("core/hardcode_characters.py")):
    from .hardcode_characters import HARDCODED_CHARACTERS
else:
    HARDCODED_CHARACTERS = []

# 角色信息加密文件路径
CHARACTERS_ENC_PATH = "data/characters.enc"

# 角色数据缓存（模块级变量，初始时_cached_characters为None）
_cache_lock = threading.Lock()  # 缓存锁
_cached_characters = None  # 缓存合并后的所有角色（硬编码+用户自定义）


def _load_characters() -> list[dict]:
    """加载所有角色（硬编码+用户自定义），并缓存结果"""
    global _cached_characters  # 声明修改模块级变量
    with _cache_lock:
        # 1. 若缓存存在，直接返回副本（避免外部修改影响缓存）
        if _cached_characters is not None:
            return _cached_characters.copy()  # 返回副本，防止外部篡改缓存

        # 2. 缓存未命中，执行原加载逻辑
        all_characters = HARDCODED_CHARACTERS.copy()  # 复制硬编码角色（避免修改原列表）

        # 加载用户自定义角色（原逻辑不变）
        if os.path.exists(CHARACTERS_ENC_PATH):
            with open(CHARACTERS_ENC_PATH, "rb") as f:
                encrypted_data = f.read()
                decrypted_data = _decrypt_config(encrypted_data)
                user_characters = json.loads(decrypted_data)
                all_characters.extend(user_characters)

        # 3. 更新缓存（存储合并后的角色列表）
        _cached_characters = all_characters

        # 4. 返回副本（避免外部修改缓存）
        return all_characters.copy()


def _save_characters(characters_list):
    """保存用户自定义角色（排除硬编码角色）"""
    user_characters = [
        char for char in characters_list if not char.get("is_hardcoded", False)
    ]
    encrypted_data = _encrypt_config(json.dumps(user_characters))
    with open(CHARACTERS_ENC_PATH, "wb") as f:
        f.write(encrypted_data)


def get_all_characters(force=False):
    """获取所有角色（若用户名不为特别用户，隐去隐藏角色）"""
    characters = _load_characters()
    if not force and not (get_username(False) in ["Iking", "雨落流绮"]):
        characters = [
            c
            for c in characters
            if not (
                c.get("is_hardcoded", False) and c.get("id", "").startswith("hidden_")
            )
        ]
    return characters


def get_character_by_id(char_id):
    """根据ID获取角色"""
    characters = _load_characters()
    for char in characters:
        if char["id"] == char_id:
            return char
    return None


def get_character_name(char_id):
    """根据ID获取角色名"""
    char = get_character_by_id(char_id)
    return char.get("name", "") if char else None


def find_character_id(ids, name):
    """在ID列表中找角色名为name的角色（需满足这个ID列表中角色名两两不同），若没找到则返回name"""
    return next((id for id in ids if get_character_name(id) == name), name)


def save_character(character_data):
    """保存或更新角色"""
    characters = _load_characters()

    # 更新现有角色或添加新角色
    existing_index = next(
        (
            i
            for i, char in enumerate(characters)
            if char["id"] == character_data.get("id")
        ),
        -1,
    )

    if existing_index >= 0:
        # 确保不能修改硬编码角色
        if characters[existing_index].get("is_hardcoded", False):
            return False

        # 更新角色数据时保留已有的summary字段（如果新数据中没有）
        if "summary" in characters[existing_index] and "summary" not in character_data:
            character_data["summary"] = characters[existing_index]["summary"]

        characters[existing_index] = character_data
    else:
        # 为新角色生成唯一ID
        if "id" not in character_data:
            character_data["id"] = str(uuid.uuid4())
        characters.append(character_data)

    # 保存用户自定义角色
    _save_characters(characters)

    # 清空缓存（数据已修改，下次需重新加载）
    global _cached_characters
    with _cache_lock:
        _cached_characters = None

    return True


def delete_character(char_id):
    """删除角色（不能删除硬编码角色）"""
    characters = _load_characters()
    new_characters = []
    deleted = False

    # 过滤要删除的角色
    for char in characters:
        if char["id"] == char_id:
            if char.get("is_hardcoded", False):
                return False  # 不能删除硬编码角色
            deleted = True
        else:
            new_characters.append(char)

    # 保存修改后的角色列表
    if deleted:
        _save_characters(new_characters)

        # 清空缓存（数据已修改，下次需重新加载）
        global _cached_characters
        with _cache_lock:
            _cached_characters = None

    return deleted


def chara_get(char: dict, key: str):
    s = str(char.get(key))
    if not s:
        return " "  # 如果为空，留个空
    return replace_newline_with_space(s)


def format_character(id, prefix="", summary=False, sp=False):
    char = get_character_by_id(id)
    if not char:
        return ""
    if summary:
        s = char.get("summary", "")
        if not s:
            from core.jieba_summarizer import summarizer

            s = summarizer.summarize(format_character(id, prefix))
        return f"""### {prefix+":" if prefix else ""}{char.get("name")}
```
{s}
```
"""

    info = f"""### {prefix}基础信息
|名称|性别|年龄或生年|身份|性格|兴趣|
|-|-|-|-|-|-|
|`{char.get("name")}`|`{chara_get(char,"gender")}`|`{chara_get(char,"age")}`|`{chara_get(char,"identity")}`|`{chara_get(char,"personality")}`|`{chara_get(char,"hobbies")}`|

### {prefix}背景设定
```
{char.get("background")}
```
"""

    if appearance := char.get("appearance"):
        info += f"""
### {prefix}外貌设定
```
{appearance}
```
"""

    if sp and (sp_ps := char.get("sp_ps")):
        info += f"""
### {prefix}补充说明
{sp_ps}
"""

    return info


def format_character_basic(id, prefix=""):
    char = get_character_by_id(id)
    if not char:
        return ""
    return f"""### {prefix+":" if prefix else ""}{char.get("name")}
|名称|性别|年龄或生年|身份|性格|兴趣|
|-|-|-|-|-|-|
|`{char.get("name")}`|`{chara_get(char,"gender")}`|`{chara_get(char,"age")}`|`{chara_get(char,"identity")}`|`{chara_get(char,"personality")}`|`{chara_get(char,"hobbies")}`|
"""
