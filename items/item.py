import os
import pygame
from player.animation import Animation


class Item:
    def __init__(self, x, y, item_type="code", skill_key=None,
                 index=None, required=None, rows=None, cols=None,
                 code=None):
        """
        code = text hiển thị trong puzzle (Jump, =, True)
        """

        self.x = x
        self.y = y

        # loại item (fruit, code, fragment…)
        self.type = item_type

        # dùng khi mở skill
        self.skill_key = skill_key

        # text của mảnh puzzle
        self.code = code                # <<< ADDED LINE !!!

        # fragment info
        self.is_fragment = (item_type == "fragment")
        self.index = index
        self.required = required
        self.rows = rows
        self.cols = cols

        self.collected = False
        self.remove = False
        self.play_collect_anim = False

        base = os.path.dirname(os.path.dirname(__file__))

        ITEM_CONFIG = {
            "apple": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Apple.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "banana": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Bananas.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "cherry": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Cherries.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "kiwi": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Kiwi.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "melon": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Melon.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "orange": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Orange.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "pineapple": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Pineapple.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },
            "strawberry": {
                "sprite": os.path.join(base, "assets/Items/Fruits/Strawberry.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.35
            },

            # giấy skill
            "code": {
                "sprite": os.path.join(base, "assets/Items/Paper.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.12
            },

            # mảnh puzzle
            "fragment": {
                "sprite": os.path.join(base, "assets/Items/Paper.png"),
                "frame_w": 32, "frame_h": 32, "speed": 0.12
            },
        }

        cfg = ITEM_CONFIG.get(self.type, ITEM_CONFIG["code"])

        # idle animation
        sheet = pygame.image.load(cfg["sprite"]).convert_alpha()
        self.anim = Animation(sheet, cfg["frame_w"], cfg["frame_h"], cfg["speed"])

        # rect
        self.rect = pygame.Rect(x, y, cfg["frame_w"], cfg["frame_h"])

        # collect animation
        collect_sheet = pygame.image.load(
            os.path.join(base, "assets/Items/Fruits/Collected.png")
        ).convert_alpha()

        self.collect_anim = Animation(collect_sheet, 32, 32, 0.3)


    # pick up item
    def on_pick(self, player):
        if self.collected:
            return

        self.collected = True
        self.play_collect_anim = True

        # fragment → gửi mảnh vào player
        if self.is_fragment:
            player.add_fragment(
                skill_name=self.skill_key,
                required=self.required,
                index=self.index,
                rows=self.rows,
                cols=self.cols
            )
            return

        # code → mở skill thẳng
        if self.type == "code" and self.skill_key:
            setattr(player.skills, self.skill_key, True)
            return


    def update(self):
        if self.remove:
            return

        if self.play_collect_anim:
            self.collect_anim.update()

            if int(self.collect_anim.index) >= len(self.collect_anim.frames) - 1:
                self.remove = True
            return

        self.anim.update()


    def draw(self, surf, cam_x, cam_y):
        if self.remove:
            return

        if self.play_collect_anim:
            img = self.collect_anim.get_image()
        else:
            img = self.anim.get_image()

        surf.blit(img, (self.rect.x - cam_x, self.rect.y - cam_y))
