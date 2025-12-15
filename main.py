import pygame
import sys

from level.level_manager import LevelManager
from ui.hud import HUD
from ui.main_menu import MainMenu
from ui.game_state import GameState
from ui.level_select import LevelSelect
from data.save_manager import SaveManager

pygame.init()

# ================= WINDOW =================
pygame.display.set_caption("Code Fruit")
BASE_W, BASE_H = 1280, 720
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)

icon = pygame.image.load("assets/Background/Logo.png").convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60
fullscreen = False

# ================= SAVE =================
save = SaveManager()

# ================= STATE =================
state = GameState.MENU

menu = MainMenu()
level_select = LevelSelect(save)
level_manager = LevelManager(save)

# ===== LOAD FRUIT TỪ SAVE =====
level_manager.item_manager.import_data(
    save.get_fruits()
)

# ================= WORLD =================
WORLD_W = level_manager.map_w
WORLD_H = level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

hud = HUD(level_manager.item_manager)


# ==================================================
def draw_scaled_world():
    sw, sh = screen.get_size()
    scale = sh / WORLD_H

    draw_w = int(WORLD_W * scale)
    scaled = pygame.transform.scale(world, (draw_w, sh))
    x = (sw - draw_w) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled, (x, 0))


# ================= MAIN LOOP =================
running = True
while running:
    dt = clock.tick(FPS) / 1000

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode(
                    (0, 0), pygame.FULLSCREEN
                ) if fullscreen else pygame.display.set_mode(
                    (BASE_W, BASE_H), pygame.RESIZABLE
                )

    # ================= MENU =================
    if state == GameState.MENU:
        result = menu.update(screen)
        if result == "PLAY":
            state = GameState.LEVEL_SELECT

    # ================= LEVEL SELECT =================
    elif state == GameState.LEVEL_SELECT:
        level = level_select.update(screen)
        if level:
            level_manager.load_level(level)
            state = GameState.PLAYING

    # ================= PLAYING =================
    elif state == GameState.PLAYING:
        keys = pygame.key.get_pressed()

        level_manager.update(dt, keys)

        # ===== CHỐT FRUIT + SAVE KHI QUA LEVEL =====
        if level_manager.level_completed:
            # chốt fruit của level vừa qua
            level_manager.item_manager.commit_level_items()

            # lưu fruit đã chốt
            save.set_fruits(
                level_manager.item_manager.export_data()
            )

            # lưu level đã hoàn thành
            completed_level = level_manager.current_level - 1
            save.complete_level(completed_level)

            level_manager.level_completed = False

        world.fill((20, 20, 25))
        level_manager.draw(world)

        draw_scaled_world()
        hud.draw(screen)


    pygame.display.flip()

pygame.quit()
sys.exit()
