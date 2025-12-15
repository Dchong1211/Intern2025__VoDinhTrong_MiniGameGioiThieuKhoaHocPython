from items.item import Item


class ItemManager:
    def __init__(self):
        self.items = []

        # ===== SỐ LƯỢNG TRÁI =====
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

        # ===== TRÁI ĐÃ PHÁT HIỆN CHƯA =====
        self.discovered = {k: False for k in self.count}

    # ======================================
    def clear_level_items(self):
        self.items.clear()

    # ======================================
    def add(self, x, y, name):
        self.items.append(Item(x, y, name))

    # ======================================
    def update(self, player, save_manager=None, objective=None):
        for item in self.items[:]:
            item.update()

            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()

                if item.name in self.count:
                    self.count[item.name] += 1
                    self.discovered[item.name] = True

                    # 🔥 báo đúng loại fruit cho objective
                    if objective:
                        objective.add(item.name, 1)

                    if save_manager:
                        save_manager.save_fruits(self.export_data())

            if item.dead:
                self.items.remove(item)


    # ======================================
    def draw(self, surf):
        for item in self.items:
            item.draw(surf)

    # ======================================
    def export_data(self):
        return {
            "count": self.count,
            "discovered": self.discovered
        }

    # ======================================
    def import_data(self, data):
        if not data:
            return

        for k in self.count:
            if "count" in data and k in data["count"]:
                self.count[k] = data["count"][k]

            if "discovered" in data and k in data["discovered"]:
                self.discovered[k] = data["discovered"][k]
