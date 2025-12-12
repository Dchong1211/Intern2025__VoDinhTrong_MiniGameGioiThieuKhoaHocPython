import pygame
from level_manager import LevelManager

pygame.init()

# Cấu hình cửa sổ mặc định
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Python Adventure")

clock = pygame.time.Clock()

level_manager = LevelManager()

fullscreen = False
running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Toggle fullscreen bằng F11
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen

                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    # Update logic của level
    level_manager.update(dt)

    # Render
    screen.fill((20, 20, 20))
    level_manager.draw(screen)

    pygame.display.flip()

pygame.quit()
