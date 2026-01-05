import os
import pygame
from ui.button import Button


class HUD:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"

    def __init__(self, item_manager):
        self.item_manager = item_manager

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
    # HANDLE EVENT
    # ======================================================
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mx, my = event.pos

        # Toggle setting panel
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

        panel_w = int(320 * scale)
        panel_h = int(96 * scale)
        GAP = int(12 * scale)

        px = self.setting_rect.right + GAP
        py = self.setting_rect.centery - panel_h // 2

        px = max(GAP, min(px, sw - panel_w - GAP))
        py = max(GAP, min(py, sh - panel_h - GAP))

        panel_rect = pygame.Rect(px, py, panel_w, panel_h)

        board = pygame.transform.scale(self.board_img, (panel_w, panel_h))
        surf.blit(board, panel_rect.topleft)

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

        if not self.setting_buttons or self._last_setting_size != panel_rect.size:
            self.setting_buttons.clear()
            self.btn_rects.clear()
            self._last_setting_size = panel_rect.size

            for i, (name, icon) in enumerate(icons):
                img = pygame.transform.scale(icon, (icon_size, icon_size))

                target_x = start_x + i * (icon_size + gap) + icon_size // 2
                target_y = y + icon_size // 2

                btn = Button(
                    image=img,
                    offset=(target_x - panel_rect.centerx,
                            target_y - panel_rect.centery),
                    origin=panel_rect.center
                )

                btn.bounce_speed = 8.0
                btn.target_offset_y = 0

                self.setting_buttons[name] = btn

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

        self._draw_inventory(surf, scale)
        self._draw_settings_icon(surf, scale)

        if self.setting_open:
            self._draw_setting_panel(surf, scale)
