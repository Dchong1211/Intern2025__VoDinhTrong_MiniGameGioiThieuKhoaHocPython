import os
import pygame
from ui.button import Button


class HUD:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"

    def __init__(self, item_manager, objective):
        self.item_manager = item_manager
        self.objective = objective

        self.show_objectives = True
        self.setting_buttons = {}   # name -> Button
        self._last_setting_size = (0, 0)

        # ===== INVENTORY ICONS =====
        self.icons = self._load_icons()

        # ===== SETTINGS ICON =====
        self.setting_icon = pygame.image.load(
            "assets/Menu/Buttons/Settings.png"
        ).convert_alpha()

        self.setting_rect = None
        self.setting_open = False
        self.sound_on = True

        # ===== SETTING PANEL ASSETS =====
        self.board_img = pygame.image.load(
            "assets/Menu/Buttons/Board_1.png"
        ).convert_alpha()

        self.icon_home = pygame.image.load(
            "assets/Menu/Buttons/Home.png"
        ).convert_alpha()

        self.icon_levels = pygame.image.load(
            "assets/Menu/Buttons/Levels.png"
        ).convert_alpha()

        self.icon_restart = pygame.image.load(
            "assets/Menu/Buttons/Restart.png"
        ).convert_alpha()

        self.icon_volume = pygame.image.load(
            "assets/Menu/Buttons/Volume.png"
        ).convert_alpha()

        self.icon_unvolume = pygame.image.load(
            "assets/Menu/Buttons/Unvolume.png"
        ).convert_alpha()

        self.btn_rects = {}

    # ======================================================
    # LOAD ICONS
    # ======================================================
    def _load_icons(self):
        base = "assets/Items/Fruits"
        icons = {}

        for name in self.item_manager.count:
            sheet = pygame.image.load(
                os.path.join(base, f"{name}.png")
            ).convert_alpha()

            icons[name] = sheet.subsurface((0, 0, 32, 32))

        return icons

    # ======================================================
    # UTILS
    # ======================================================
    def _scale(self, surf):
        return surf.get_height() / self.BASE_H

    def _font(self, size, scale):
        return pygame.font.Font(
            self.FONT_PATH,
            max(1, int(size * scale))
        )

    def _outline_text(self, text, font, color, outline, thick):
        base = font.render(text, True, color)
        w, h = base.get_size()

        surf = pygame.Surface(
            (w + thick * 2, h + thick * 2),
            pygame.SRCALPHA
        )

        for dx in range(-thick, thick + 1):
            for dy in range(-thick, thick + 1):
                if dx or dy:
                    surf.blit(
                        font.render(text, True, outline),
                        (dx + thick, dy + thick)
                    )

        surf.blit(base, (thick, thick))
        return surf

    # ======================================================
    # HANDLE EVENT (IMPORTANT)
    # ======================================================
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mx, my = event.pos

        # click setting icon
        if self.setting_rect and self.setting_rect.collidepoint(mx, my):
            self.setting_open = not self.setting_open
            return None

        if not self.setting_open:
            return None

        for key, rect in self.btn_rects.items():
            if rect.collidepoint(mx, my):
                if key == "SOUND":
                    self.sound_on = not self.sound_on
                    return "TOGGLE_SOUND"
                return key

        return None

    # ======================================================
    # INVENTORY
    # ======================================================
    def _draw_inventory(self, surf, scale):
        sw, _ = surf.get_size()

        font = self._font(14, scale)
        size = int(56 * scale)
        spacing = int(92 * scale)

        x = sw - int(70 * scale)
        y = int(42 * scale)

        for name, icon in self.icons.items():
            if not self.item_manager.discovered.get(name):
                continue

            count = self.item_manager.count[name]
            icon_scaled = pygame.transform.scale(icon, (size, size))
            rect = icon_scaled.get_rect(topright=(x, y))
            surf.blit(icon_scaled, rect)

            text = self._outline_text(
                f"x{count}",
                font,
                (255, 255, 255),
                (0, 0, 0),
                max(1, int(3 * scale))
            )

            surf.blit(
                text,
                text.get_rect(
                    midleft=(rect.right - int(4 * scale), rect.centery)
                )
            )

            x -= spacing

    # ======================================================
    # OBJECTIVES
    # ======================================================
    def _draw_objectives(self, surf, scale):
        if not self.objective or not self.objective.objectives:
            return

        font_title = self._font(18, scale)
        font_item = self._font(14, scale)

        pad = int(10 * scale)
        gap = int(6 * scale)
        outline = max(1, int(2 * scale))
        icon_size = int(42 * scale)
        icon_gap = int(8 * scale)

        lines = []

        title = self._outline_text(
            "MISSION",
            font_title,
            (255, 220, 120),
            (0, 0, 0),
            outline
        )
        lines.append((title, None))

        for name, data in self.objective.objectives.items():
            c, r = data["collected"], data["required"]
            color = (0, 220, 0) if c >= r else (255, 255, 255)

            text = self._outline_text(
                f"{name}: {c}/{r}",
                font_item,
                color,
                (0, 0, 0),
                outline
            )

            icon = pygame.transform.scale(
                self.icons[name],
                (icon_size, icon_size)
            ) if name in self.icons else None

            lines.append((text, icon))

        max_w = max(
            text.get_width() + (icon.get_width() + icon_gap if icon else 0)
            for text, icon in lines
        )

        total_h = sum(text.get_height() + gap for text, _ in lines)

        box_w = max_w + pad * 2
        box_h = total_h + pad * 2

        x = int(16 * scale)
        y = int(16 * scale)

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surf.blit(bg, (x, y))

        draw_y = y + pad

        title_text, _ = lines[0]
        surf.blit(
            title_text,
            (x + (box_w - title_text.get_width()) // 2, draw_y)
        )
        draw_y += title_text.get_height() + gap

        for text, icon in lines[1:]:
            surf.blit(text, (x + pad, draw_y))
            if icon:
                surf.blit(
                    icon,
                    (
                        x + pad + text.get_width() + icon_gap,
                        draw_y + (text.get_height() - icon.get_height()) // 2
                    )
                )
            draw_y += text.get_height() + gap
    def _is_hover(self, rect):
        mx, my = pygame.mouse.get_pos()
        return rect.collidepoint(mx, my)

    # ======================================================
    # SETTINGS ICON
    # ======================================================
    def _draw_settings_icon(self, surf, scale):
        sw, sh = surf.get_size()
        size = int(48 * scale)

        icon = pygame.transform.scale(self.setting_icon, (size, size))

        x = int(16 * scale)
        y = sh - size - int(16 * scale)

        surf.blit(icon, (x, y))
        self.setting_rect = pygame.Rect(x, y, size, size)

    # ======================================================
    # SETTINGS PANEL
    # ======================================================
    def _draw_setting_panel(self, surf, scale):
        if not self.setting_rect:
            return

        sw, sh = surf.get_size()

        # ===== PANEL SIZE =====
        panel_w = int(320 * scale)
        panel_h = int(96 * scale)
        GAP = int(12 * scale)

        px = self.setting_rect.right + GAP
        py = self.setting_rect.centery - panel_h // 2

        px = max(GAP, min(px, sw - panel_w - GAP))
        py = max(GAP, min(py, sh - panel_h - GAP))

        panel_rect = pygame.Rect(px, py, panel_w, panel_h)

        # ===== DRAW BOARD =====
        board = pygame.transform.scale(self.board_img, (panel_w, panel_h))
        surf.blit(board, panel_rect.topleft)

        # ===== ICON CONFIG =====
        icon_size = int(48 * scale)
        gap = int(20 * scale)

        icons = [
            ("HOME", self.icon_home),
            ("LEVEL", self.icon_levels),
            ("RESTART", self.icon_restart),
            ("SOUND", self.icon_volume if self.sound_on else self.icon_unvolume),
        ]

        total_w = len(icons) * icon_size + (len(icons) - 1) * gap
        start_x = panel_rect.left + (panel_w - total_w) // 2
        y = panel_rect.top + (panel_h - icon_size) // 2

        # ===== REBUILD BUTTONS =====
        if not self.setting_buttons or self._last_setting_size != panel_rect.size:
            self.setting_buttons.clear()
            self.btn_rects.clear()
            self._last_setting_size = panel_rect.size

            for i, (name, icon) in enumerate(icons):
                img = pygame.transform.scale(icon, (icon_size, icon_size))

                target_x = start_x + i * (icon_size + gap) + icon_size // 2
                target_y = y + icon_size // 2

                cx, cy = panel_rect.center

                btn = Button(
                    image=img,
                    offset=(target_x - panel_rect.centerx,
                            target_y - panel_rect.centery),
                    origin=panel_rect.center
                )


                btn.bounce_speed = 8.0
                btn.target_offset_y = 0

                self.setting_buttons[name] = btn

        # ===== UPDATE & DRAW =====
        for name, btn in self.setting_buttons.items():
            btn.handle_hover()
            btn.update(1 / 60, surf)
            btn.draw(surf)
            self.btn_rects[name] = btn.rect

    # ======================================================
    # MAIN DRAW
    # ======================================================
    def draw(self, surf):
        scale = self._scale(surf)

        if self.show_objectives:
            self._draw_objectives(surf, scale)

        self._draw_inventory(surf, scale)
        self._draw_settings_icon(surf, scale)

        if self.setting_open:
            self._draw_setting_panel(surf, scale)
