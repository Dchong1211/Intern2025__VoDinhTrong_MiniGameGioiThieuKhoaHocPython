import pygame
import os


class HUD:
    def __init__(self, item_manager, objective):
        self.item_manager = item_manager
        self.objective = objective
        self.font_path = "assets/Font/FVF Fernando 08.ttf"

        self.show_objectives = True

        # ================= FRUIT ICON =================
        base = "assets/Items/Fruits"
        self.icons = {}

        for name in self.item_manager.count:
            sheet = pygame.image.load(
                os.path.join(base, f"{name}.png")
            ).convert_alpha()

            frame = sheet.subsurface((0, 0, 32, 32))
            frame = pygame.transform.scale(frame, (56, 56))
            self.icons[name] = frame

        # ================= SETTINGS ICON =================
        self.setting_icon = pygame.image.load(
            "assets/Menu/Buttons/Settings.png"
        ).convert_alpha()

        self.setting_rect = None

    # ==================================================
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

    # ==================================================
    def draw_inventory(self, surf):
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
            if not self.item_manager.discovered.get(name, False):
                continue

            count = self.item_manager.count[name]

            size = int(56 * ui_scale)
            icon_scaled = pygame.transform.scale(icon, (size, size))
            rect = icon_scaled.get_rect(topright=(x, y))
            surf.blit(icon_scaled, rect)

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

    # ==================================================
    def draw_objectives(self, surf):
        if not self.objective or not self.objective.objectives:
            return

        font_title = pygame.font.Font(self.font_path, 18)
        font_item = pygame.font.Font(self.font_path, 14)

        padding = 10
        line_spacing = 6
        outline = 2

        icon_size = 42
        icon_gap = 8

        rendered_lines = []

        title = self.render_text_outline(
            "MISSION",
            font_title,
            (255, 220, 120),
            (0, 0, 0),
            outline
        )
        rendered_lines.append((title, None))

        for name, data in self.objective.objectives.items():
            collected = data["collected"]
            required = data["required"]

            completed = collected >= required
            color = (0, 220, 0) if completed else (255, 255, 255)

            text = self.render_text_outline(
                f"{name}: {collected}/{required}",
                font_item,
                color,
                (0, 0, 0),
                outline
            )

            icon = None
            if name in self.icons:
                icon = pygame.transform.scale(
                    self.icons[name],
                    (icon_size, icon_size)
                )

            rendered_lines.append((text, icon))

        max_width = 0
        total_height = 0

        for text, icon in rendered_lines:
            w = text.get_width()
            if icon:
                w += icon_gap + icon.get_width()
            max_width = max(max_width, w)
            total_height += text.get_height() + line_spacing

        box_w = max_width + padding * 2
        box_h = total_height + padding * 2

        # 👉 GÓC TRÊN TRÁI
        x = 16
        y = 16

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surf.blit(bg, (x, y))

        draw_y = y + padding

        title_text, _ = rendered_lines[0]
        surf.blit(
            title_text,
            (
                x + (box_w - title_text.get_width()) // 2,
                draw_y
            )
        )
        draw_y += title_text.get_height() + line_spacing

        for text, icon in rendered_lines[1:]:
            surf.blit(text, (x + padding, draw_y))

            if icon:
                surf.blit(
                    icon,
                    (
                        x + padding + text.get_width() + icon_gap,
                        draw_y + (text.get_height() - icon.get_height()) // 2
                    )
                )

            draw_y += text.get_height() + line_spacing

    # ==================================================
    def draw_settings_icon(self, surf):
        sw, sh = surf.get_size()
        size = 48

        icon = pygame.transform.scale(self.setting_icon, (size, size))

        # 👉 GÓC DƯỚI TRÁI
        x = 16
        y = sh - size - 16

        surf.blit(icon, (x, y))
        self.setting_rect = pygame.Rect(x, y, size, size)

    # ==================================================
    def draw(self, surf):
        if self.show_objectives:
            self.draw_objectives(surf)

        self.draw_inventory(surf)
        self.draw_settings_icon(surf)
