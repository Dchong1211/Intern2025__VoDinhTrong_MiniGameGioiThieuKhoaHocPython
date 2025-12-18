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
            },
            "characters": {
                "owned": ["Virtual Guy"],
                "selected": "Virtual Guy"
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

        # đảm bảo key gốc tồn tại
        for key, value in default.items():
            self.data.setdefault(key, value)

        # levels
        self.data.setdefault("levels", {})
        self.data["levels"].setdefault("unlocked", [1])

        # characters (🔥 QUAN TRỌNG)
        self.data.setdefault("characters", {})
        self.data["characters"].setdefault(
            "owned", ["Virtual Guy"]
        )
        self.data["characters"].setdefault(
            "selected", "Virtual Guy"
        )

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

    # ================= CHARACTERS =================
    def get_owned_characters(self):
        return self.data["characters"]["owned"]

    def get_selected_character(self):
        return self.data["characters"]["selected"]

    def save_characters(self, owned, selected):
        self.data["characters"]["owned"] = owned
        self.data["characters"]["selected"] = selected
        self.save()
