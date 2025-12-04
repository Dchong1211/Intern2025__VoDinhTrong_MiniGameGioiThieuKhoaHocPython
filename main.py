import pygame
import os
from player.player import Player
from level_manager import LevelManager
from items.item_manager import ItemManager
from ui.puzzle_ui import PuzzleUI

pygame.init()
pygame.display.set_caption("Code Run")

SCREEN_W, SCREEN_H = 1280, 720
ZOOM = 2
VIEW_W, VIEW_H = SCREEN_W // ZOOM, SCREEN_H // ZOOM

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
world = pygame.Surface((VIEW_W, VIEW_H))
clock = pygame.time.Clock()

BASE = os.path.dirname(__file__)


def draw_map(surf, tmx, cam_x, cam_y):
    tw, th = tmx.tilewidth, tmx.tileheight
    for layer in tmx.layers:
        if hasattr(layer, "data") and layer.visible:
            for y, row in enumerate(layer.data):
                for x, gid in enumerate(row):
                    img = tmx.get_tile_image_by_gid(gid)
                    if img:
                        surf.blit(img, (x * tw - cam_x, y * th - cam_y))


def main():
    # load level đầu tiên
    level = LevelManager(BASE).load(1)

    px, py = level.spawn
    player = Player(px, py, BASE)

    collisions = level.collisions
    goal = level.goal
    item_manager = ItemManager(level.items)

    puzzle_ui = None
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if puzzle_ui:
                puzzle_ui.handle_event(e)

        keys = pygame.key.get_pressed()

        # nếu puzzle đang mở thì chỉ update UI
        if puzzle_ui:
            puzzle_ui.update()
            if not puzzle_ui.active:
                puzzle_ui = None

        else:
            # update player + item
            player.update(collisions, keys)
            item_manager.update(player)

            # mở puzzle khi đủ fragment
            if player.pending_puzzle and not puzzle_ui:
                skill = player.pending_puzzle
                fragments = [
                    it for it in level.items
                    if it.skill_key == skill and it.is_fragment
                ]
                puzzle_ui = PuzzleUI(player, skill, fragments)
                player.pending_puzzle = None

            # chuyển level khi chạm goal
            if goal and player.rect.colliderect(goal):
                next_level = level.level_index + 1
                print("Loading next level:", next_level)

                level = LevelManager(BASE).load(next_level)
                collisions = level.collisions
                goal = level.goal
                item_manager = ItemManager(level.items)

                px, py = level.spawn
                player.rect.topleft = (px, py)
                player.x, player.y = px, py
                player.vel_x = 0
                player.vel_y = 0
                player.state = "idle"

                continue

            # respawn nếu rơi khỏi map
            if player.y > level.map_h + 200:
                px, py = level.spawn
                player.rect.topleft = (px, py)
                player.x, player.y = px, py
                player.vel_x = 0
                player.vel_y = 0
                player.state = "idle"

        # camera
        cam_x = int(player.x - VIEW_W // 2)
        cam_y = int(player.y - VIEW_H // 2)
        cam_x = max(0, min(cam_x, level.map_w - VIEW_W))
        cam_y = max(0, min(cam_y, level.map_h - VIEW_H))

        world.fill((0, 0, 0))
        draw_map(world, level.tmx, cam_x, cam_y)
        item_manager.draw(world, cam_x, cam_y)
        player.draw(world, cam_x, cam_y)

        screen.blit(pygame.transform.scale(world, (SCREEN_W, SCREEN_H)), (0, 0))
        if puzzle_ui:
            puzzle_ui.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
