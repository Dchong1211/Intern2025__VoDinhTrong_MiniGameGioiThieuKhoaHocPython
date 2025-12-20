import pygame
from enemies.enemy_factory import create_enemy


class EnemyManager:
    def __init__(self):
        self.enemies = pygame.sprite.Group()

    # ===============================
    def spawn(self, name, x, y):
        enemy = create_enemy(name, x, y)
        self.enemies.add(enemy)

    # ===============================
    def update(self, player, tiles):
        for enemy in self.enemies:
            enemy.update(player, tiles)

    # ===============================
    def draw(self, screen):
        self.enemies.draw(screen)

    # ===============================
    def clear(self):
        self.enemies.empty()
