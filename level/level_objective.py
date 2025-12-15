import random


class LevelObjective:
    def __init__(self):
        # fruit_name -> {required, collected, max}
        self.objectives = {}

    # ======================================
    def generate(self, fruit_max_dict):
        """
        fruit_max_dict = {
            "Apple": 5,
            "Bananas": 3,
            ...
        }
        """
        self.objectives.clear()

        for name, max_count in fruit_max_dict.items():
            required = random.randint(1, max_count)

            self.objectives[name] = {
                "required": required,
                "collected": 0,
                "max": max_count
            }

    # ======================================
    def add(self, fruit_name, amount=1):
        if fruit_name in self.objectives:
            self.objectives[fruit_name]["collected"] += amount

    # ======================================
    def is_completed(self):
        for data in self.objectives.values():
            if data["collected"] < data["required"]:
                return False
        return True
