import os
import pygame
from pytmx import load_pygame
from items.item import Item


class LevelManager:
    def __init__(self, base_dir):
        self.base = base_dir
        self.tmx = None
        self.level_index = 1

        self.map_w = 0
        self.map_h = 0
        self.spawn = (0, 0)
        self.collisions = []
        self.goal = None

        # tất cả item trên map (code fragment, coin,…)
        self.items = []

    # LOAD LEVEL
    def load(self, level_number):
        self.level_index = level_number

        path = os.path.join(self.base, f"assets/levels/level{level_number}.tmx")
        print("Loading:", path)

        self.tmx = load_pygame(path)

        tw, th = self.tmx.tilewidth, self.tmx.tileheight
        self.map_w = self.tmx.width * tw
        self.map_h = self.tmx.height * th

        # RESET DATA
        self.spawn = (0, 0)
        self.collisions = []
        self.goal = None
        self.items = []

        # PARSE OBJECTS
        for obj in self.tmx.objects:

            # Player spawn
            if obj.name == "Player":
                self.spawn = (obj.x, obj.y)

            # Collision
            elif obj.name == "Collision":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.collisions.append(rect)

            # Goal
            elif obj.name == "Goal":
                self.goal = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            # Item (fragment)
            elif obj.name == "Item":
                item_type = obj.properties.get("item_type", "fragment")

                skill = obj.properties.get("skill")      # vd: "jump"
                code  = obj.properties.get("code")       # vd: "Jump", "=", "True"

                index = obj.properties.get("index")
                index = int(index) if index is not None else 0

                rows = obj.properties.get("rows")
                rows = int(rows) if rows is not None else 1

                cols = obj.properties.get("cols")
                cols = int(cols) if cols is not None else 1

                required = obj.properties.get("required")
                required = int(required) if required is not None else 1

                self.items.append(
                    Item(
                        x=obj.x,
                        y=obj.y,
                        item_type=item_type,
                        skill_key=skill,
                        code=code,
                        index=index,
                        rows=rows,
                        cols=cols,
                        required=required
                    )
                )

        return self
