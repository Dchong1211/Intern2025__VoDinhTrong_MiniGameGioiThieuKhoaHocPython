import json


class QuestManager:
    def __init__(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            self.quest = json.load(f)

    # ================= QUESTION =================
    def text(self):
        return self.quest.get("question", "")

    # ================= CHOICES =================
    def choices(self):
        return self.quest.get("choices", {})

    # ================= ANSWER =================
    def answer(self):
        return self.quest.get("answer", "A")

    # ================= KEY QUEST =================
    def is_key(self):
        return self.quest.get("key", False)

    # ================= UNLOCK SKILL =================
    def unlock_skill(self):
        return self.quest.get("unlock_skill")
