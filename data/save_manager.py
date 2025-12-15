import json
import os


class SaveManager:
    def __init__(self, path="data/save.json"):
        self.path = path

        # ===== DEFAULT DATA =====
        self.default_data = {
            "unlocked_level": 1,
            "completed_levels": [],
            "fruits": {
                "Apple": 0,
                "Bananas": 0,
                "Cherries": 0,
                "Kiwi": 0,
                "Melon": 0,
                "Orange": 0,
                "Pineapple": 0,
                "Strawberry": 0,
            }
        }

        self.data = {}
        self.load()

    # ==================================================
    def load(self):
        # Nếu chưa có file → tạo mới
        if not os.path.exists(self.path):
            self.data = self.default_data.copy()
            self.save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()

                # File rỗng
                if not content:
                    self.data = self.default_data.copy()
                    self.save()
                    return

                self.data = json.loads(content)

        except (json.JSONDecodeError, IOError):
            self.data = self.default_data.copy()
            self.save()
            return

        # ===== MIGRATE SAVE CŨ =====
        self._migrate()

    # ==================================================
    def _migrate(self):
        changed = False

        # unlocked_level
        if "unlocked_level" not in self.data:
            self.data["unlocked_level"] = self.default_data["unlocked_level"]
            changed = True

        # completed_levels
        if "completed_levels" not in self.data:
            self.data["completed_levels"] = []
            changed = True

        # fruits (QUAN TRỌNG NHẤT)
        if "fruits" not in self.data:
            self.data["fruits"] = self.default_data["fruits"].copy()
            changed = True
        else:
            # Bổ sung trái cây mới nếu có
            for k in self.default_data["fruits"]:
                if k not in self.data["fruits"]:
                    self.data["fruits"][k] = 0
                    changed = True

        if changed:
            self.save()

    # ==================================================
    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    # ==================================================
    # ===== LEVEL API =====
    def complete_level(self, level):
        if level not in self.data["completed_levels"]:
            self.data["completed_levels"].append(level)

        if level + 1 > self.data["unlocked_level"]:
            self.data["unlocked_level"] = level + 1

        self.save()

    def is_level_unlocked(self, level):
        return level <= self.data["unlocked_level"]

    # ==================================================
    # ===== FRUIT API =====
    def get_fruits(self):
        return self.data["fruits"]

    def set_fruits(self, fruits_dict):
        self.data["fruits"] = fruits_dict.copy()
        self.save()
