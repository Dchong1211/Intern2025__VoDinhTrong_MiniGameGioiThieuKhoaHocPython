import json
import os


class SaveManager:
    def __init__(self, path="data/save.json"):
        self.path = path
        self.data = self._default_data()
        self._ensure_dir()
        self.load()

    # ================= CORE =================
    def _default_data(self):
        return {
            "fruits": {},
            "levels": {
                "unlocked": [1]
            }
        }

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self):
        if not os.path.exists(self.path):
            self.save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.data = self._default_data()
            self.save()

        self._normalize()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def _normalize(self):
        default = self._default_data()

        for key, value in default.items():
            self.data.setdefault(key, value)

        self.data["levels"].setdefault("unlocked", [1])

    # ================= FRUITS =================
    def save_fruits(self, fruits):
        self.data["fruits"] = fruits
        self.save()

    def get_fruits(self):
        return self.data["fruits"]

    # ================= LEVELS =================
    def unlock_level(self, level_id):
        unlocked = self.data["levels"]["unlocked"]

        if level_id not in unlocked:
            unlocked.append(level_id)
            unlocked.sort()
            self.save()

    def is_level_unlocked(self, level_id):
        return level_id in self.data["levels"]["unlocked"]
