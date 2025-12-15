from items.item import Item


class ItemManager:
    def __init__(self):
        self.items = []

        # ===== INVENTORY TOÀN GAME (ĐÃ CHỐT) =====
        self.count = {
            "Apple": 0,
            "Bananas": 0,
            "Cherries": 0,
            "Kiwi": 0,
            "Melon": 0,
            "Orange": 0,
            "Pineapple": 0,
            "Strawberry": 0,
        }

        # ===== FRUIT NHẶT TRONG LEVEL HIỆN TẠI =====
        self.level_collected = {k: 0 for k in self.count}

    # ==================================================
    def clear_level_items(self):
        self.items.clear()
        self.level_collected = {k: 0 for k in self.count}

    # ==================================================
    def add(self, x, y, name):
        self.items.append(Item(x, y, name))

    # ==================================================
    def update(self, player):
        for item in self.items[:]:
            item.update()

            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()
                if item.name in self.level_collected:
                    self.level_collected[item.name] += 1

            if item.dead:
                self.items.remove(item)

    # ==================================================
    def draw(self, surf):
        for item in self.items:
            item.draw(surf)

    # ==================================================
    def commit_level_items(self):
        """Chốt fruit khi qua level"""
        for k in self.count:
            self.count[k] += self.level_collected[k]

        self.level_collected = {k: 0 for k in self.count}

    # ==================================================
    def export_data(self):
        return self.count.copy()

    def import_data(self, data):
        for k in self.count:
            if k in data:
                self.count[k] = data[k]
