import json
import random


class QuestManager:
    def __init__(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Mỗi level chỉ có 1 quest
        self.quest = data

        self.used = False

    # =========================
    # CÂU HỎI
    def text(self):
        return self.quest.get("question", "")

    # =========================
    # ĐÁP ÁN (A, B, C, D)
    def choices(self):
        """
        Trả về dict:
        {
            "A": "...",
            "B": "...",
            "C": "...",
            "D": "..."
        }
        """
        return self.quest.get("choices", {})

    # =========================
    # ĐÁP ÁN ĐÚNG
    def answer(self):
        return self.quest.get("answer", "A")

    # =========================
    # QUEST CÓ PHẢI CHỦ CHỐT KHÔNG
    def is_key(self):
        return self.quest.get("key", False)

    # =========================
    # KỸ NĂNG MỞ KHÓA
    def unlock_skill(self):
        return self.quest.get("unlock_skill", None)
