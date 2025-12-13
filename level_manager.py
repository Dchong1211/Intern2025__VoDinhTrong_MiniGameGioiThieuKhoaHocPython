import pygame
from pytmx.util_pygame import load_pygame
from pytmx import TiledTileLayer

from player.player import Player


class LevelManager:
    def __init__(self):
        self.levels = {
            1: "assets/levels/level1.tmx",
            2: "assets/levels/level2.tmx",
            3: "assets/levels/level3.tmx",
        }

        self.current_level = 1

        self.tmx = None
        self.map_surface = None

        self.tw = 0
        self.th = 0
        self.map_w = 0
        self.map_h = 0

        # runtime objects
        self.player = None
        self.goal = None
        self.collisions = []

        self.load_level(self.current_level)

    # ======================================================
    def load_level(self, level_id):
        print(f"> Load level {level_id}")

        self.current_level = level_id
        self.tmx = load_pygame(self.levels[level_id])

        self.tw = self.tmx.tilewidth
        self.th = self.tmx.tileheight

        self.map_w = self.tmx.width * self.tw
        self.map_h = self.tmx.height * self.th

        # reset
        self.player = None
        self.goal = None
        self.collisions = []

        # render surface
        self.map_surface = pygame.Surface(
            (self.map_w, self.map_h),
            pygame.SRCALPHA
        )

        self._render_map()
        self._load_objects()

        # fallback nếu quên đặt Player
        if self.player is None:
            self.player = Player(32, 32)

    # ======================================================
    # RENDER TILE MAP (chỉ tile layer)
    # ======================================================
    def _render_map(self):
        for layer in self.tmx.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        self.map_surface.blit(
                            image,
                            (x * self.tw, y * self.th)
                        )

    # ======================================================
    # LOAD OBJECTS (ALL-IN-ONE)
    # ======================================================
    def _load_objects(self):
        for obj in self.tmx.objects:

            # -------- PLAYER --------
            if obj.name == "Player":
                self.player = Player(obj.x, obj.y)

            # -------- GOAL --------
            elif obj.name == "Goal":
                self.goal = pygame.Rect(
                    obj.x, obj.y, obj.width, obj.height
                )

            # -------- COLLISION (RECT) --------
            elif obj.name == "Collision":
                self.collisions.append(
                    pygame.Rect(
                        obj.x, obj.y, obj.width, obj.height
                    )
                )

            # -------- ENEMY (sau này) --------
            elif obj.name == "Enemy":
                print("Enemy spawn:", obj.x, obj.y)

            # -------- ITEM / SKILL --------
            elif obj.name == "Item":
                print("Item spawn:", obj.x, obj.y)

    # ======================================================
    def update(self, dt, keys):
        self.player.update(dt, keys, self.collisions)

        # chạm goal → next level
        if self.goal and self.player.rect.colliderect(self.goal):
            next_level = self.current_level + 1
            if next_level in self.levels:
                self.load_level(next_level)
            else:
                print("🎉 GAME COMPLETE")

    # ======================================================
    def draw(self, surf):
        surf.blit(self.map_surface, (0, 0))

        # debug collision (nếu cần)
        # for r in self.collisions:
        #     pygame.draw.rect(surf, (255, 0, 0), r, 1)

        self.player.draw(surf)
