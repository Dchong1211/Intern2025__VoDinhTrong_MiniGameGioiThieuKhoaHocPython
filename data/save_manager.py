import json
import os


class SaveManager:
    def __init__(self):
        self.path = "data/save.json"
        self.data = {
            "fruits": {},
            "levels": {
                "unlocked": [1]
            }
        }

        self.load()

    # ======================================
    def load(self):
        if not os.path.exists(self.path):
            self.save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if not content:
                    raise ValueError("Empty save file")

                self.data = json.loads(content)

        except (json.JSONDecodeError, ValueError):
            print("⚠️ Save file corrupted or empty → reset save")

            self.data = {
                "fruits": {},
                "levels": {
                    "unlocked": [1]
                }
            }
            self.save()

        # đảm bảo không thiếu key
        self.data.setdefault("fruits", {})
        self.data.setdefault("levels", {})
        self.data["levels"].setdefault("unlocked", [1])

    # ======================================
    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    # ======================================
    # ========== FRUITS ==========
    def save_fruits(self, fruits_data):
        self.data["fruits"] = fruits_data
        self.save()

    def get_fruits(self):
        return self.data.get("fruits", {})

    # ======================================
    # ========== LEVELS ==========
    def unlock_level(self, level_id):
        unlocked = self.data["levels"]["unlocked"]

        if level_id not in unlocked:
            unlocked.append(level_id)
            unlocked.sort()

        self.save()

    def is_level_unlocked(self, level_id):
        return level_id in self.data["levels"]["unlocked"]
