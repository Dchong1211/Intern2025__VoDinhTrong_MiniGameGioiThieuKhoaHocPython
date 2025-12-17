# gameplay/quest_manager.py
import json

class QuestManager:
    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.quest = json.load(f)

    def get_text(self):
        return self.quest["text"]

    def get_choices(self):
        return self.quest["choices"]  # dict A B C D

    def get_answer(self):
        return self.quest["answer"]

    def is_key(self):
        return self.quest["key_quest"]

    def unlock_skill(self):
        return self.quest["unlock_skill"]
