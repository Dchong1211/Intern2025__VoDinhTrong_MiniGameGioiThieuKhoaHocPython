import pygame
from ui.button import Button


class MainMenu:
    BASE_H = 720
    FONT_PATH = "assets/Menu/Text/FVF Fernando 08.ttf"

    def __init__(self):
        # ===== BACKGROUND =====
        self.bg = pygame.image.load(
            "assets/Background/Menu/Background_menu.png"
        ).convert()

        # ===== PLAY BUTTON IMAGE =====
        self.play_img_raw = pygame.image.load(
            "assets/Menu/Buttons/Play_Text.png"
        ).convert_alpha()

        # ===== PLAY BUTTON =====
        self.play_btn = Button(
            image=self.play_img_raw,
            anchor=("center", "center"),
            offset=(0, 0)
        )

        # ===== TITLE =====
        self.title_left = "Code"
        self.title_right = "Fruit"

    # ==============================
    def handle_event(self, event, screen):
        if self.play_btn.handle_event(event):
            return "PLAY"
        return None

    # ==============================
    def draw(self, screen, dt):
        sw, sh = screen.get_size()
        scale = sh / self.BASE_H

        # ===== BACKGROUND =====
        screen.blit(
            pygame.transform.scale(self.bg, (sw, sh)),
            (0, 0)
        )

        # ===== TITLE =====
        self._draw_title(screen, scale)

        # ===== PLAY BUTTON (KHÔNG SCALE ĐỘNG) =====
        btn_w = int(260 * scale)
        ratio = btn_w / self.play_img_raw.get_width()
        btn_h = int(self.play_img_raw.get_height() * ratio)

        # scale 1 lần theo màn hình, KHÔNG scale mỗi frame
        self.play_btn.image = pygame.transform.smoothscale(
            self.play_img_raw,
            (btn_w, btn_h)
        )

        # hover + update bounce
        self.play_btn.handle_hover()
        self.play_btn.update(dt, screen)
        self.play_btn.draw(screen)

    # ==============================
    def _draw_title(self, screen, scale):
        sw, sh = screen.get_size()
        size = int(96 * scale)
        shadow = max(2, int(4 * scale))

        font = pygame.font.Font(self.FONT_PATH, size)

        code = font.render(self.title_left, True, (255, 255, 255))
        fruit = font.render(self.title_right, True, (255, 220, 120))

        total_w = code.get_width() + fruit.get_width()
        x = (sw - total_w) // 2
        y = int(80 * scale)

        # shadow
        screen.blit(
            font.render(self.title_left, True, (0, 0, 0)),
            (x + shadow, y + shadow)
        )
        screen.blit(
            font.render(self.title_right, True, (0, 0, 0)),
            (x + code.get_width() + shadow, y + shadow)
        )

        # text
        screen.blit(code, (x, y))
        screen.blit(fruit, (x + code.get_width(), y))
