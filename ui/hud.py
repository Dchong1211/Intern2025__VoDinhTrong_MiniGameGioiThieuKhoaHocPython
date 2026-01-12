import os
import pygame

class HUD:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"

    def __init__(self, item_manager):
        self.item_manager = item_manager
        self.count_font = pygame.font.Font(self.FONT_PATH, 16)
        self.icons = self._load_icons()
        self.setting_icon = pygame.image.load("assets/Menu/Buttons/Settings.png").convert_alpha()
        self.setting_rect = None
        self.sound_on = True
        self.opened = False
        self.panel_t = 0.0
        self.speed = 5.0
        self.btn_size = 48
        self.gap = 12
        self.icon_home = pygame.image.load("assets/Menu/Buttons/Home.png").convert_alpha()
        self.icon_levels = pygame.image.load("assets/Menu/Buttons/Levels.png").convert_alpha()
        self.icon_restart = pygame.image.load("assets/Menu/Buttons/Restart.png").convert_alpha()
        self.icon_volume = pygame.image.load("assets/Menu/Buttons/Volume.png").convert_alpha()
        self.icon_unvolume = pygame.image.load("assets/Menu/Buttons/Unvolume.png").convert_alpha()
        self.btn_rects = {}

    def _load_icons(self):
        base = "assets/Items/Fruits"
        icons = {}
        if not os.path.exists(base):
            return icons
            
        for name in self.item_manager.count:
            path = os.path.join(base, f"{name}.png")
            if os.path.exists(path):
                sheet = pygame.image.load(path).convert_alpha()
                icons[name] = sheet.subsurface((0, 0, 32, 32))
        return icons

    def _scale(self, surf):
        return surf.get_height() / self.BASE_H

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mx, my = event.pos

        if self.setting_rect and self.setting_rect.collidepoint(mx, my):
            self.opened = not self.opened
            return None

        if self.panel_t <= 0:
            return None

        for name, rect in self.btn_rects.items():
            if rect.collidepoint(mx, my):
                if name == "SOUND":
                    return "TOGGLE_SOUND"
                return name
        return None

    def update(self, dt):
        if self.opened:
            self.panel_t = min(1.0, self.panel_t + self.speed * dt)
        else:
            self.panel_t = max(0.0, self.panel_t - self.speed * dt)

    def _draw_inventory(self, surf, scale, right_margin):
        sw, _ = surf.get_size()
        icon_size = int(48 * scale)
        
        start_x = sw - right_margin - int(60 * scale)
        y = int(40 * scale)

        items_to_draw = []
        for name, icon in self.icons.items():
            if self.item_manager.discovered.get(name):
                 items_to_draw.append((name, icon))
        
        current_x = start_x
        for name, icon in items_to_draw:
            count = self.item_manager.count.get(name, 0)
            text = self.count_font.render(str(count), True, (255, 255, 255))
            text = pygame.transform.scale(text, (int(text.get_width()*scale), int(text.get_height()*scale)))
            
            text_rect = text.get_rect(topright=(current_x, y + icon_size//4))
            surf.blit(text, text_rect)
            
            icon_scaled = pygame.transform.scale(icon, (icon_size, icon_size))
            icon_rect = icon_scaled.get_rect(topright=(text_rect.left - int(5*scale), y))
            surf.blit(icon_scaled, icon_rect)

            current_x = icon_rect.left - int(30 * scale)

    def _draw_settings(self, surf, scale):
        sw, sh = surf.get_size()
        size = int(self.btn_size * scale)
        gap = int(self.gap * scale)

        gx = int(16 * scale)
        gy = sh - size - int(16 * scale)

        gear = pygame.transform.scale(self.setting_icon, (size, size))
        surf.blit(gear, (gx, gy))
        self.setting_rect = pygame.Rect(gx, gy, size, size)

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
        extra_gap = int(8 * scale)
        x_origin = gx + size // 2
        y = gy

        for i, (name, icon) in enumerate(icons):
            x_target = gx + size + extra_gap + i * (size + gap)
            x = x_origin + (x_target - x_origin) * self.panel_t

            img = pygame.transform.scale(icon, (size, size))
            rect = pygame.Rect(int(x), y, size, size)

            surf.blit(img, rect)
            self.btn_rects[name] = rect

    def draw(self, surf, dt, right_margin=0):
        scale = self._scale(surf)
        self.update(dt)
        self._draw_inventory(surf, scale, right_margin)
        self._draw_settings(surf, scale)