import os
import pygame


class HUD:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"

    def __init__(self, item_manager):
        self.item_manager = item_manager

        # ===== INVENTORY =====
        self.icons = self._load_icons()

        # ===== SETTINGS ICON =====
        self.setting_icon = pygame.image.load(
            "assets/Menu/Buttons/Settings.png"
        ).convert_alpha()

        self.setting_rect = None

        # ===== SOUND STATE (sync từ main) =====
        self.sound_on = True

        # ===== SLIDE PANEL STATE =====
        self.opened = False
        self.panel_t = 0.0          # 0 = đóng, 1 = mở
        self.speed = 5.0            # tốc độ trượt (giống CodePanel)

        # ===== SETTINGS ICON SIZE =====
        self.btn_size = 48
        self.gap = 12

        # ===== ICONS =====
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
    # LOAD INVENTORY ICONS
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

    # ======================================================
    # INPUT
    # ======================================================
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mx, my = event.pos

        # ⚙ Toggle settings
        if self.setting_rect and self.setting_rect.collidepoint(mx, my):
            self.opened = not self.opened
            return None

        # Nếu panel đang đóng → không xử lý icon khác
        if self.panel_t <= 0:
            return None

        for name, rect in self.btn_rects.items():
            if rect.collidepoint(mx, my):
                if name == "SOUND":
                    return "TOGGLE_SOUND"
                return name

        return None

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, dt):
        if self.opened:
            self.panel_t = min(1.0, self.panel_t + self.speed * dt)
        else:
            self.panel_t = max(0.0, self.panel_t - self.speed * dt)

    # ======================================================
    # DRAW INVENTORY
    # ======================================================
    def _draw_inventory(self, surf, scale):
        sw, _ = surf.get_size()

        size = int(56 * scale)
        spacing = int(92 * scale)

        x = sw - int(70 * scale)
        y = int(42 * scale)

        for name, icon in self.icons.items():
            if not self.item_manager.discovered.get(name):
                continue

            icon_scaled = pygame.transform.scale(icon, (size, size))
            rect = icon_scaled.get_rect(topright=(x, y))
            surf.blit(icon_scaled, rect)

            x -= spacing

    # ======================================================
    # DRAW SETTINGS (SLIDE)
    # ======================================================
    def _draw_settings(self, surf, scale):
        sw, sh = surf.get_size()
        size = int(self.btn_size * scale)
        gap = int(self.gap * scale)

        # ⚙ SETTING ICON (LUÔN LUÔN HIỆN)
        gx = int(16 * scale)
        gy = sh - size - int(16 * scale)

        gear = pygame.transform.scale(self.setting_icon, (size, size))
        surf.blit(gear, (gx, gy))
        self.setting_rect = pygame.Rect(gx, gy, size, size)

        # Nếu panel đóng hoàn toàn → không vẽ icon khác
        if self.panel_t <= 0:
            self.btn_rects.clear()
            return

        icons = [
            ("HOME", self.icon_home),
            ("LEVEL", self.icon_levels),
            ("RESTART", self.icon_restart),
            ("SOUND", self.icon_volume if self.sound_on else self.icon_unvolume),
        ]

        self.btn_rects.clear()

        EXTRA_GAP = int(8 * scale)   # khoảng cách thêm
        # Điểm gốc: ngay trên nút setting
        x_origin = gx + size // 2
        y = gy

        for i, (name, icon) in enumerate(icons):
            x_target = gx + size + EXTRA_GAP + i * (size + gap)

            # 🔥 LERP ĐÚNG: từ ⚙ → vị trí icon
            x = x_origin + (x_target - x_origin) * self.panel_t

            img = pygame.transform.scale(icon, (size, size))
            rect = pygame.Rect(int(x), y, size, size)

            surf.blit(img, rect)
            self.btn_rects[name] = rect


    # ======================================================
    # MAIN DRAW
    # ======================================================
    def draw(self, surf, dt):
        scale = self._scale(surf)

        self.update(dt)
        self._draw_inventory(surf, scale)
        self._draw_settings(surf, scale)
