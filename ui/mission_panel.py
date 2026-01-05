import pygame


class MissionPanel:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf"

    def __init__(self, screen_w, objective, icons):
        self.screen_w = screen_w
        self.objective = objective
        self.icons = icons

        # ===== SIZE =====
        self.width = 300
        self.height = 120  # sẽ recalc

        # ===== SLIDE LEFT → RIGHT =====
        self.hidden_x = -self.width
        self.visible_x = 0

        self.x = self.hidden_x
        self.target_x = self.hidden_x

        self.speed = 1600
        self.opened = False

        # ===== FONT =====
        self.font_title = pygame.font.Font(self.FONT_PATH, 18)
        self.font_item = pygame.font.Font(self.FONT_PATH, 14)

        # ===== TOGGLE BUTTON =====
        self.btn_size = 40
        self.btn_rect = pygame.Rect(0, 0, self.btn_size, self.btn_size)

        self.btn_show = pygame.transform.scale(
            pygame.image.load("assets/Menu/Buttons/Show.png").convert_alpha(),
            (self.btn_size, self.btn_size)
        )
        self.btn_hide = pygame.transform.scale(
            pygame.image.load("assets/Menu/Buttons/Hide.png").convert_alpha(),
            (self.btn_size, self.btn_size)
        )

        self.recalc_height()

    # ==================================================
    # CONTROL
    # ==================================================
    def open(self):
        self.opened = True
        self.target_x = self.visible_x

    def close(self):
        self.opened = False
        self.target_x = self.hidden_x

    def toggle(self):
        self.open() if not self.opened else self.close()

    # ==================================================
    # EVENT
    # ==================================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_rect.collidepoint(event.pos):
                self.toggle()

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, dt):
        if self.x < self.target_x:
            self.x = min(self.target_x, self.x + self.speed * dt)
        elif self.x > self.target_x:
            self.x = max(self.target_x, self.x - self.speed * dt)

        # toggle button nằm giữa panel
        self.btn_rect.x = int(self.x + self.width)
        self.btn_rect.y = int(self.height // 2 - self.btn_size // 2)

    # ==================================================
    # SIZE
    # ==================================================
    def recalc_height(self):
        if not self.objective or not self.objective.objectives:
            self.height = 120
            return

        pad = 14
        gap = 8
        icon_size = 36

        title_h = self.font_title.get_height()
        item_h = max(self.font_item.get_height(), icon_size)

        self.height = (
            pad * 2
            + title_h
            + gap
            + len(self.objective.objectives) * (item_h + gap)
        )

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self, screen):
        if not self.objective or not self.objective.objectives:
            return

        pad = 14
        gap = 8
        icon_size = 36
        y = pad

        panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))

        # ===== TITLE =====
        title = self.font_title.render("MISSION", True, (255, 220, 120))
        panel.blit(
            title,
            ((self.width - title.get_width()) // 2, y)
        )
        y += title.get_height() + gap

        # ===== OBJECTIVES =====
        for name, data in self.objective.objectives.items():
            done = data["collected"] >= data["required"]
            color = (0, 220, 0) if done else (255, 255, 255)

            # TEXT NAME (TRÁI)
            name_text = self.font_item.render(name, True, color)
            panel.blit(name_text, (pad, y))

            # ICON + COUNT (PHẢI – CÙNG HÀNG)
            if name in self.icons:
                icon = pygame.transform.scale(
                    self.icons[name], (icon_size, icon_size)
                )

                right_x = self.width - pad - icon_size
                panel.blit(icon, (right_x, y))

                count_text = self.font_item.render(
                    f"{data['collected']}/{data['required']}",
                    True,
                    color
                )

                panel.blit(
                    count_text,
                    (
                        right_x - count_text.get_width() - 6,
                        y + (icon_size - count_text.get_height()) // 2
                    )
                )

            y += max(icon_size, name_text.get_height()) + gap

        # ===== BLIT PANEL =====
        screen.blit(panel, (int(self.x), 0))

        # ===== TOGGLE BUTTON =====
        screen.blit(
            self.btn_hide if self.opened else self.btn_show,
            self.btn_rect
        )
