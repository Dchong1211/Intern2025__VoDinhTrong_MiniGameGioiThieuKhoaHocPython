import pygame
from characters.character_data import CHARACTERS


class CharacterSelect:
    ICON_SIZE = 96

    def __init__(self, char_manager):
        self.cm = char_manager

        self.icons = {
            name: pygame.image.load(info["preview"]).convert_alpha()
            for name, info in CHARACTERS.items()
        }

        self.font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 18
        )

        # layout
        self.start_x = 200
        self.start_y = 200
        self.gap = 140

    # ================= DRAW =================
    def draw(self, surf):
        for i, name in enumerate(CHARACTERS):
            x = self.start_x + i * self.gap
            y = self.start_y

            icon = pygame.transform.scale(
                self.icons[name],
                (self.ICON_SIZE, self.ICON_SIZE)
            )
            rect = icon.get_rect(topleft=(x, y))

            # 🔒 chưa mua → tối màu
            if not self.cm.is_owned(name):
                dark = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
                dark.fill((0, 0, 0, 160))
                icon.blit(dark, (0, 0))

            # ⭐ đang chọn → viền vàng
            if self.cm.get_selected() == name:
                pygame.draw.rect(
                    surf,
                    (255, 215, 0),
                    rect.inflate(10, 10),
                    3
                )

            surf.blit(icon, rect)

            # ===== NAME =====
            name_txt = self.font.render(name, True, (255, 255, 255))
            surf.blit(
                name_txt,
                (
                    rect.centerx - name_txt.get_width() // 2,
                    rect.bottom + 6
                )
            )

            # ===== PRICE =====
            if not self.cm.is_owned(name):
                price = CHARACTERS[name]["price"]
                price_txt = self.font.render(
                    f"{price} 🍎",
                    True,
                    (255, 120, 120)
                )
                surf.blit(
                    price_txt,
                    (
                        rect.centerx - price_txt.get_width() // 2,
                        rect.bottom + 26
                    )
                )

    # ================= EVENT =================
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        mx, my = event.pos

        for i, name in enumerate(CHARACTERS):
            x = self.start_x + i * self.gap
            y = self.start_y
            rect = pygame.Rect(
                x, y,
                self.ICON_SIZE, self.ICON_SIZE
            )

            if rect.collidepoint(mx, my):
                if self.cm.is_owned(name):
                    self.cm.select(name)
                else:
                    self.cm.buy(name)
