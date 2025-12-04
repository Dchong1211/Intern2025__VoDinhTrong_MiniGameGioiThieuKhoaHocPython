# items/item_manager.py
class ItemManager:
    def __init__(self, items):
        self.items = items

    def update(self, player):
        for item in self.items:
            item.update()

            # Check pickup
            if (not item.collected) and player.rect.colliderect(item.rect):
                item.on_pick(player)

        # remove item đã hoàn tất animation
        self.items = [i for i in self.items if not i.remove]

    def draw(self, surf, cam_x, cam_y):
        for item in self.items:
            item.draw(surf, cam_x, cam_y)
