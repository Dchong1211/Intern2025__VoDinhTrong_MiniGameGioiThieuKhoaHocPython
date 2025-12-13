import pygame
import sys

from level.level_manager import LevelManager
from ui.hud import HUD
from ui.main_menu import MainMenu
from ui.game_state import GameState

pygame.init()
pygame.display.set_caption("CodeRun")

BASE_W, BASE_H = 1280, 720
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)

clock = pygame.time.Clock()
FPS = 60
fullscreen = False

# ===== STATE =====
state = GameState.MENU

menu = MainMenu()
level_manager = LevelManager()

# World
WORLD_W = level_manager.map_w
WORLD_H = level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

hud = HUD(level_manager.item_manager)

def draw_scaled_world():
    sw, sh = screen.get_size()
    scale = sh / WORLD_H

    draw_w = int(WORLD_W * scale)
    draw_h = sh

    scaled = pygame.transform.scale(world, (draw_w, draw_h))
    x = (sw - draw_w) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled, (x, 0))

running = True
while running:
    dt = clock.tick(FPS) / 1000

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

    # =============== MENU =================
    if state == GameState.MENU:
        result = menu.update(screen)
        if result == "PLAY":
            state = GameState.PLAYING

    # =============== PLAYING =================
    elif state == GameState.PLAYING:
        keys = pygame.key.get_pressed()
        level_manager.update(dt, keys)

        world.fill((20, 20, 25))
        level_manager.draw(world)

        draw_scaled_world()
        hud.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
