import pygame
import sys

from level.level_manager import LevelManager
from ui.hud import HUD
from ui.main_menu import MainMenu
from ui.game_state import GameState
from ui.level_select import LevelSelect
from data.save_manager import SaveManager
from ui.square_transition import SquareTransition

pygame.init()

# ================= WINDOW =================
pygame.display.set_caption("Code Fruit")
BASE_W, BASE_H = 1280, 720
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)

icon = pygame.image.load("assets/Background/Menu/Logo.png").convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60
fullscreen = False

# ================= SAVE =================
save = SaveManager()

# ================= STATE =================
state = GameState.MENU
next_state = None
next_level = None

menu = MainMenu()
level_select = LevelSelect(save)
level_manager = LevelManager(save)

# ================= WORLD =================
WORLD_W = level_manager.map_w
WORLD_H = level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

hud = HUD(
    level_manager.item_manager,
    level_manager.objective
)

# ================= TRANSITION =================
transition = SquareTransition(screen.get_size())

# ==================================================
def draw_scaled_world():
    sw, sh = screen.get_size()
    scale = sh / WORLD_H

    draw_w = int(WORLD_W * scale)
    scaled = pygame.transform.scale(world, (draw_w, sh))
    x = (sw - draw_w) // 2

    screen.fill((0, 0, 0))          # clear full screen
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
            screen = pygame.display.set_mode(
                event.size, pygame.RESIZABLE
            )
            transition.resize(event.size)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode(
                    (0, 0), pygame.FULLSCREEN
                ) if fullscreen else pygame.display.set_mode(
                    (BASE_W, BASE_H), pygame.RESIZABLE
                )
                transition.resize(screen.get_size())

            elif event.key == pygame.K_j:
                hud.show_objectives = not hud.show_objectives

    # ================= MENU =================
    if state == GameState.MENU:
        screen.fill((0, 0, 0))
        result = menu.update(screen)

        if result == "PLAY" and transition.phase == "idle":
            next_state = GameState.LEVEL_SELECT
            transition.start_close()

    # ================= LEVEL SELECT =================
    elif state == GameState.LEVEL_SELECT:
        screen.fill((0, 0, 0))
        result = level_select.update(screen)

        if result == "BACK" and transition.phase == "idle":
            next_state = GameState.MENU
            transition.start_close()

        elif isinstance(result, int) and transition.phase == "idle":
            next_state = GameState.PLAYING
            next_level = result
            transition.start_close()

    # ================= PLAYING =================
    elif state == GameState.PLAYING:
        keys = pygame.key.get_pressed()

        level_manager.update(dt, keys)

        world.fill((20, 20, 25))
        level_manager.draw(world)

        draw_scaled_world()
        hud.draw(screen)

    # ================= TRANSITION =================
    transition.update(dt)

    # ----- ĐÓNG KÍN → ĐỔI STATE → MỞ -----
    if transition.is_closed() and next_state is not None:
        state = next_state

        if state == GameState.PLAYING and next_level is not None:
            level_manager.load_level(next_level)
            hud = HUD(
                level_manager.item_manager,
                level_manager.objective
            )
            next_level = None

        next_state = None
        transition.start_open()

    transition.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
