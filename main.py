import pygame
import sys
from level_manager import LevelManager

pygame.init()
pygame.display.set_caption("CodeRun")

BASE_W, BASE_H = 1280, 720

screen = pygame.display.set_mode(
    (BASE_W, BASE_H),
    pygame.RESIZABLE
)

clock = pygame.time.Clock()
FPS = 60

fullscreen = False

# Load level
level_manager = LevelManager()

WORLD_W = level_manager.map_w
WORLD_H = level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H))

def draw_scaled_world():
    sw, sh = screen.get_size()

    scale = sh / WORLD_H

    draw_w = int(WORLD_W * scale)
    draw_h = sh  # full chiều cao

    scaled = pygame.transform.scale(world, (draw_w, draw_h))

    x = (sw - draw_w) // 2
    y = 0

    screen.fill((0, 0, 0))
    screen.blit(scaled, (x, y))

running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                event.size,
                pygame.RESIZABLE
            )
    keys = pygame.key.get_pressed()

    level_manager.update(dt, keys)

    world.fill((20, 20, 25))
    level_manager.draw(world)

    draw_scaled_world()
    pygame.display.flip()

pygame.quit()
sys.exit()
