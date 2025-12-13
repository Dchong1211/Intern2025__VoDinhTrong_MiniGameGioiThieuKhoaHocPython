from items.item import Item


class ItemManager:
    def __init__(self):
        self.items = []

        # inventory toàn game (KHÔNG RESET)
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

    # gọi mỗi khi load level
    def clear_level_items(self):
        self.items.clear()

    def add(self, x, y, name):
        self.items.append(Item(x, y, name))

    def update(self, player):
        for item in self.items[:]:
            item.update()

            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()

                if item.name in self.count:
                    self.count[item.name] += 1

            if item.dead:
                self.items.remove(item)

    def draw(self, surf):
        for item in self.items:
            item.draw(surf)
