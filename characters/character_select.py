import pygame
from characters.character_data import CHARACTERS
from player.animation import Animation


class CharacterSelect:
    ICON_SIZE = 96

    def __init__(self, char_manager):
        self.cm = char_manager

        self.anims = {}
        for name, info in CHARACTERS.items():
            sheet = pygame.image.load(info["preview"]).convert_alpha()
            anim = Animation(
                sheet,
                32, 32,
                speed=0.15,
                loop=True
            )
            self.anims[name] = anim

        self.font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 18
        )

        self.selected_rects = {}

    # ================= EVENT =================
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        mx, my = event.pos
        for name, rect in self.selected_rects.items():
            if rect.collidepoint(mx, my):

                # đã sở hữu → chọn
                if self.cm.is_owned(name):
                    self.cm.select(name)

                # chưa sở hữu → thử mua
                else:
                    self.cm.buy(name)

    # ================= UPDATE =================
    def update(self, dt):
        for anim in self.anims.values():
            anim.update()

    # ================= DRAW =================
    def draw(self, surf):
        sw, sh = surf.get_size()
        y = sh // 2 - 60
        start_x = sw // 2 - (len(CHARACTERS) * 140) // 2

        self.selected_rects.clear()

        for i, name in enumerate(CHARACTERS):
            anim = self.anims[name]
            frame = anim.get_image()
            frame = pygame.transform.scale(
                frame,
                (self.ICON_SIZE, self.ICON_SIZE)
            )

            x = start_x + i * 140
            rect = frame.get_rect(center=(x, y))
            self.selected_rects[name] = rect

            # chưa mua → làm tối
            if not self.cm.is_owned(name):
                dark = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                dark.fill((0, 0, 0, 150))
                frame.blit(dark, (0, 0))

            surf.blit(frame, rect)

            # đang chọn → viền vàng
            if self.cm.selected == name:
                pygame.draw.rect(
                    surf,
                    (255, 215, 0),
                    rect.inflate(10, 10),
                    3
                )

            # ===== TÊN =====
            txt = self.font.render(name, True, (255, 255, 255))
            surf.blit(
                txt,
                txt.get_rect(midtop=(rect.centerx, rect.bottom + 8))
            )

            # ===== GIÁ =====
            if not self.cm.is_owned(name):
                price = CHARACTERS[name]["price"]
                ptxt = self.font.render(
                    str(price), True, (255, 80, 80)
                )
                surf.blit(
                    ptxt,
                    ptxt.get_rect(
                        midtop=(rect.centerx, rect.bottom + 30)
                    )
                )
