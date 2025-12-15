import pygame
import os

class LevelSelect:
    def __init__(self, progress):
        self.progress = progress

        self.bg = pygame.image.load(
            "assets\Background\Background_select_level.png"
        ).convert()

        self.level_folder = "assets/Menu/Levels"
        self.level_icons = sorted(os.listdir(self.level_folder))

        self.levels_per_page = 6
        self.current_page = 0

        self.icon_size = 96
        self.start_y = 220
        self.start_x = 320
        self.gap_x = 240
        self.gap_y = 140

    def update(self, screen):
        sw, sh = screen.get_size()

        # ===== BACKGROUND MENU =====
        screen.blit(
            pygame.transform.scale(self.bg, (sw, sh)),
            (0, 0)
        )

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        cols = 3
        rows = 2
        icon_size = 96
        gap_x = 80
        gap_y = 60

        total_width = cols * icon_size + (cols - 1) * gap_x
        total_height = rows * icon_size + (rows - 1) * gap_y

        start_x = (sw - total_width) // 2
        start_y = (sh - total_height) // 2

        start = self.current_page * self.levels_per_page
        end = start + self.levels_per_page
        visible = self.level_icons[start:end]

        selected_level = None

        for i, icon_name in enumerate(visible):
            level_number = start + i + 1

            row = i // cols
            col = i % cols

            x = start_x + col * (icon_size + gap_x)
            y = start_y + row * (icon_size + gap_y)

            icon = pygame.image.load(
                os.path.join(self.level_folder, icon_name)
            ).convert_alpha()

            icon = pygame.transform.scale(icon, (icon_size, icon_size))
            rect = icon.get_rect(topleft=(x, y))

            unlocked = self.progress.is_unlocked(level_number)

            if unlocked:
                screen.blit(icon, rect)
                if rect.collidepoint(mouse_pos) and mouse_click:
                    selected_level = level_number
            else:
                dark = icon.copy()
                dark.fill((0, 0, 0, 150), special_flags=pygame.BLEND_RGBA_SUB)
                screen.blit(dark, rect)

        return selected_level
