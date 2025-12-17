import pygame


class QuestPanel:
    def __init__(self, quest_manager, skills, level_manager):
        self.qm = quest_manager
        self.skills = skills
        self.level_manager = level_manager

        self.visible = False
        self.hovered = -1
        self.clicked = -1
        self.failed = False

        self.keys = ["A", "B", "C", "D"]

        # ===== BOARD =====
        self.board_src = pygame.image.load(
            "assets/Menu/Buttons/Board.png"
        ).convert_alpha()
        self.board_img = self.board_src
        self.panel_rect = self.board_img.get_rect()

        # ===== ICONS =====
        self.icon_close = pygame.image.load(
            "assets/Menu/Buttons/Close.png"
        ).convert_alpha()
        self.icon_home = pygame.image.load(
            "assets/Menu/Buttons/Home.png"
        ).convert_alpha()
        self.icon_restart = pygame.image.load(
            "assets/Menu/Buttons/Restart.png"
        ).convert_alpha()
        self.icon_levels = pygame.image.load(
            "assets/Menu/Buttons/Levels.png"
        ).convert_alpha()

        # ===== SAFE RECT =====
        self.close_rect = pygame.Rect(0, 0, 0, 0)
        self.home_rect = pygame.Rect(0, 0, 0, 0)
        self.restart_rect = pygame.Rect(0, 0, 0, 0)
        self.levels_rect = pygame.Rect(0, 0, 0, 0)

        self.font = None
        self.title_font = None

    # ===============================
    def open(self):
        self.visible = True
        self.hovered = -1
        self.clicked = -1
        self.failed = False

    def close(self):
        self.visible = False

    # ===============================
    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # ❌ CLOSE
            if self.close_rect.collidepoint(event.pos):
                self.close()
                return

            # ===== FAIL MENU =====
            if self.failed:
                if self.restart_rect.collidepoint(event.pos):
                    self.close()
                    self.level_manager.restart_level()
                    return

                if self.levels_rect.collidepoint(event.pos):
                    self.close()
                    self.level_manager.go_level_select()
                    return

                if self.home_rect.collidepoint(event.pos):
                    self.close()
                    self.level_manager.go_home()
                    return

            # ===== CLICK ANSWER =====
            if self.hovered != -1 and self.clicked == -1:
                self.clicked = self.hovered

                # ✅ ĐÚNG
                if self.keys[self.clicked] == self.qm.answer():
                    if self.qm.is_key():
                        skill = self.qm.unlock_skill()
                        if skill:
                            self.skills.unlock(skill)

                    self.level_manager.on_quest_success()
                    self.close()

                # ❌ SAI → PHẠT
                else:
                    self.failed = True
                    self.level_manager.item_manager.punish_random_type(0.1)

    # ===============================
    def draw(self, surf):
        if not self.visible:
            return

        sw, sh = surf.get_size()
        mx, my = pygame.mouse.get_pos()
        self.hovered = -1

        # ===== SCALE BOARD =====
        target_w = int(sw * 0.9)
        scale = target_w / self.board_src.get_width()
        target_h = int(self.board_src.get_height() * scale)

        self.board_img = pygame.transform.smoothscale(
            self.board_src, (target_w, target_h)
        )
        self.panel_rect = self.board_img.get_rect(
            center=(sw // 2, sh // 2)
        )

        base = self.panel_rect.width

        self.title_font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf",
            max(14, int(base * 0.020))
        )
        self.font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf",
            max(13, int(base * 0.018))
        )

        # ===== OVERLAY =====
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        surf.blit(self.board_img, self.panel_rect.topleft)

        # =====================================================
        # ❌ CLOSE BUTTON – TOP RIGHT OF BOARD (FIXED & STABLE)
        # =====================================================
        size = int(base * 0.04)

        # offset theo tỉ lệ board (ổn khi F11)
        offset_x = int(base * 0.045)   # dịch vào trái
        offset_y = int(base * 0.05)   # dịch xuống

        close_img = pygame.transform.smoothscale(
            self.icon_close, (size, size)
        )

        self.close_rect = close_img.get_rect(
            topright=(
                self.panel_rect.right - offset_x,
                self.panel_rect.top + offset_y
            )
        )

        surf.blit(close_img, self.close_rect)


        # hover feedback
        if self.close_rect.collidepoint(mx, my):
            close_img.set_alpha(210)
        else:
            close_img.set_alpha(255)

        surf.blit(close_img, self.close_rect)

        # ===== TITLE =====
        title_text = self.qm.text()
        title_h = 0
        if title_text:
            title_img = self.title_font.render(
                title_text, True, (255, 255, 255)
            )

            pad = int(base * 0.015)
            bg = title_img.get_rect(
                midtop=(
                    self.panel_rect.centerx,
                    self.panel_rect.y + self.panel_rect.height * 0.22
                )
            )
            bg.inflate_ip(pad * 2, pad * 2)

            pygame.draw.rect(
                surf, (40, 40, 60), bg, border_radius=10
            )
            surf.blit(
                title_img,
                title_img.get_rect(center=bg.center)
            )
            title_h = bg.height

        # ===== ANSWERS =====
        center_x = self.panel_rect.centerx
        top_y = (
            self.panel_rect.y
            + self.panel_rect.height * 0.35
            + title_h * 0.3
        )

        total_w = self.panel_rect.width * 0.7
        gap = total_w * 0.08
        col_w = (total_w - gap) / 2
        row_h = self.panel_rect.height * 0.18

        left_x = center_x - gap / 2 - col_w
        right_x = center_x + gap / 2

        correct = self.qm.answer()
        choices = self.qm.choices()

        for i, key in enumerate(self.keys):
            row = i // 2
            col = i % 2
            x = left_x if col == 0 else right_x
            y = top_y + row * row_h
            rect = pygame.Rect(x, y, col_w, row_h)

            if not self.failed and rect.collidepoint(mx, my):
                self.hovered = i

            color = None
            if self.hovered == i and self.clicked == -1:
                color = (80, 80, 100)
            if self.clicked == i:
                color = (
                    (70, 160, 90)
                    if key == correct
                    else (170, 70, 70)
                )

            if color:
                pygame.draw.rect(
                    surf,
                    color,
                    rect.inflate(
                        -int(col_w * 0.06),
                        -int(row_h * 0.35)
                    ),
                    border_radius=int(row_h * 0.25)
                )

            txt = self.font.render(
                f"[{key}] {choices.get(key, '')}",
                True,
                (255, 255, 255)
            )
            surf.blit(
                txt,
                (
                    rect.x + int(col_w * 0.06),
                    rect.y + (rect.height - txt.get_height()) // 2
                )
            )

        if self.failed:
            self._draw_fail_menu(surf)

    # ===============================
    def _draw_fail_menu(self, surf):
        cx = self.panel_rect.centerx
        y = self.panel_rect.bottom - self.panel_rect.height * 0.26
        size = int(self.panel_rect.width * 0.08)
        gap = size * 0.7

        # 🗺️ LEVEL SELECT
        self.levels_rect = pygame.Rect(
            cx - size - gap, y, size, size
        )
        surf.blit(
            pygame.transform.scale(self.icon_levels, (size, size)),
            self.levels_rect
        )

        # 🔁 RESTART
        self.restart_rect = pygame.Rect(
            cx - size // 2, y, size, size
        )
        surf.blit(
            pygame.transform.scale(self.icon_restart, (size, size)),
            self.restart_rect
        )

        # 🏠 HOME
        self.home_rect = pygame.Rect(
            cx + gap, y, size, size
        )
        surf.blit(
            pygame.transform.scale(self.icon_home, (size, size)),
            self.home_rect
        )
