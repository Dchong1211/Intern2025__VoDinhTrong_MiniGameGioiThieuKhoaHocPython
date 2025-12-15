import pygame
import os

class ScrollingBackground:
    def __init__(self, image_path, map_w, map_h, speed=30):
        self.image = pygame.image.load(image_path).convert()
        self.tile_w = self.image.get_width()
        self.tile_h = self.image.get_height()

        self.map_w = map_w
        self.map_h = map_h

        self.speed = speed
        self.offset_y = 0

    def update(self, dt):
        self.offset_y += self.speed * dt

        # loop khi vượt chiều cao tile
        if self.offset_y >= self.tile_h:
            self.offset_y -= self.tile_h

    def draw(self, surf):
        # lặp tile phủ kín map
        for y in range(
            -self.tile_h,
            self.map_h + self.tile_h,
            self.tile_h
        ):
            for x in range(
                0,
                self.map_w,
                self.tile_w
            ):
                surf.blit(
                    self.image,
                    (x, y + int(self.offset_y))
                )
