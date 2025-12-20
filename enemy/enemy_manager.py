from enemy.enemy import Enemy

class EnemyManager:
    def __init__(self):
        self.enemies = []

    def add(self, x, y, name, props, tile_size):
        enemy = Enemy(x, y, name, props, tile_size)
        self.enemies.append(enemy)

    def update(self, player):
        for e in self.enemies[:]:
            e.update(player)
            if not e.alive:
                self.enemies.remove(e)

    def draw(self, surf):
        for e in self.enemies:
            e.draw(surf)
