import os
import math
import pygame

from level.scrolling_background import ScrollingBackground
from ui.button import Button


class LevelSelect:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"

    def __init__(self, save):
        self.save = save

        # ================= LEVEL DATA =================
        self.level_folder = "assets/Menu/Levels"
        self.level_icons = sorted(
            os.listdir(self.level_folder),
            key=lambda x: int(os.path.splitext(x)[0])
        )

        self.levels_per_page = 9
        self.current_page = 0
        self.total_pages = math.ceil(
            len(self.level_icons) / self.levels_per_page
        )

        # ================= ICON CACHE =================
        self.icon_cache = {
            name: pygame.image.load(
                os.path.join(self.level_folder, name)
            ).convert_alpha()
            for name in self.level_icons
        }

        # ================= BACKGROUND =================
        self.bg_folder = "assets/Background/Level"
        self.bg_files = [
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ]
        self.bg = None
        self.bg_size = (0, 0)

        # ================= RAW NAV IMAGES =================
        self.prev_raw = pygame.image.load(
            "assets/Menu/Buttons/Previous.png"
        ).convert_alpha()

        self.next_raw = pygame.image.load(
            "assets/Menu/Buttons/Next.png"
        ).convert_alpha()

        self.home_raw = pygame.image.load(
            "assets/Menu/Buttons/Home.png"
        ).convert_alpha()

        # ================= NAV BUTTONS =================
        self.btn_prev = Button(self.prev_raw, ("center", "bottom"), (0, 0))
        self.btn_next = Button(self.next_raw, ("center", "bottom"), (0, 0))
        self.btn_back = Button(self.home_raw, ("left", "top"), (0, 0))

        # ================= LEVEL BUTTONS =================
        self.level_buttons = []

        # ================= FONT =================
        self.font = pygame.font.Font(self.FONT_PATH, 20)

        # ================= RESIZE FLAG =================
        self.need_rebuild = True

    # =================================================
    def on_resize(self, screen):
        self.need_rebuild = True
        self.level_buttons.clear()
        self.bg_size = (0, 0)

        # reset bounce state
        for b in (self.btn_prev, self.btn_next, self.btn_back):
            b.offset_y = 0
            b.target_offset_y = 0
            b.update_layout(screen)

    # =================================================
    def _load_background(self, screen_size):
        if not self.bg_files:
            self.bg = None
            return

        sw, sh = screen_size
        self.bg_size = (sw, sh)

        bg = self.bg_files[self.current_page % len(self.bg_files)]
        self.bg = ScrollingBackground(
            os.path.join(self.bg_folder, bg),
            sw,
            sh,
            speed=0
        )

    # =================================================
    def _build_level_buttons(self, screen):
        self.level_buttons.clear()

        sw, sh = screen.get_size()
        scale = sh / self.BASE_H

        cols, rows = 3, 3
        icon_size = int(96 * scale)
        gap_x = int(60 * scale)
        gap_y = int(50 * scale)

        total_w = cols * icon_size + (cols - 1) * gap_x
        total_h = rows * icon_size + (rows - 1) * gap_y

        start_x = (sw - total_w) // 2
        start_y = (sh - total_h) // 2

        cx, cy = sw // 2, sh // 2

        start = self.current_page * self.levels_per_page
        visible = self.level_icons[start:start + self.levels_per_page]

        for i, name in enumerate(visible):
            row, col = divmod(i, cols)

            x = start_x + col * (icon_size + gap_x)
            y = start_y + row * (icon_size + gap_y)

            ox = x + icon_size // 2 - cx
            oy = y + icon_size // 2 - cy

            img = pygame.transform.scale(
                self.icon_cache[name],
                (icon_size, icon_size)
            )

            btn = Button(img, ("center", "center"), (ox, oy))
            btn.level_id = start + i + 1
            self.level_buttons.append(btn)

    # ================= EVENT ==========================
    def handle_event(self, event, screen):
        for b in (self.btn_prev, self.btn_next, self.btn_back):
            b.update_layout(screen)

        if self.btn_prev.handle_event(event):
            if self.current_page > 0:
                self.current_page -= 1
                self.need_rebuild = True
                self.level_buttons.clear()
                self._load_background(screen.get_size())

        if self.btn_next.handle_event(event):
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self.need_rebuild = True
                self.level_buttons.clear()
                self._load_background(screen.get_size())

        if self.btn_back.handle_event(event):
            return "BACK"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.level_buttons:
                if (
                    btn.rect.collidepoint(event.pos)
                    and self.save.is_level_unlocked(btn.level_id)
                ):
                    return btn.level_id

        return None

    # ================= UPDATE =========================
    def update(self, dt):
        if self.bg:
            self.bg.update(dt)

    # ================= DRAW ===========================
    def draw(self, screen, dt):
        sw, sh = screen.get_size()
        scale = sh / self.BASE_H

        # ===== BACKGROUND =====
        if self.bg is None or self.bg_size != (sw, sh):
            self._load_background((sw, sh))

        if self.bg:
            self.bg.draw(screen)
        else:
            screen.fill((25, 25, 30))

        # ===== SCALE NAV BUTTON IMAGES =====
        nav_w = int(48 * scale)
        nav_h = int(nav_w * self.prev_raw.get_height() / self.prev_raw.get_width())

        self.btn_prev.image = pygame.transform.scale(self.prev_raw, (nav_w, nav_h))
        self.btn_next.image = pygame.transform.scale(self.next_raw, (nav_w, nav_h))

        home_w = int(56 * scale)
        home_h = int(home_w * self.home_raw.get_height() / self.home_raw.get_width())
        self.btn_back.image = pygame.transform.scale(self.home_raw, (home_w, home_h))

        # ===== NAV OFFSETS (SCALE THEO MÀN HÌNH) =====
        x_gap = int(140 * scale)
        y_gap = int(60 * scale)

        self.btn_prev.base_offset = (-x_gap, -y_gap)
        self.btn_next.base_offset = ( x_gap, -y_gap)
        self.btn_back.base_offset = (int(40 * scale), int(40 * scale))

        # update layout sau khi set offset
        for b in (self.btn_prev, self.btn_next, self.btn_back):
            b.update_layout(screen)

        # ===== BUILD LEVEL BUTTONS =====
        if self.need_rebuild:
            self._build_level_buttons(screen)
            self.need_rebuild = False

        # ===== LEVEL ICONS =====
        for btn in self.level_buttons:
            unlocked = self.save.is_level_unlocked(btn.level_id)

            if unlocked:
                btn.handle_hover()
            else:
                btn.target_offset_y = 0

            btn.update(dt, screen)

            if unlocked:
                btn.draw(screen)
            else:
                locked = btn.image.copy()
                locked.fill(
                    (120, 120, 120, 80),
                    special_flags=pygame.BLEND_RGBA_SUB
                )
                screen.blit(locked, btn.rect)

        # ===== PAGE NUMBER (CĂN THEO PREV) =====
        self._draw_page_number(screen, scale)

        # ===== NAV BUTTONS =====
        for b in (self.btn_prev, self.btn_next, self.btn_back):
            b.handle_hover()
            b.update(dt, screen)
            b.draw(screen)

    # ================= PAGE ===========================
    def _draw_page_number(self, screen, scale):
        sw, sh = screen.get_size()

        font_size = int(20 * scale)
        font = pygame.font.Font(self.FONT_PATH, font_size)

        text = f"{self.current_page + 1} / {self.total_pages}"
        outline = font.render(text, True, (0, 0, 0))
        main = font.render(text, True, (255, 255, 255))

        y = self.btn_prev.rect.centery + int(2 * scale)
        cx = sw // 2

        screen.blit(outline, outline.get_rect(center=(cx + 2, y + 2)))
        screen.blit(main, main.get_rect(center=(cx, y)))
