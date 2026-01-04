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

        # ================= CODE PHASE =================
        self.code_lines = [
            "move_right(3)",
            "jump()"
        ]
        self.code_queue = []
        self.code_timer = 0
        self.code_delay = 0.35
        self.code_running = False

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

        # reset code phase
        self.code_queue.clear()
        self.code_timer = 0
        self.code_running = False

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

    def update_code_phase(self, dt):
        if self.bg:
            self.bg.update(dt)

        if not self.code_running:
            self._parse_code()
            self.code_running = True

        self.code_timer += dt
        if self.code_timer >= self.code_delay and self.code_queue:
            cmd = self.code_queue.pop(0)
            self._execute_command(cmd)
            self.code_timer = 0

        if not self.code_queue and self.code_running:
            self.code_running = False
            # chuyển sang phase chơi tay
            from ui.game_state import GameState
            import pygame
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {"next_state": GameState.LEVEL_PLAY}
                )
            )

    def _parse_code(self):
        self.code_queue.clear()
        for line in self.code_lines:
            line = line.strip()

            if line.startswith("move_right"):
                steps = int(line[line.find("(")+1:line.find(")")])
                self.code_queue.append(("MOVE", steps))

            elif line.startswith("move_left"):
                steps = int(line[line.find("(")+1:line.find(")")])
                self.code_queue.append(("MOVE", -steps))

            elif line == "jump()":
                self.code_queue.append(("JUMP", 1))

    def _execute_command(self, cmd):
        if cmd[0] == "MOVE":
            self.player.rect.x += cmd[1] * self.tw
        elif cmd[0] == "JUMP":
            self.player.velocity_y = -self.player.jump_force

    def draw_code_ui(self, screen):
        panel = pygame.Rect(
            screen.get_width() - 360,
            0,
            360,
            screen.get_height()
        )

        pygame.draw.rect(screen, (25, 25, 35), panel)

        font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 18
        )

        y = 20
        for line in self.code_lines:
            text = font.render(line, True, (200, 200, 220))
            screen.blit(text, (panel.x + 20, y))
            y += 28

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
