import pygame
import os
import random

from pytmx.util_pygame import load_pygame
from pytmx import TiledTileLayer

from player.player import Player
from items.item_manager import ItemManager
from .checkpoint import Checkpoint
from .level_state import LevelState
from .scrolling_background import ScrollingBackground


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
        self.checkpoint = None
        self.collisions = []

        # inventory global (không reset)
        self.item_manager = ItemManager()

        # ===== BACKGROUND RANDOM =====
        self.bg_folder = "assets/Background"
        self.bg_files = [
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ]
        self.bg = None
        self.last_bg = None

        # STATE
        self.state = LevelState.PLAYING
        self.fade_alpha = 0
        self.fade_speed = 300  # alpha / giây

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

        # reset runtime
        self.player = None
        self.checkpoint = None
        self.collisions = []

        self.item_manager.clear_level_items()

        # ===== RANDOM BACKGROUND (KHÔNG TRÙNG LIÊN TIẾP) =====
        bg_name = random.choice(self.bg_files)
        while bg_name == self.last_bg and len(self.bg_files) > 1:
            bg_name = random.choice(self.bg_files)

        self.last_bg = bg_name
        bg_path = os.path.join(self.bg_folder, bg_name)

        self.bg = ScrollingBackground(
            bg_path,
            self.map_w,
            self.map_h,
            speed=40
        )

        print(f"🎨 Background: {bg_name}")

        # ===== MAP SURFACE =====
        self.map_surface = pygame.Surface(
            (self.map_w, self.map_h),
            pygame.SRCALPHA
        )

        self._render_map()
        self._load_objects()

        if self.player is None:
            self.player = Player(32, 32)

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
    def _load_objects(self):
        for obj in self.tmx.objects:

            if obj.name == "Player":
                self.player = Player(obj.x, obj.y)

            elif obj.name == "Checkpoint":
                self.checkpoint = Checkpoint(
                    obj.x, obj.y, obj.width, obj.height
                )

            elif obj.name == "Collision":
                self.collisions.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )

            elif obj.type == "Items":
                self.item_manager.add(obj.x, obj.y, obj.name)

    # ======================================================
    def update(self, dt, keys):

        # ===== BACKGROUND UPDATE =====
        if self.bg:
            self.bg.update(dt)

        # ===== PLAYER LUÔN UPDATE =====
        if self.state in (
            LevelState.PLAYING,
            LevelState.CHECKPOINT_ANIM,
            LevelState.FADING_OUT,
            LevelState.FADING_IN
        ):
            self.player.update(dt, keys, self.collisions)
            self.item_manager.update(self.player)

        # =============== PLAYING =================
        if self.state == LevelState.PLAYING:
            if (
                self.checkpoint
                and self.player.rect.colliderect(self.checkpoint.rect)
            ):
                self.checkpoint.activate()
                self.state = LevelState.CHECKPOINT_ANIM

        # =============== CHECKPOINT ANIMATION =================
        elif self.state == LevelState.CHECKPOINT_ANIM:
            self.checkpoint.update(dt)
            if self.checkpoint.animation_finished():
                self.state = LevelState.FADING_OUT

        # =============== FADE OUT =================
        elif self.state == LevelState.FADING_OUT:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.state = LevelState.LOADING

        # =============== LOAD NEXT LEVEL =================
        elif self.state == LevelState.LOADING:
            next_level = self.current_level + 1
            if next_level in self.levels:
                self.load_level(next_level)
                self.state = LevelState.FADING_IN
            else:
                print("🎉 GAME COMPLETE")

        # =============== FADE IN =================
        elif self.state == LevelState.FADING_IN:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.state = LevelState.PLAYING

    # ======================================================
    def draw(self, surf):

        # ===== BACKGROUND =====
        if self.bg:
            self.bg.draw(surf)

        # ===== MAP =====
        surf.blit(self.map_surface, (0, 0))

        # ===== OBJECTS =====
        self.item_manager.draw(surf)

        if self.checkpoint:
            self.checkpoint.draw(surf)

        self.player.draw(surf)

        # ===== FADE =====
        if self.fade_alpha > 0:
            fade = pygame.Surface((self.map_w, self.map_h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(self.fade_alpha))
            surf.blit(fade, (0, 0))
