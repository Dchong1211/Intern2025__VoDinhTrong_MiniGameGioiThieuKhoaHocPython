import pygame
from ui.button import Button


class MainMenu:
    def __init__(self):
        # ===== BACKGROUND =====
        self.bg = pygame.image.load(
            "assets/Background/Menu/Background_menu.png"
        ).convert()

        # ===== BUTTON IMAGE =====
        self.play_img_raw = pygame.image.load(
            "assets/Menu/Buttons/Play.png"
        ).convert_alpha()

        # ===== FONT =====
        self.font_path = "assets/Menu/Text/FVF Fernando 08.ttf"

        # ===== TEXT CONTENT =====
        self.title_left = "Code"
        self.title_right = "Fruit"

        self.play_btn = None

    # ==================================================
    def update(self, screen):
        sw, sh = screen.get_size()

        # ===== BACKGROUND =====
        bg_scaled = pygame.transform.scale(self.bg, (sw, sh))
        screen.blit(bg_scaled, (0, 0))

        # ===== LOGO =====
        title_size = int(sw * 0.08)
        title_font = pygame.font.Font(self.font_path, title_size)

        title_code = title_font.render(
            self.title_left, True, (255, 255, 255)
        )
        title_fruit = title_font.render(
            self.title_right, True, (255, 220, 120)
        )

        total_width = title_code.get_width() + title_fruit.get_width()
        title_x = sw // 2 - total_width // 2
        title_y = int(sh * 0.10)

        # Shadow
        shadow_offset = 4
        shadow_code = title_font.render(
            self.title_left, True, (0, 0, 0)
        )
        shadow_fruit = title_font.render(
            self.title_right, True, (0, 0, 0)
        )

        screen.blit(shadow_code, (title_x + shadow_offset, title_y + shadow_offset))
        screen.blit(
            shadow_fruit,
            (
                title_x + title_code.get_width() + shadow_offset,
                title_y + shadow_offset
            )
        )

        # Text
        screen.blit(title_code, (title_x, title_y))
        screen.blit(title_fruit, (title_x + title_code.get_width(), title_y))

        # ===== PLAY BUTTON =====
        btn_width = int(sw * 0.04)  # chỉnh size tại đây
        ratio = btn_width / self.play_img_raw.get_width()
        btn_height = int(self.play_img_raw.get_height() * ratio)

        play_img = pygame.transform.smoothscale(
            self.play_img_raw,
            (btn_width, btn_height)
        )

        self.play_btn = Button(
            sw // 2,
            int(sh * 0.48),
            play_img
        )

        if self.play_btn.draw(screen):
            return "PLAY"

        return "MENU"
