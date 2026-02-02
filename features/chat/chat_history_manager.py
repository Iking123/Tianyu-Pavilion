import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from funcs import sanitize_windows_filename


class ChatHistoryManager:
    def __init__(self, storage_dir="chat_histories"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_chat(
        self,
        conversation_history: List[Dict],
        messages: List[Dict],
        chat_id: Optional[str] = None,
    ) -> str:
        """保存聊天记录到文件"""
        # if chat_id is None:
        #     chat_id = str(uuid.uuid4())

        # 生成对话标题（使用第一条用户消息的前20个字符）
        title = "新对话"
        for msg in conversation_history:
            if msg["role"] == "user":
                content = msg["content"]
                title = content[:20] + "..." if len(content) > 20 else content
                break

        timestamp = datetime.now().isoformat()

        if chat_id is None:
            chat_id = sanitize_windows_filename(f"{timestamp} {title}")

        # 创建聊天记录数据
        chat_data = {
            "id": chat_id,
            "title": title,
            "timestamp": timestamp,
            "conversation_history": conversation_history,
            "messages": messages,
        }

        # 保存到文件
        file_path = os.path.join(self.storage_dir, f"{chat_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)

        return chat_id

    def load_chat(self, chat_id: str) -> Dict:
        """从文件加载聊天记录"""
        file_path = os.path.join(self.storage_dir, f"{chat_id}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_chats(self) -> List[Dict]:
        """获取所有聊天记录的基本信息"""
        chats = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        chat_data = json.load(f)
                        # 只返回基本信息，不包含完整的对话历史
                        chats.append(
                            {
                                "id": chat_data["id"],
                                "title": chat_data["title"],
                                "timestamp": chat_data["timestamp"],
                            }
                        )
                except Exception as e:
                    print(f"Error loading chat {filename}: {e}")

        # 按时间倒序排列
        chats.sort(key=lambda x: x["timestamp"], reverse=True)
        return chats

    def delete_chat(self, chat_id: str) -> bool:
        """删除聊天记录"""
        file_path = os.path.join(self.storage_dir, f"{chat_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def update_chat_title(self, chat_id: str, new_title: str) -> bool:
        filename = f"{chat_id}.json"
        file_path = os.path.join(self.storage_dir, filename)
        if os.path.exists(file_path):
            chat_data = {}
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chat_data = json.load(f)
                    chat_data["title"] = new_title
            except Exception as e:
                print(f"Error loading chat {filename}: {e}")
                return False
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            return True
        return False

    def get_title_by_id(self, chat_id: str) -> str:
        filename = f"{chat_id}.json"
        file_path = os.path.join(self.storage_dir, filename)
        if os.path.exists(file_path):
            chat_data = {}
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chat_data = json.load(f)
                    return chat_data["title"]
            except Exception as e:
                print(f"Error loading chat {filename}: {e}")
                return ""
        return ""
