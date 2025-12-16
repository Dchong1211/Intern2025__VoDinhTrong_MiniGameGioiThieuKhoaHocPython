import pygame
import os
import math

from level.scrolling_background import ScrollingBackground


class LevelSelect:
    def __init__(self, save):
        self.save = save

        # ================= LEVEL ICON =================
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

        # ================= BACKGROUND =================
        self.bg_folder = "assets/Background/Level"
        self.bg_files = sorted([
            f for f in os.listdir(self.bg_folder)
            if f.endswith(".png")
        ])

        self.bg = None
        self.load_bg_for_page()

        # ================= BUTTON PREV / NEXT =================
        self.btn_size = 64

        self.btn_prev = pygame.image.load(
            "assets/Menu/Buttons/Previous.png"
        ).convert_alpha()
        self.btn_prev = pygame.transform.scale(
            self.btn_prev, (self.btn_size, self.btn_size)
        )

        self.btn_next = pygame.image.load(
            "assets/Menu/Buttons/Next.png"
        ).convert_alpha()
        self.btn_next = pygame.transform.scale(
            self.btn_next, (self.btn_size, self.btn_size)
        )

        # ================= BACK BUTTON =================
        self.btn_back = pygame.image.load(
            "assets/Menu/Buttons/Back.png"
        ).convert_alpha()
        self.btn_back = pygame.transform.scale(
            self.btn_back, (64, 64)
        )

        # ================= GRID =================
        self.icon_size = 96
        self.gap_x = 60
        self.gap_y = 50

        # ================= PAGE FONT =================
        self.page_font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 20
        )

    # ==================================================
    def load_bg_for_page(self):
        if not self.bg_files:
            self.bg = None
            return

        index = self.current_page % len(self.bg_files)
        bg_name = self.bg_files[index]
        bg_path = os.path.join(self.bg_folder, bg_name)

        self.bg = ScrollingBackground(
            bg_path,
            map_w=4000,
            map_h=4000,
            speed=0  # KHÔNG SCROLL
        )

    # ==================================================
    def update(self, screen):
        sw, sh = screen.get_size()

        # ================= BACKGROUND =================
        if self.bg:
            self.bg.draw(screen)
        else:
            screen.fill((25, 25, 30))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        # ================= GRID CONFIG =================
        cols = 3
        rows = 3

        total_w = cols * self.icon_size + (cols - 1) * self.gap_x
        total_h = rows * self.icon_size + (rows - 1) * self.gap_y

        start_x = (sw - total_w) // 2
        start_y = (sh - total_h) // 2

        start = self.current_page * self.levels_per_page
        end = start + self.levels_per_page
        visible = self.level_icons[start:end]

        selected_level = None

        # ================= LEVEL ICON =================
        for i, icon_name in enumerate(visible):
            level_number = start + i + 1

            row = i // cols
            col = i % cols

            x = start_x + col * (self.icon_size + self.gap_x)
            y = start_y + row * (self.icon_size + self.gap_y)

            icon = pygame.image.load(
                os.path.join(self.level_folder, icon_name)
            ).convert_alpha()

            icon = pygame.transform.scale(
                icon, (self.icon_size, self.icon_size)
            )

            rect = icon.get_rect(topleft=(x, y))

            unlocked = self.save.is_level_unlocked(level_number)

            if unlocked:
                screen.blit(icon, rect)
                if rect.collidepoint(mouse_pos) and mouse_click:
                    selected_level = level_number
            else:
                locked = icon.copy()
                locked.fill(
                    (0, 0, 0, 180),
                    special_flags=pygame.BLEND_RGBA_SUB
                )
                screen.blit(locked, rect)

        # ================= BUTTON PREV / NEXT =================
        btn_y = sh - 90  # ĐẨY LÊN CAO HƠN CHO KHỎI CHÌM

        if self.current_page > 0:
            prev_rect = self.btn_prev.get_rect(
                center=(sw // 2 - 150, btn_y)
            )
            screen.blit(self.btn_prev, prev_rect)

            if prev_rect.collidepoint(mouse_pos) and mouse_click:
                self.current_page -= 1
                self.load_bg_for_page()
                pygame.time.delay(150)

        if self.current_page < self.total_pages - 1:
            next_rect = self.btn_next.get_rect(
                center=(sw // 2 + 150, btn_y)
            )
            screen.blit(self.btn_next, next_rect)

            if next_rect.collidepoint(mouse_pos) and mouse_click:
                self.current_page += 1
                self.load_bg_for_page()
                pygame.time.delay(150)

        # ================= PAGE NUMBER (KHÔNG CHÌM) =================
        page_text = f"{self.current_page + 1} / {self.total_pages}"

        # viền
        outline = self.page_font.render(
            page_text, True, (0, 0, 0)
        )
        outline_rect = outline.get_rect(
            center=(sw // 2 + 2, btn_y + 2)
        )
        screen.blit(outline, outline_rect)

        # chữ chính
        text = self.page_font.render(
            page_text, True, (255, 255, 255)
        )
        text_rect = text.get_rect(
            center=(sw // 2, btn_y)
        )
        screen.blit(text, text_rect)

        # ================= BACK BUTTON =================
        back_rect = self.btn_back.get_rect(
            topleft=(30, 30)
        )
        screen.blit(self.btn_back, back_rect)

        if back_rect.collidepoint(mouse_pos) and mouse_click:
            pygame.time.delay(150)
            return "BACK"

        return selected_level
