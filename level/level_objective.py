import random
class LevelObjective:
    def __init__(self):
        self.objectives = {}

    # ================= GENERATE =================
    def generate(self, fruit_max):
        self.objectives = {
            name: {
                "required": random.randint(1, max_count),
                "collected": 0,
                "max": max_count
            }
            for name, max_count in fruit_max.items()
        }

    # ================= UPDATE =================
    def add(self, name, amount=1):
        obj = self.objectives.get(name)
        if not obj:
            return

        obj["collected"] = min(
            obj["collected"] + amount,
            obj["required"]
        )

    # ================= CHECK =================
    def is_completed(self):
        return all(
            obj["collected"] >= obj["required"]
            for obj in self.objectives.values()
        )

    # ================= UI HELPERS =================
    def get_data(self):
        return self.objectives

    def reset(self):
        for obj in self.objectives.values():
            obj["collected"] = 0
