import pygame
import os


class HUD:
    def __init__(self, item_manager, objective):
        self.item_manager = item_manager
        self.objective = objective
        self.font_path = "assets/Font/FVF Fernando 08.ttf"

        # 🔥 bật / tắt mission (phím J)
        self.show_objectives = True

        base = "assets/Items/Fruits"
        self.icons = {}

        # ===== LOAD ICON (FRAME ĐẦU) =====
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
    def draw_inventory(self, surf):
        """Inventory bên phải"""
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

            # chưa discovered → không hiện
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

    # ======================================
    def draw_objectives(self, surf):
        if not self.objective or not self.objective.objectives:
            return

        # ===== UI SCALE (CHO TRẺ EM) =====
        font_title = pygame.font.Font(self.font_path, 18)
        font_item = pygame.font.Font(self.font_path, 14)

        x = 16
        y = 16
        padding = 10
        line_spacing = 6
        outline = 2

        icon_size = 64 
        icon_gap = 8

        rendered_lines = []

        # ===== TITLE =====
        title = self.render_text_outline(
            "MISSION",
            font_title,
            (255, 220, 120),
            (0, 0, 0),
            outline
        )
        rendered_lines.append((title, None))

        # ===== OBJECTIVES =====
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

        # ===== TÍNH KÍCH THƯỚC KHUNG (CHUẨN, KHÔNG TRÀN) =====
        max_width = 0
        total_height = 0

        for text, icon in rendered_lines:
            line_width = text.get_width()
            if icon:
                line_width += icon_gap + icon.get_width()

            max_width = max(max_width, line_width)
            total_height += text.get_height() + line_spacing

        box_width = max_width + padding * 2
        box_height = total_height + padding * 2

        # ===== NỀN ĐEN MỜ =====
        bg = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surf.blit(bg, (x, y))

        draw_y = y + padding

        # ===== TITLE (CĂN GIỮA) =====
        title_text, _ = rendered_lines[0]
        title_x = x + (box_width - title_text.get_width()) // 2
        surf.blit(title_text, (title_x, draw_y))
        draw_y += title_text.get_height() + line_spacing

        # ===== OBJECTIVE LINES =====
        for text, icon in rendered_lines[1:]:
            surf.blit(text, (x + padding, draw_y))

            if icon:
                icon_x = x + padding + text.get_width() + icon_gap
                icon_y = draw_y + (text.get_height() - icon.get_height()) // 2
                surf.blit(icon, (icon_x, icon_y))

            draw_y += text.get_height() + line_spacing

    # ======================================
    def draw(self, surf):
        # mission bên trái (có thể bật / tắt bằng phím J)
        if self.show_objectives:
            self.draw_objectives(surf)

        # inventory bên phải (luôn hiện)
        self.draw_inventory(surf)
