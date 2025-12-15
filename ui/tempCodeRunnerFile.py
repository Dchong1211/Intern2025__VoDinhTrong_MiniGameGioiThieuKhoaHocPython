import pygame
import os


class HUD:
    def __init__(self, item_manager):
        self.item_manager = item_manager

        # Font
        self.font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 14
        )

        base = "assets/Items/Fruits"
        self.icons = {}

        # Load icon: chỉ lấy frame đầu
        for name in self.item_manager.count.keys():
            sheet = pygame.image.load(
                os.path.join(base, f"{name}.png")
            ).convert_alpha()

            icon = sheet.subsurface((0, 0, 32, 32))
            icon = pygame.transform.scale(icon, (56, 56))  # to hơn chút

            self.icons[name] = icon

    # ======================================================
    # Render chữ đậm + viền
    def render_text_outline(
        self,
        text,
        font,
        text_color,
        outline_color,
        thickness=2
    ):
        base = font.render(text, True, text_color)
        w, h = base.get_size()

        surf = pygame.Surface(
            (w + thickness * 2, h + thickness * 2),
            pygame.SRCALPHA
        )

        # Vẽ viền
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx != 0 or dy != 0:
                    outline = font.render(text, True, outline_color)
                    surf.blit(outline, (dx + thickness, dy + thickness))

        # Vẽ chữ chính
        surf.blit(base, (thickness, thickness))
        return surf

    # ======================================================
    def draw(self, surf):
        sw, sh = surf.get_size()
        ui_scale = sh / 720

        font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf",
            int(14 * ui_scale)
        )

        x = sw - int(70 * ui_scale)
        y = int(42 * ui_scale)
        spacing = int(92 * ui_scale)

        for name in self.icons:
            count = self.item_manager.count[name]
            base_icon = self.icons[name]

            size = int(56 * ui_scale)
            icon = pygame.transform.scale(base_icon, (size, size))

            icon_rect = icon.get_rect(topright=(x, y))
            surf.blit(icon, icon_rect)

            if count > 0:
                text = self.render_text_outline(
                    f"x{count}",
                    font,
                    (255, 255, 255),
                    (0, 0, 0),
                    thickness=max(1, int(3 * ui_scale))
                )

                text_rect = text.get_rect(
                    midleft=(
                        icon_rect.right - int(4 * ui_scale),
                        icon_rect.centery - int(4 * ui_scale)
                    )
                )
                surf.blit(text, text_rect)

            x -= spacing
