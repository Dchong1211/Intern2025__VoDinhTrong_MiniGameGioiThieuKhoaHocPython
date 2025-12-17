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

        # ===== FLAGS CHO MAIN =====
        self.request_go_home = False
        self.request_go_level_select = False

        # ===== QUEST UI =====
        self.quest_panel = None

        # ===== LEVEL LIST =====
        self.levels = {
            1: "assets/levels/level1.tmx",
            2: "assets/levels/level2.tmx",
            3: "assets/levels/level3.tmx",
        }

        self.current_level = 1

        # ===== MAP =====
        self.tmx = None
        self.map_surface = None
        self.tw = 0
        self.th = 0
        self.map_w = 0
        self.map_h = 0

        # ===== OBJECTS =====
        self.player = None
        self.checkpoint = None
        self.collisions = []
        self.one_way_platforms = []

        # ===== INVENTORY (GLOBAL – LOAD 1 LẦN) =====
        self.item_manager = ItemManager()
        if not hasattr(save, "_fruit_loaded"):
            self.item_manager.import_data(save.get_fruits())
            save._fruit_loaded = True

        # ===== OBJECTIVE (PER LEVEL) =====
        self.objective = LevelObjective()

        # ===== BACKGROUND =====
        self.bg_folder = "assets/Background/Level"
        self.bg_files = [
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ]
        self.bg = None

        # ===== STATE =====
        self.state = LevelState.PLAYING
        self.fade_alpha = 0
        self.fade_speed = 300

        self.load_level(self.current_level)

    # ======================================================
    def is_level_completed(self, level_id):
        """Level đã hoàn thành nếu level tiếp theo đã unlock"""
        return self.save.is_level_unlocked(level_id + 1)

    # ======================================================
    def load_level(self, level_id):
        self.current_level = level_id
        self.state = LevelState.PLAYING
        self.fade_alpha = 0
        self.request_go_home = False
        self.request_go_level_select = False

        self.tmx = load_pygame(self.levels[level_id])

        self.tw = self.tmx.tilewidth
        self.th = self.tmx.tileheight
        self.map_w = self.tmx.width * self.tw
        self.map_h = self.tmx.height * self.th

        # ===== RESET OBJECTS =====
        self.player = None
        self.checkpoint = None
        self.collisions.clear()
        self.one_way_platforms.clear()

        # ❗ reset item spawn (KHÔNG reset count)
        self.item_manager.clear_level_items()

        # ===== BACKGROUND =====
        random.seed(level_id)
        bg_name = random.choice(self.bg_files)
        random.seed()

        self.bg = ScrollingBackground(
            os.path.join(self.bg_folder, bg_name),
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

        # ✅ AUTO ACTIVE CHECKPOINT NẾU LEVEL ĐÃ QUA
        if self.checkpoint and self.is_level_completed(level_id):
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
    # ================= QUEST CALLBACK =====================
    # ======================================================
    def on_quest_success(self):
        self.save.save_fruits(self.item_manager.export_data())
        if self.checkpoint:
            self.checkpoint.activate()

    def on_quest_failed(self):
        # ❌ nếu replay level đã qua → KHÔNG PHẠT
        if self.is_level_completed(self.current_level):
            return

        # ❌ phạt 10% random 1 loại
        self.item_manager.punish_random_type_percent(0.1)
        self.save.save_fruits(self.item_manager.export_data())

    def go_home(self):
        self.request_go_home = True

    def go_level_select(self):
        self.request_go_level_select = True

    def restart_level(self):
        self.load_level(self.current_level)

    # ======================================================
    # ================= UPDATE =============================
    # ======================================================
    def update(self, dt, keys):

        if self.bg:
            self.bg.update(dt)
        # ===== UPDATE CHECKPOINT LUÔN LUÔN =====
        if self.checkpoint:
            self.checkpoint.update(dt)

        # ===== LOCK PLAYER KHI QUEST =====
        if self.quest_panel and self.quest_panel.visible:
            return


        # ===== PLAYER =====
        if self.state == LevelState.PLAYING:
            self.player.update(
                dt, keys,
                self.collisions,
                self.one_way_platforms
            )

            self.item_manager.update(
                self.player,
                objective=self.objective
            )

        # ================= PLAYING =================
        if self.state == LevelState.PLAYING and self.checkpoint:

            # 🔥 FIX QUAN TRỌNG: KHÔNG CHO objective ghi đè active
            if self.checkpoint.active:
                self.checkpoint.ready = True
            else:
                self.checkpoint.ready = self.objective.is_completed()

            if self.player.rect.colliderect(self.checkpoint.rect):

                if not self.checkpoint.ready:
                    return

                # ===== CHƯA ACTIVE =====
                if not self.checkpoint.active:

                    # ✅ replay → bỏ quest
                    if self.is_level_completed(self.current_level):
                        self.checkpoint.activate()
                        self.state = LevelState.CHECKPOINT_ANIM
                        return

                    # ❗ lần đầu → mở quest
                    if self.quest_panel:
                        self.checkpoint.on_player_touch(self.quest_panel)
                    return

                self.state = LevelState.CHECKPOINT_ANIM

        # ================= CHECKPOINT ANIM =================
        elif self.state == LevelState.CHECKPOINT_ANIM:
            self.checkpoint.update(dt)
            if self.checkpoint.animation_finished():
                self.state = LevelState.FADING_OUT

        # ================= FADE OUT =================
        elif self.state == LevelState.FADING_OUT:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.state = LevelState.LOADING

        # ================= LOAD NEXT =================
        elif self.state == LevelState.LOADING:
            next_level = self.current_level + 1
            if next_level in self.levels:
                self.save.unlock_level(next_level)
                self.load_level(next_level)
                self.state = LevelState.FADING_IN
            else:
                self.state = LevelState.PLAYING

        # ================= FADE IN =================
        elif self.state == LevelState.FADING_IN:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.state = LevelState.PLAYING

    # ======================================================
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
