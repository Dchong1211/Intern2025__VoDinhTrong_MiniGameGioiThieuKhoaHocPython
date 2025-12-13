import pygame
import os
from player.animation import Animation


class Item:
    def __init__(self, x, y, name):
        self.name = name
        self.rect = pygame.Rect(x, y, 32, 32)

        base = "assets/Items/Fruits"

        def load(img):
            return pygame.image.load(os.path.join(base, img)).convert_alpha()

        self.anim_idle = Animation(load(f"{name}.png"), 32, 32, 0.3)
        self.anim_collect = Animation(load("Collected.png"), 32, 32, 0.2, loop=False)

        self.current_anim = self.anim_idle
        self.collected = False
        self.dead = False

    def collect(self):
        self.collected = True
        self.current_anim = self.anim_collect
        self.current_anim.reset()

    def update(self):
        self.current_anim.update()

        if self.collected:
            if self.current_anim.index >= len(self.current_anim.frames) - 1:
                self.dead = True

    def draw(self, surf):
        surf.blit(self.current_anim.get_image(), self.rect.topleft)
