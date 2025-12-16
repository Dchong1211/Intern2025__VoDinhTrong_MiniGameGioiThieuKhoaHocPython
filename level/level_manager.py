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
from .level_objective import LevelObjective


class LevelManager:
    def __init__(self, save):
        self.save = save
        self.completed_level_id = None

        # ===== LEVEL LIST =====
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

        # ===== RUNTIME OBJECTS =====
        self.player = None
        self.checkpoint = None
        self.collisions = []
        self.one_way_platforms = []

        # ===== INVENTORY (GLOBAL) =====
        self.item_manager = ItemManager()
        self.item_manager.import_data(
            self.save.get_fruits()
        )

        # ===== OBJECTIVE (PER LEVEL) =====
        self.objective = LevelObjective()

        # ===== BACKGROUND RANDOM =====
        self.bg_folder = "assets/Background/Level"
        self.bg_files = [
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ]
        self.bg = None
        self.last_bg = None

        # ===== STATE =====
        self.state = LevelState.PLAYING
        self.fade_alpha = 0
        self.fade_speed = 300

        self.level_completed = False

        self.load_level(self.current_level)

    # ======================================================
    def load_level(self, level_id):
        self.current_level = level_id
        self.level_completed = False

        self.tmx = load_pygame(self.levels[level_id])

        self.tw = self.tmx.tilewidth
        self.th = self.tmx.tileheight

        self.map_w = self.tmx.width * self.tw
        self.map_h = self.tmx.height * self.th

        # ===== RESET =====
        self.player = None
        self.checkpoint = None
        self.collisions.clear()
        self.one_way_platforms.clear()

        self.item_manager.clear_level_items()

        # ===== RANDOM BACKGROUND =====
        random.seed(self.current_level)  # 🔒 khóa theo level
        bg_name = random.choice(self.bg_files)
        random.seed()  # mở lại random toàn cục


        self.last_bg = bg_name
        bg_path = os.path.join(self.bg_folder, bg_name)

        self.bg = ScrollingBackground(
            bg_path,
            self.map_w,
            self.map_h,
            speed=40
        )

        # ===== MAP SURFACE =====
        self.map_surface = pygame.Surface(
            (self.map_w, self.map_h),
            pygame.SRCALPHA
        )

        self._render_map()
        self._load_objects()

        # ===== CHECKPOINT STATE THEO SAVE =====
        if (
            self.checkpoint
            and self.save.is_level_unlocked(self.current_level + 1)
        ):
            self.checkpoint.force_active()

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
        fruit_max = {}

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

            elif obj.name == "OneWay":
                self.one_way_platforms.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )

            elif obj.type == "Items":
                self.item_manager.add(obj.x, obj.y, obj.name)
                fruit_max[obj.name] = fruit_max.get(obj.name, 0) + 1

        self.objective.generate(fruit_max)

    # ======================================================
    def update(self, dt, keys):

        # ===== BACKGROUND =====
        if self.bg:
            self.bg.update(dt)

        # ===== PLAYER + ITEM UPDATE =====
        if self.state in (
            LevelState.PLAYING,
            LevelState.CHECKPOINT_ANIM,
            LevelState.FADING_OUT,
            LevelState.FADING_IN
        ):
            self.player.update(
                dt,
                keys,
                self.collisions,
                self.one_way_platforms
            )

            self.item_manager.update(
                self.player,
                self.save,
                self.objective
            )

        # =============== PLAYING =================
        if self.state == LevelState.PLAYING:
            if (
                self.checkpoint
                and self.player.rect.colliderect(self.checkpoint.rect)
            ):
                if not self.objective.is_completed():
                    return

                self.checkpoint.activate()
                self.state = LevelState.CHECKPOINT_ANIM

        # =============== CHECKPOINT =================
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
            self.completed_level_id = self.current_level
            self.level_completed = True

            next_level = self.current_level + 1

            if next_level in self.levels:
                self.save.unlock_level(next_level)
                self.load_level(next_level)
                self.state = LevelState.FADING_IN
            else:
                print("🎉 GAME COMPLETE")
                self.state = LevelState.PLAYING

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
