import random
from items.item import Item


class ItemManager:
    FRUIT_TYPES = (
        "Apple",
        "Bananas",
        "Cherries",
        "Kiwi",
        "Melon",
        "Orange",
        "Pineapple",
        "Strawberry",
    )

    def __init__(self):
        self.items: list[Item] = []

        self.count = {name: 0 for name in self.FRUIT_TYPES}
        self.discovered = {name: False for name in self.FRUIT_TYPES}

    # ================= LEVEL =================
    def clear_level_items(self):
        self.items.clear()

    def add(self, x, y, name):
        if name in self.count:
            self.items.append(Item(x, y, name))

    # ================= UPDATE =================
    def update(self, player, save_manager=None, objective=None):
        for item in self.items:
            item.update()

            if not item.collected and player.rect.colliderect(item.rect):
                self._collect(item, save_manager, objective)

        self.items = [item for item in self.items if not item.dead]

    def _collect(self, item, save_manager, objective):
        item.collect()

        self.count[item.name] += 1
        self.discovered[item.name] = True

        if objective:
            objective.add(item.name, 1)

        if save_manager:
            save_manager.save_fruits(self.export_data())

    # ================= DRAW =================
    def draw(self, surf):
        for item in self.items:
            item.draw(surf)

    # ================= SAVE DATA =================
    def export_data(self):
        return {
            "count": self.count.copy(),
            "discovered": self.discovered.copy()
        }

    def import_data(self, data):
        if not data:
            return

        for name in self.count:
            self.count[name] = data.get("count", {}).get(name, 0)
            self.discovered[name] = data.get("discovered", {}).get(name, False)

    # ================= PENALTY =================
    def punish_random_type(self, percent=0.1):
        available = [k for k, v in self.count.items() if v > 0]
        if not available:
            return

        fruit = random.choice(available)
        lost = max(1, int(self.count[fruit] * percent))

        self.count[fruit] = max(0, self.count[fruit] - lost)
