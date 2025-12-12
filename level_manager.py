import pygame
from pytmx.util_pygame import load_pygame
from player import Player


class LevelManager:
    def __init__(self):
        self.levels = {
            1: "map/Level1.tmx",
        }

        self.current_level = 1
        self.tmx_data = None
        self.map_surface = None
        self.player = None
        self.objects = {}

        # Collision rectangles in ORIGINAL coordinate
        self.collision_rects = []

        self.load_level(self.current_level)

    # =====================================
    def load_level(self, level_id):
        print(f"> Load Level {level_id}")

        level_path = self.levels[level_id]
        self.tmx_data = load_pygame(level_path)

        width = self.tmx_data.width * self.tmx_data.tilewidth
        height = self.tmx_data.height * self.tmx_data.tileheight
        self.map_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.draw_tile_layers()
        self.load_objects()

    # =====================================
    def draw_tile_layers(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    px = x * self.tmx_data.tilewidth
                    py = y * self.tmx_data.tileheight
                    self.map_surface.blit(tile, (px, py))

    # =====================================
    def load_objects(self):
        self.objects.clear()
        self.collision_rects = []   # RESET COLLISIONS

        for obj in self.tmx_data.objects:

            # Spawn player
            if obj.name == "Player":
                self.player = Player(obj.x, obj.y)

            # Collision rectangles
            if obj.name == "Collisions" or obj.type == "Collisions":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.collision_rects.append(rect)

            # Other objects
            if obj.type and obj.type != "Collisions":
                if obj.type not in self.objects:
                    self.objects[obj.type] = []
                self.objects[obj.type].append(obj)

    # =====================================
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self.player:
            # UPDATE USING ORIGINAL COORDINATES
            self.player.update(dt, keys, self.collision_rects)

    # =====================================
    def draw(self, screen):
        sw, sh = screen.get_size()
        mw, mh = self.map_surface.get_size()

        # Scale map to screen
        scaled_map = pygame.transform.scale(self.map_surface, (sw, sh))
        screen.blit(scaled_map, (0, 0))

        # Scale factor (for drawing only)
        scale_x = sw / mw
        scale_y = sh / mh

        # DRAW PLAYER (RENDER ONLY — NO COLLISION)
        if self.player:

            # Scale sprite visual size
            pw = int(self.player.rect.width * scale_x)
            ph = int(self.player.rect.height * scale_y)

            # Convert world coords → screen coords for rendering
            px = int(self.player.rect.x * scale_x)
            py = int(self.player.rect.y * scale_y)

            frame = pygame.transform.scale(self.player.get_frame(), (pw, ph))
            screen.blit(frame, (px, py))
