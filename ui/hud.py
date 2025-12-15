import pygame
import os


class HUD:
    def __init__(self, item_manager):
        self.item_manager = item_manager
        self.font_path = "assets/Font/FVF Fernando 08.ttf"

        base = "assets/Items/Fruits"
        self.icons = {}

        # load tất cả icon nhưng KHÔNG vẽ nếu chưa discovered
        for name in self.item_manager.count:
            sheet = pygame.image.load(
                os.path.join(base, f"{name}.png")
            ).convert_alpha()

            icon = sheet.subsurface((0, 0, 32, 32))
            icon = pygame.transform.scale(icon, (56, 56))
            self.icons[name] = icon

    # ======================================
    def render_text_outline(self, text, font, color, outline, thickness):
        base = font.render(text, True, color)
        w, h = base.get_size()
        surf = pygame.Surface(
            (w + thickness * 2, h + thickness * 2),
            pygame.SRCALPHA
        )

        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx or dy:
                    surf.blit(
                        font.render(text, True, outline),
                        (dx + thickness, dy + thickness)
                    )

        surf.blit(base, (thickness, thickness))
        return surf

    # ======================================
    def draw(self, surf):
        sw, sh = surf.get_size()
        ui_scale = sh / 720

        font = pygame.font.Font(
            self.font_path,
            int(14 * ui_scale)
        )

        x = sw - int(70 * ui_scale)
        y = int(42 * ui_scale)
        spacing = int(92 * ui_scale)

        for name, icon in self.icons.items():

            # 🔥 CHƯA PHÁT HIỆN → KHÔNG HIỆN
            if not self.item_manager.discovered[name]:
                continue

            count = self.item_manager.count[name]

            size = int(56 * ui_scale)
            icon = pygame.transform.scale(icon, (size, size))
            rect = icon.get_rect(topright=(x, y))
            surf.blit(icon, rect)

            text = self.render_text_outline(
                f"x{count}",
                font,
                (255, 255, 255),
                (0, 0, 0),
                max(1, int(3 * ui_scale))
            )

            surf.blit(
                text,
                text.get_rect(
                    midleft=(
                        rect.right - int(4 * ui_scale),
                        rect.centery
                    )
                )
            )

            x -= spacing
