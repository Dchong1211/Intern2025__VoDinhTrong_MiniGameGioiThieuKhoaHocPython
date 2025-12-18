import os
import random
import pygame

from pytmx.util_pygame import load_pygame
from pytmx import TiledTileLayer

from player.player import Player
from items.item_manager import ItemManager
from level.checkpoint import Checkpoint
from level.level_state import LevelState
from level.scrolling_background import ScrollingBackground
from level.level_objective import LevelObjective


class LevelManager:
    def __init__(self, save):
        self.save = save

        # ================= REQUEST FLAGS =================
        self.request_go_home = False
        self.request_go_level_select = False

        # ================= QUEST UI =================
        self.quest_panel = None

        # ================= LEVEL LIST =================
        self.levels = {
            1: "assets/levels/level1.tmx",
            2: "assets/levels/level2.tmx",
            3: "assets/levels/level3.tmx",
        }

        self.current_level = 1

        # ================= MAP =================
        self.tmx = None
        self.map_surface = None
        self.tw = self.th = 0
        self.map_w = self.map_h = 0

        # ================= OBJECTS =================
        self.player = None
        self.checkpoint = None
        self.collisions = []
        self.one_way_platforms = []

        # ================= INVENTORY (GLOBAL) =================
        self.item_manager = ItemManager()
        if not getattr(save, "_fruit_loaded", False):
            self.item_manager.import_data(save.get_fruits())
            save._fruit_loaded = True

        # ================= OBJECTIVE (PER LEVEL) =================
        self.objective = LevelObjective()

        # ================= BACKGROUND =================
        self.bg_folder = "assets/Background/Level"
        self.bg_files = [
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ]
        self.bg = None

        # ================= STATE =================
        self.state = LevelState.PLAYING
        self.fade_alpha = 0
        self.fade_speed = 300

        self.load_level(self.current_level)

    # ==================================================
    # ================= PUBLIC API (BẮT BUỘC) ==========
    # ==================================================

    def restart_level(self):
        self.load_level(self.current_level)

    def go_home(self):
        self.request_go_home = True

    def go_level_select(self):
        self.request_go_level_select = True

    def is_level_completed(self, level_id):
        return self.save.is_level_unlocked(level_id + 1)

    def on_quest_success(self):
        self.save.save_fruits(self.item_manager.export_data())
        if self.checkpoint:
            self.checkpoint.activate()

    def on_quest_failed(self):
        if self.is_level_completed(self.current_level):
            return
        self.item_manager.punish_random_type(0.1)
        self.save.save_fruits(self.item_manager.export_data())

    # ==================================================
    # ================= LOAD LEVEL =====================
    # ==================================================

    def load_level(self, level_id):
        self.current_level = level_id
        self.state = LevelState.PLAYING
        self.fade_alpha = 0

        self.request_go_home = False
        self.request_go_level_select = False

        self.collisions.clear()
        self.one_way_platforms.clear()
        self.item_manager.clear_level_items()

        self.tmx = load_pygame(self.levels[level_id])

        self.tw = self.tmx.tilewidth
        self.th = self.tmx.tileheight
        self.map_w = self.tmx.width * self.tw
        self.map_h = self.tmx.height * self.th

        self._load_background(level_id)
        self._build_map_surface()
        self._load_objects()

        if self.checkpoint and self.is_level_completed(level_id):
            self.checkpoint.force_active()

        if not self.player:
            self.player = Player(32, 32)

    # ==================================================
    # ================= LOAD HELPERS ===================
    # ==================================================

    def _load_background(self, seed):
        if not self.bg_files:
            self.bg = None
            return

        random.seed(seed)
        bg = random.choice(self.bg_files)
        random.seed()

        self.bg = ScrollingBackground(
            os.path.join(self.bg_folder, bg),
            self.map_w,
            self.map_h,
            speed=40
        )

    def _build_map_surface(self):
        self.map_surface = pygame.Surface(
            (self.map_w, self.map_h),
            pygame.SRCALPHA
        )

        for layer in self.tmx.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        self.map_surface.blit(
                            image,
                            (x * self.tw, y * self.th)
                        )

    def _load_objects(self):
        fruit_max = {}

        self.player = None
        self.checkpoint = None

        for obj in self.tmx.objects:
            if obj.name == "Player":
                self.player = Player(obj.x, obj.y)

            elif obj.name == "Checkpoint":
                self.checkpoint = Checkpoint(obj.x, obj.y)

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

    # ==================================================
    # ================= UPDATE =========================
    # ==================================================

    def update(self, dt, keys):
        if self.bg:
            self.bg.update(dt)

        if self.checkpoint:
            self.checkpoint.update(dt)

        if self.quest_panel and self.quest_panel.visible:
            return

        if self.state == LevelState.PLAYING:
            self._update_playing(dt, keys)

        elif self.state == LevelState.CHECKPOINT_ANIM:
            if self.checkpoint.animation_finished():
                self.state = LevelState.FADING_OUT

        elif self.state == LevelState.FADING_OUT:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt)
            if self.fade_alpha >= 255:
                self.state = LevelState.LOADING

        elif self.state == LevelState.LOADING:
            self._load_next_level()

        elif self.state == LevelState.FADING_IN:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed * dt)
            if self.fade_alpha <= 0:
                self.state = LevelState.PLAYING

    def _update_playing(self, dt, keys):
        self.player.update(
            dt, keys,
            self.collisions,
            self.one_way_platforms
        )

        self.item_manager.update(
            self.player,
            objective=self.objective
        )

        if not self.checkpoint:
            return

        self.checkpoint.ready = (
            True if self.checkpoint.active
            else self.objective.is_completed()
        )

        inside = self.player.rect.colliderect(self.checkpoint.rect)

        # 🔥 Player vừa bước VÀO checkpoint
        if inside and not self.checkpoint.player_inside:
            if not self.checkpoint.active:
                if self.is_level_completed(self.current_level):
                    self.checkpoint.activate()
                    self.state = LevelState.CHECKPOINT_ANIM
                elif self.quest_panel:
                    self.checkpoint.on_player_touch(self.quest_panel)
            else:
                self.state = LevelState.CHECKPOINT_ANIM

        # cập nhật trạng thái cho frame sau
        self.checkpoint.player_inside = inside

    def _load_next_level(self):
        next_level = self.current_level + 1
        if next_level in self.levels:
            self.save.unlock_level(next_level)
            self.load_level(next_level)
            self.state = LevelState.FADING_IN
        else:
            self.state = LevelState.PLAYING

    # ==================================================
    # ================= DRAW ===========================
    # ==================================================

    def draw(self, surf):
        if self.bg:
            self.bg.draw(surf)

        surf.blit(self.map_surface, (0, 0))
        self.item_manager.draw(surf)

        if self.checkpoint:
            self.checkpoint.draw(surf)

        self.player.draw(surf)

        if self.fade_alpha > 0:
            fade = pygame.Surface((self.map_w, self.map_h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(self.fade_alpha))
            surf.blit(fade, (0, 0))
