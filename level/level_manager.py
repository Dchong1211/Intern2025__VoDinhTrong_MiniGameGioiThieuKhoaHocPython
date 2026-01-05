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

from enemy.enemy_manager import EnemyManager


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

        # ================= ENEMY =================
        self.enemy_manager = EnemyManager()

        # ================= INVENTORY =================
        self.item_manager = ItemManager()
        if not getattr(save, "_fruit_loaded", False):
            self.item_manager.import_data(save.get_fruits())
            save._fruit_loaded = True

        # ================= OBJECTIVE =================
        self.objective = LevelObjective()

        # ================= BACKGROUND =================
        self.bg_folder = "assets/Background/Level"
        self.bg_files = [
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ]
        self.bg = None

        # ================= INTERNAL STATE =================
        self.fade_alpha = 0
        self.fade_speed = 300

        self.load_level(self.current_level)

    # ==================================================
    # ================= LEVEL CONTROL ==================
    # ==================================================

    def restart_level(self):
        self.load_level(self.current_level)

    def go_home(self):
        self.request_go_home = True

    def go_level_select(self):
        self.request_go_level_select = True

    def is_level_completed(self, level_id):
        return self.save.is_level_unlocked(level_id + 1)

    # ==================================================
    # ================= QUEST CALLBACK =================
    # ==================================================

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
        self.fade_alpha = 0

        self.request_go_home = False
        self.request_go_level_select = False

        self.collisions.clear()
        self.one_way_platforms.clear()
        self.item_manager.clear_level_items()
        self.enemy_manager.enemies.clear()

        self.tmx = load_pygame(self.levels[level_id])

        self.tw = self.tmx.tilewidth
        self.th = self.tmx.tileheight
        self.map_w = self.tmx.width * self.tw
        self.map_h = self.tmx.height * self.th

        self._load_background(level_id)
        self._build_map_surface()
        self._load_objects()

        if not self.player:
            self.player = Player(
                32, 32,
                self.save.get_selected_character()
            )

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
        tile_size = self.tmx.tilewidth
        character = self.save.get_selected_character()

        for obj in self.tmx.objects:
            if obj.name == "Player":
                self.player = Player(obj.x, obj.y, character)

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

            elif obj.type == "Enemy":
                self.enemy_manager.add(
                    obj.x,
                    obj.y,
                    obj.name,
                    obj.properties,
                    tile_size
                )

            elif obj.type == "Items":
                self.item_manager.add(obj.x, obj.y, obj.name)
                fruit_max[obj.name] = fruit_max.get(obj.name, 0) + 1

        self.objective.generate(fruit_max)

    # ==================================================
    # ================= PHASE: CODE ====================
    # ==================================================
    def run_code(self, code_lines: list[str]):
        """
        Nhận code từ CodePanel và chuyển cho Player
        """
        if not self.player:
            return

        # 🔒 BẮT ĐẦU CODE PHASE Ở PLAYER
        self.player.start_code_phase(code_lines)


    # ==================================================
    # ================= PHASE: PLAY ====================
    # ==================================================

    def update_play_phase(self, dt, keys):
        if self.bg:
            self.bg.update(dt)

        if self.checkpoint:
            self.checkpoint.update(dt)

        if self.quest_panel and self.quest_panel.visible:
            return

        self.player.update(
            dt, keys,
            self.collisions,
            self.one_way_platforms
        )

        self.enemy_manager.update(self.player)

        self.item_manager.update(
            self.player,
            objective=self.objective
        )

    # ==================================================
    # ================= DRAW WORLD =====================
    # ==================================================

    def draw(self, surf):
        if self.bg:
            self.bg.draw(surf)

        surf.blit(self.map_surface, (0, 0))
        self.enemy_manager.draw(surf)
        self.item_manager.draw(surf)

        if self.checkpoint:
            self.checkpoint.draw(surf)

        self.player.draw(surf)

        if self.fade_alpha > 0:
            fade = pygame.Surface((self.map_w, self.map_h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(self.fade_alpha))
            surf.blit(fade, (0, 0))
