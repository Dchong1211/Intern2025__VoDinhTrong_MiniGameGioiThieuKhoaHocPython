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
from gameplay.code_runner import CodeRunner

# ===== ENEMY =====
from enemy.enemy_manager import EnemyManager

class LevelManager:
    def __init__(self, save):
        self.save = save

        # ================= REQUEST FLAGS =================
        self.request_go_home = False
        self.request_go_level_select = False

        # ================= QUEST UI =================
        self.quest_panel = None

        # ================= LEVEL LIST (AUTO LOAD) =================
        self.levels = {}
        self.level_dir = "assets/levels" 
        
        # Quét level tự động từ 1 -> N
        lvl_id = 1
        while True:
            filename = f"level{lvl_id}.tmx"
            path = os.path.join(self.level_dir, filename)
            if os.path.exists(path):
                self.levels[lvl_id] = path
                print(f"[LevelManager] Loaded path for: {filename}")
                lvl_id += 1
            else:
                break
        
        self.current_level = 1

        # ================= MAP =================
        self.tmx = None
        self.map_surface = None
        self.tw = self.th = 0
        self.map_w = self.map_h = 0

        # ================= OBJECTS =================
        self.player = None
        self.code_runner = None
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
        self.bg_files = []
        if os.path.exists(self.bg_folder):
            self.bg_files = [
                f for f in os.listdir(self.bg_folder)
                if f.endswith(".png")
            ]
        self.bg = None

        # ================= STATE =================
        self.state = LevelState.PLAYING
        self.fade_alpha = 0
        self.fade_speed = 300

        # Khởi tạo level đầu tiên
        if self.levels:
            self.load_level(self.current_level)

    # ==================================================
    # ================= PUBLIC API =====================
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
            self.state = LevelState.CHECKPOINT_ANIM

    def on_quest_failed(self):
        if self.is_level_completed(self.current_level):
            return
        self.item_manager.punish_random_type(0.1)
        self.save.save_fruits(self.item_manager.export_data())
    
    def run_code(self, lines):
        if not self.player or not self.code_runner:
            return
        self.code_runner.load(lines)

    # ==================================================
    # ================= LOAD LEVEL =====================
    # ==================================================

    def load_level(self, level_id):
        if level_id not in self.levels:
            print(f"[ERROR] Level {level_id} not found!")
            return

        print(f"--- LOADING LEVEL {level_id} ---")
        self.current_level = level_id
        self.state = LevelState.PLAYING
        self.fade_alpha = 0

        self.request_go_home = False
        self.request_go_level_select = False

        # Reset dữ liệu cũ
        self.collisions.clear()
        self.one_way_platforms.clear()
        self.item_manager.clear_level_items() # Xóa item của màn trước
        self.enemy_manager.enemies.clear()

        # Load file TMX
        self.tmx = load_pygame(self.levels[level_id])

        self.tw = self.tmx.tilewidth
        self.th = self.tmx.tileheight
        self.map_w = self.tmx.width * self.tw
        self.map_h = self.tmx.height * self.th

        self._load_background(level_id)
        self._build_map_surface()
        
        # Load Objects (QUAN TRỌNG)
        self._load_objects()

        if not self.player:
            self.player = Player(
                32, 32,
                self.save.get_selected_character()
            )

        self.code_runner = CodeRunner(self.player)

        if self.checkpoint and self.is_level_completed(level_id):
            self.checkpoint.force_active()


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
        # Biến đếm số lượng trái cây có trong map
        fruit_max = {}
        
        # Danh sách tên các loại quả (Phải khớp chính xác với Tiled)
        valid_fruits = [
            "Apple", "Bananas", "Cherries", "Kiwi", 
            "Melon", "Orange", "Pineapple", "Strawberry"
        ]

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
                    obj.x, obj.y, obj.name,
                    obj.properties, tile_size
                )

            # === FIX LOGIC ITEMS (QUAN TRỌNG) ===
            # Ưu tiên kiểm tra theo TÊN (Name) trước, vì Type có thể bị cache lỗi
            elif obj.name in valid_fruits:
                self.item_manager.add(obj.x, obj.y, obj.name)
                # Cộng dồn số lượng
                fruit_max[obj.name] = fruit_max.get(obj.name, 0) + 1

            # Dự phòng: Kiểm tra theo TYPE (nếu lỡ đặt sai tên nhưng đúng Type)
            elif getattr(obj, "type", "") == "Items":
                self.item_manager.add(obj.x, obj.y, obj.name)
                # Chỉ tính vào nhiệm vụ nếu tên hợp lệ
                if obj.name in valid_fruits:
                    fruit_max[obj.name] = fruit_max.get(obj.name, 0) + 1

        # Gửi dữ liệu đếm được vào Objective để tạo nhiệm vụ
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
            self.fade_alpha = min(
                255,
                self.fade_alpha + self.fade_speed * dt
            )
            if self.fade_alpha >= 255:
                self.state = LevelState.LOADING

        elif self.state == LevelState.LOADING:
            self._load_next_level()

        elif self.state == LevelState.FADING_IN:
            self.fade_alpha = max(
                0,
                self.fade_alpha - self.fade_speed * dt
            )
            if self.fade_alpha <= 0:
                self.state = LevelState.PLAYING
    def _update_playing(self, dt, keys):
            if self.code_runner:
                self.code_runner.update()

            keyboard_locked = (keys is None) or (self.player and self.player.code_active)

            if self.player:
                self.player.update(
                    dt,
                    None if keyboard_locked else keys,
                    self.collisions,
                    self.one_way_platforms
                )

            self.enemy_manager.update(self.player)
            self.item_manager.update(self.player, save_manager=self.save, objective=self.objective)

            if not self.checkpoint:
                return

            # Cập nhật trạng thái Ready cho checkpoint nếu đã gom đủ quả
            # (Dòng này giúp checkpoint biết là nó đã sẵn sàng bay cờ)
            is_completed = self.objective.is_completed()
            self.checkpoint.ready = (True if self.checkpoint.active else is_completed)

            # Kiểm tra va chạm giữa Player và Checkpoint
            inside = self.player.rect.colliderect(self.checkpoint.rect)

            if inside and not self.checkpoint.player_inside:
                
                # === PHẦN SỬA LOGIC QUAN TRỌNG TẠI ĐÂY ===
                
                # TRƯỜNG HỢP 1: Đã gom đủ trái cây -> CHIẾN THẮNG
                if is_completed:
                    self.checkpoint.activate()      # Kích hoạt animation cờ bay
                    self.state = LevelState.CHECKPOINT_ANIM # Chuyển state để chặn điều khiển và chờ animation
                    
                    # Tự động đóng bảng nhiệm vụ nếu đang mở cho đỡ vướng
                    if self.quest_panel: 
                        self.quest_panel.close()

                # TRƯỜNG HỢP 2: Chưa đủ trái cây -> Hiện bảng nhắc nhở
                elif not self.checkpoint.active:
                    if self.quest_panel:
                        self.checkpoint.on_player_touch(self.quest_panel)
                
                # ==========================================

            self.checkpoint.player_inside = inside

    def _load_next_level(self):
        next_level = self.current_level + 1
        if next_level in self.levels:
            self.save.unlock_level(next_level)
            self.load_level(next_level)
            self.state = LevelState.FADING_IN
        else:
            print("All levels completed!")
            self.state = LevelState.PLAYING
            self.go_level_select()

    # ==================================================
    # ================= DRAW ===========================
    # ==================================================

    def draw(self, surf):
        if self.bg:
            self.bg.draw(surf)

        if self.map_surface:
            surf.blit(self.map_surface, (0, 0))

        self.enemy_manager.draw(surf)
        self.item_manager.draw(surf)

        if self.checkpoint:
            self.checkpoint.draw(surf)

        if self.player:
            self.player.draw(surf)

        if self.fade_alpha > 0:
            fade = pygame.Surface((self.map_w, self.map_h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(self.fade_alpha))
            surf.blit(fade, (0, 0))

    def get_camera_offset(self, screen_w, screen_h):
        if not self.player:
            return 0, 0

        target_x = self.player.rect.centerx
        target_y = self.player.rect.centery
        cam_x = screen_w // 2 - target_x
        cam_y = screen_h // 2 - target_y
        cam_x = min(0, max(cam_x, -(self.map_w - screen_w)))
        cam_y = min(0, max(cam_y, -(self.map_h - screen_h)))

        return cam_x, cam_y