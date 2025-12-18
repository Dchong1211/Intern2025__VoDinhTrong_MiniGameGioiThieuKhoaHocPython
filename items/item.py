import os
import pygame
from player.animation import Animation


class Item:
    SIZE = 32
    BASE_PATH = "assets/Items/Fruits"

    def __init__(self, x, y, name):
        self.name = name

        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)

        idle_img = self._load_image(f"{name}.png")
        collect_img = self._load_image("Collected.png")

        self.anim_idle = Animation(idle_img, self.SIZE, self.SIZE, 0.3)
        self.anim_collect = Animation(
            collect_img,
            self.SIZE,
            self.SIZE,
            0.2,
            loop=False
        )

        self.current_anim = self.anim_idle
        self.collected = False
        self.dead = False

    # ================= CORE =================
    def _load_image(self, filename):
        return pygame.image.load(
            os.path.join(self.BASE_PATH, filename)
        ).convert_alpha()

    def collect(self):
        if self.collected:
            return

        self.collected = True
        self.current_anim = self.anim_collect
        self.current_anim.index = 0

    def update(self):
        self.current_anim.update()

        if self.collected and self.current_anim.finished:
            self.dead = True

    def draw(self, surf):
        surf.blit(
            self.current_anim.get_image(),
            self.rect
        )
