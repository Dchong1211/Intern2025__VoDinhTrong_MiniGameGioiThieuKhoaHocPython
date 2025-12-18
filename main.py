import sys
import pygame

from data.save_manager import SaveManager
from level.level_manager import LevelManager
from level.quest_manager import QuestManager

from ui.game_state import GameState
from ui.main_menu import MainMenu
from ui.level_select import LevelSelect
from ui.hud import HUD
from ui.quest_panel import QuestPanel
from ui.square_transition import SquareTransition

pygame.init()

# ================= WINDOW =================
BASE_W, BASE_H = 1280, 720
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
pygame.display.set_caption("Code Fruit")

icon = pygame.image.load("assets/Background/Menu/Logo.png").convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60

fullscreen = False
windowed_size = (BASE_W, BASE_H)   # 👈 LƯU SIZE TRƯỚC KHI FULLSCREEN

# ================= SAVE =================
save = SaveManager()

# ================= STATE =================
state = GameState.MENU
next_state = None
next_level = None

# ================= UI =================
menu = MainMenu()
level_select = LevelSelect(save)

# ================= LEVEL =================
level_manager = LevelManager(save)

# ================= WORLD =================
WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

hud = HUD(
    level_manager.item_manager,
    level_manager.objective
)

quest_panel = None

# ================= TRANSITION =================
transition = SquareTransition(screen.get_size())


# ================= DRAW WORLD =================
def draw_scaled_world():
    sw, sh = screen.get_size()
    scale = min(sw / WORLD_W, sh / WORLD_H)

    draw_w = int(WORLD_W * scale)
    draw_h = int(WORLD_H * scale)

    scaled = pygame.transform.scale(world, (draw_w, draw_h))
    x = (sw - draw_w) // 2
    y = (sh - draw_h) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled, (x, y))


# ================= MAIN LOOP =================
running = True
while running:
    dt = clock.tick(FPS) / 1000

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== WINDOW RESIZE =====
        elif event.type == pygame.VIDEORESIZE:
            if not fullscreen:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                transition.resize(event.size)
                level_select.on_resize(screen)


        # ===== KEY INPUT =====
        elif event.type == pygame.KEYDOWN:

            # ===== TOGGLE FULLSCREEN =====
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen

                if fullscreen:
                    # lưu size trước khi vào fullscreen
                    windowed_size = screen.get_size()
                    screen = pygame.display.set_mode(
                        (0, 0),
                        pygame.FULLSCREEN
                    )
                else:
                    # restore size cũ
                    screen = pygame.display.set_mode(
                        windowed_size,
                        pygame.RESIZABLE
                    )

                transition.resize(screen.get_size())
                level_select.on_resize(screen)

            elif event.key == pygame.K_j:
                hud.show_objectives = not hud.show_objectives

        # ===== UI EVENTS =====
        if state == GameState.MENU:
            result = menu.handle_event(event, screen)
            if result == "PLAY" and not transition.is_active():
                next_state = GameState.LEVEL_SELECT
                transition.start_close()

        elif state == GameState.LEVEL_SELECT:
            result = level_select.handle_event(event, screen)
            if result == "BACK" and not transition.is_active():
                next_state = GameState.MENU
                transition.start_close()
            elif isinstance(result, int) and not transition.is_active():
                next_state = GameState.PLAYING
                next_level = result
                transition.start_close()

        elif state == GameState.PLAYING and quest_panel:
            quest_panel.handle_event(event)

    # ================= UPDATE =================
    if state == GameState.PLAYING:
        keys = pygame.key.get_pressed()
        level_manager.update(dt, keys)

        if level_manager.request_go_home:
            next_state = GameState.MENU
            transition.start_close()
            level_manager.request_go_home = False

        if level_manager.request_go_level_select:
            next_state = GameState.LEVEL_SELECT
            transition.start_close()
            level_manager.request_go_level_select = False

    transition.update(dt)

    # ================= STATE SWITCH =================
    if transition.is_closed() and next_state:
        state = next_state

        if state == GameState.PLAYING and next_level:
            level_manager.load_level(next_level)

            hud = HUD(
                level_manager.item_manager,
                level_manager.objective
            )

            quest_path = f"data/quests/level{next_level}.json"
            quest_manager = QuestManager(quest_path)

            quest_panel = QuestPanel(
                quest_manager,
                level_manager.player.skills,
                level_manager
            )

            level_manager.quest_panel = quest_panel
            next_level = None

        next_state = None
        transition.start_open()

    # ================= DRAW =================
    if state == GameState.MENU:
        menu.draw(screen, dt)

    elif state == GameState.LEVEL_SELECT:
        level_select.update(dt)
        level_select.draw(screen, dt)

    elif state == GameState.PLAYING:
        world.fill((20, 20, 25))
        level_manager.draw(world)

        draw_scaled_world()
        hud.draw(screen)

        if quest_panel:
            quest_panel.draw(screen)

    transition.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
