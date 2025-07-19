import json
import os
import uuid
from .config_manager import _encrypt_config, _decrypt_config, _get_key
from .hardcode import HARDCODED_FICTIONS

# 小说信息加密文件路径
FICTIONS_ENC_PATH = "fictions.enc"


def _load_fictions():
    """加载所有小说信息（硬编码+用户自定义）"""
    all_fictions = HARDCODED_FICTIONS.copy()

    # 加载用户自定义小说信息
    if os.path.exists(FICTIONS_ENC_PATH):
        with open(FICTIONS_ENC_PATH, "rb") as f:
            encrypted_data = f.read()
            decrypted_data = _decrypt_config(encrypted_data)
            user_fictions = json.loads(decrypted_data)
            all_fictions.extend(user_fictions)

    return all_fictions


def _save_fictions(fictions_list):
    """保存用户自定义小说信息（排除硬编码小说）"""
    user_fictions = [fic for fic in fictions_list if not fic.get("is_hardcoded", False)]
    encrypted_data = _encrypt_config(json.dumps(user_fictions))
    with open(FICTIONS_ENC_PATH, "wb") as f:
        f.write(encrypted_data)


def get_all_fictions():
    """获取所有小说信息"""
    return _load_fictions()


def get_fiction_by_id(char_id):
    """根据ID获取小说信息"""
    fictions = _load_fictions()
    for fic in fictions:
        if fic["id"] == char_id:
            return fic
    return None


def save_fiction(fiction_data):
    """保存或更新小说信息"""
    fictions = _load_fictions()

    # 更新现有小说信息或添加新小说信息
    existing_index = next(
        (i for i, fic in enumerate(fictions) if fic["id"] == fiction_data.get("id")),
        -1,
    )

    if existing_index >= 0:
        # 确保不能修改硬编码小说信息
        if fictions[existing_index].get("is_hardcoded", False):
            return False
        fictions[existing_index] = fiction_data
    else:
        # 为新小说信息生成唯一ID
        if "id" not in fiction_data:
            fiction_data["id"] = str(uuid.uuid4())
        fictions.append(fiction_data)

    _save_fictions(fictions)
    return True


def delete_fiction(char_id):
    """删除小说信息（不能删除硬编码小说信息）"""
    fictions = _load_fictions()
    new_fictions = []
    deleted = False

    for fic in fictions:
        if fic["id"] == char_id:
            if fic.get("is_hardcoded", False):
                return False  # 不能删除硬编码小说信息
            deleted = True
        else:
            new_fictions.append(fic)

    if deleted:
        _save_fictions(new_fictions)

    return deleted


def format_fiction(id):
    """
    用于构建系统提示\n
    需要注意：在编辑页面中，给用户看的相应的名称有所不同！\n
    存储的键名：plot-task-plot_attention\n
    系统提示中的对应名称：基础情节-小说主题-关键情节\n
    用户编辑界面显示的名称：情节描述-小说规则-注意事项
    """
    fic = get_fiction_by_id(id)
    if not fic:
        return ""
    return f"""# 情节规则
### 小说主题
```
{fic.get("task","")}
```

### 基础情节
```
{fic.get("plot","")}
```

### 关键情节
```
{fic.get("plot_attention","")}
```
"""
