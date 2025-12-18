import pygame
from ui.button import Button


class QuestPanel:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"
    KEYS = ("A", "B", "C", "D")

    def __init__(self, quest_manager, skills, level_manager):
        self.qm = quest_manager
        self.skills = skills
        self.level_manager = level_manager

        self.visible = False
        self.failed = False
        self.hovered = None
        self.clicked = None
        self._last_panel_size = (0, 0)

        # ===== ASSETS =====
        self.board_src = pygame.image.load(
            "assets/Menu/Buttons/Board.png"
        ).convert_alpha()

        self.icons = {
            "close": pygame.image.load("assets/Menu/Buttons/Close.png").convert_alpha(),
            "home": pygame.image.load("assets/Menu/Buttons/Home.png").convert_alpha(),
            "restart": pygame.image.load("assets/Menu/Buttons/Restart.png").convert_alpha(),
            "levels": pygame.image.load("assets/Menu/Buttons/Levels.png").convert_alpha(),
        }

        # ===== RUNTIME =====
        self.board_img = None
        self.panel_rect = pygame.Rect(0, 0, 0, 0)

        self.close_rect = pygame.Rect(0, 0, 0, 0)

        self.action_buttons = {}   # Button objects
        self.action_rects = {}     # rect for click

        self.font = None
        self.title_font = None

    # ================= STATE =================
    def open(self):
        self.visible = True
        self.failed = False
        self.hovered = None
        self.clicked = None
        self.action_buttons.clear()

    def close(self):
        self.visible = False
        self.action_buttons.clear()

        # 🔥 QUAN TRỌNG: cho phép mở lại quest
        if self.level_manager and self.level_manager.checkpoint:
            self.level_manager.checkpoint.waiting_quest = False


    # ================= EVENT =================
    def handle_event(self, event):
        if not self.visible:
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        pos = event.pos

        if self.close_rect.collidepoint(pos):
            self.close()
            return

        if self.failed:
            for name, rect in self.action_rects.items():
                if rect.collidepoint(pos):
                    self.close()
                    if name == "restart":
                        self.level_manager.restart_level()
                    elif name == "levels":
                        self.level_manager.go_level_select()
                    elif name == "home":
                        self.level_manager.go_home()
            return

        if self.hovered is None:
            return

        key = self.KEYS[self.hovered]
        self.clicked = self.hovered

        if key == self.qm.answer():
            if self.qm.is_key():
                skill = self.qm.unlock_skill()
                if skill:
                    self.skills.unlock(skill)

            self.level_manager.on_quest_success()
            self.close()
        else:
            self.failed = True
            self.level_manager.item_manager.punish_random_type(0.1)

    # ================= DRAW =================
    def draw(self, surf):
        if not self.visible:
            return

        sw, sh = surf.get_size()
        scale = sh / self.BASE_H
        mx, my = pygame.mouse.get_pos()

        self._build_layout(sw, sh)

        # ===== OVERLAY (vẽ TRƯỚC) =====
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))

        # ===== BOARD =====
        surf.blit(self.board_img, self.panel_rect)

        self._draw_close(surf, mx, my)
        self._draw_title(surf)
        self._draw_answers(surf, mx, my)

        if self.failed:
            self._draw_fail_menu(surf)

    # ================= LAYOUT =================
    def _build_layout(self, sw, sh):
        target_w = int(sw * 0.9)
        ratio = target_w / self.board_src.get_width()
        target_h = int(self.board_src.get_height() * ratio)

        self.board_img = pygame.transform.scale(
            self.board_src, (target_w, target_h)
        )
        self.panel_rect = self.board_img.get_rect(center=(sw // 2, sh // 2))

        base = self.panel_rect.width
        self.title_font = pygame.font.Font(self.FONT_PATH, int(base * 0.02))
        self.font = pygame.font.Font(self.FONT_PATH, int(base * 0.018))

    # ================= UI =================
    def _draw_close(self, surf, mx, my):
        size = int(self.panel_rect.width * 0.045)
        icon = pygame.transform.scale(self.icons["close"], (size, size))

        self.close_rect = icon.get_rect(
            topright=(
                self.panel_rect.right - int(size * 0.8),
                self.panel_rect.top + int(size * 0.8)
            )
        )

        icon.set_alpha(200 if self.close_rect.collidepoint(mx, my) else 255)
        surf.blit(icon, self.close_rect)

    def _draw_title(self, surf):
        text = self.qm.text()
        if not text:
            return

        img = self.title_font.render(text, True, (255, 255, 255))
        bg = img.get_rect(
            midtop=(
                self.panel_rect.centerx,
                self.panel_rect.top + int(self.panel_rect.height * 0.22)
            )
        )
        bg.inflate_ip(28, 18)

        pygame.draw.rect(surf, (40, 40, 60), bg, border_radius=12)
        surf.blit(img, img.get_rect(center=bg.center))

    def _draw_answers(self, surf, mx, my):
        self.hovered = None

        cx = self.panel_rect.centerx
        top = self.panel_rect.top + int(self.panel_rect.height * 0.38)

        total_w = self.panel_rect.width * 0.7
        gap = total_w * 0.08
        col_w = (total_w - gap) / 2
        row_h = self.panel_rect.height * 0.18

        left = cx - gap / 2 - col_w
        right = cx + gap / 2

        correct = self.qm.answer()
        choices = self.qm.choices()

        for i, key in enumerate(self.KEYS):
            row, col = divmod(i, 2)
            x = left if col == 0 else right
            y = top + row * row_h
            rect = pygame.Rect(x, y, col_w, row_h)

            if not self.failed and rect.collidepoint(mx, my):
                self.hovered = i

            color = None
            if self.hovered == i and self.clicked is None:
                color = (80, 80, 100)
            elif self.clicked == i:
                color = (70, 160, 90) if key == correct else (170, 70, 70)

            if color:
                pygame.draw.rect(
                    surf,
                    color,
                    rect.inflate(-int(col_w * 0.06), -int(row_h * 0.35)),
                    border_radius=int(row_h * 0.25)
                )

            txt = self.font.render(
                f"[{key}] {choices.get(key, '')}", True, (255, 255, 255)
            )
            surf.blit(
                txt,
                (rect.x + int(col_w * 0.06),
                 rect.centery - txt.get_height() // 2)
            )

    # ================= FAIL MENU (BUTTON STYLE) =================
    def _draw_fail_menu(self, surf):
        cx = self.panel_rect.centerx
        cy = self.panel_rect.centery

        y = self.panel_rect.bottom - int(self.panel_rect.height * 0.2)

        size = int(self.panel_rect.width * 0.075)
        gap = int(size * 1.5)

        names = ("levels", "restart", "home")

        # 🔥 rebuild nếu chưa có hoặc panel đổi size
        if (
            not self.action_buttons
            or self._last_panel_size != self.panel_rect.size
        ):
            self.action_buttons.clear()
            self.action_rects.clear()
            self._last_panel_size = self.panel_rect.size

            for i, name in enumerate(names):
                img = pygame.transform.scale(
                    self.icons[name],
                    (size, size)
                )

                target_x = cx + (i - 1) * gap
                target_y = y

                btn = Button(
                    image=img,
                    anchor=("center", "center"),
                    offset=(target_x - cx, target_y - cy)
                )

                btn.bounce_speed = 8.0
                btn.target_offset_y = 0

                self.action_buttons[name] = btn

        # ===== DRAW =====
        for name, btn in self.action_buttons.items():
            btn.handle_hover()
            btn.update(1 / 60, surf)
            btn.draw(surf)
            self.action_rects[name] = btn.rect
