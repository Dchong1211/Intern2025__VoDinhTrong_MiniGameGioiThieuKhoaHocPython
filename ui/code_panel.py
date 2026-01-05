import pygame
import json


class CodePanel:
    def __init__(self, screen_w, screen_h):
        # ================= BASE SIZE (DESIGN SIZE) =================
        self.base_width = 360
        self.base_height = 720

        # ================= RUNTIME SIZE =================
        self.scale = screen_h / self.base_height
        self.width = int(self.base_width * self.scale)
        self.height = screen_h

        self.hidden_x = screen_w
        self.visible_x = screen_w - self.width

        self.x = self.hidden_x
        self.y = 0
        self.target_x = self.hidden_x

        self.speed = 1600
        self.opened = False

        # ================= SURFACE =================
        self.surface = pygame.Surface(
            (self.base_width, self.base_height),
            pygame.SRCALPHA
        )

        # ================= FONT (BASE SIZE) =================
        self.font_base = 18
        self.title_font_base = 26

        self.font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf",
            self.font_base
        )
        self.title_font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf",
            self.title_font_base
        )

        # ================= DATA =================
        self.title = "CODE MISSION"
        self.instructions = []
        self.hints = []
        self.code_lines = []

        # ================= BUTTON: TOGGLE =================
        self.btn_open_img = pygame.image.load(
            "assets/Menu/Buttons/Show.png"
        ).convert_alpha()
        self.btn_close_img = pygame.image.load(
            "assets/Menu/Buttons/Hide.png"
        ).convert_alpha()

        self.btn_open_img = pygame.transform.scale(
            self.btn_open_img, (48, 48)
        )
        self.btn_close_img = pygame.transform.scale(
            self.btn_close_img, (48, 48)
        )

        self.btn_size = 48
        self.btn_rect = pygame.Rect(0, 0, 48, 48)

        # ================= BUTTON: RUN =================
        self.run_img = pygame.image.load(
            "assets/Menu/Buttons/Run.png"
        ).convert_alpha()

        self.run_img = pygame.transform.scale(
            self.run_img, (160, 56)
        )

        self.run_rect = pygame.Rect(0, 0, 160, 56)

    # ==================================================
    # ================= RESIZE =========================
    # ==================================================

    def on_resize(self, screen_w, screen_h):
        self.scale = screen_h / self.base_height
        self.width = int(self.base_width * self.scale)
        self.height = screen_h

        self.hidden_x = screen_w
        self.visible_x = screen_w - self.width

        if self.opened:
            self.x = self.visible_x
            self.target_x = self.visible_x
        else:
            self.x = self.hidden_x
            self.target_x = self.hidden_x

    # ==================================================
    # ================= LOAD JSON ======================
    # ==================================================

    def load_from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.title = data.get("title", "")
        self.instructions = data.get("instruction", [])
        self.hints = data.get("hint", [])
        self.code_lines = data.get("solution", [])

    # ==================================================
    # ================= TOGGLE =========================
    # ==================================================

    def toggle(self):
        if self.opened:
            self.close()
        else:
            self.open()
        
    def open(self):
        self.opened = True
        self.target_x = self.visible_x

    def close(self):
        self.opened = False
        self.target_x = self.hidden_x


    # ==================================================
    # ================= UPDATE =========================
    # ==================================================

    def update(self, dt):
        if self.x < self.target_x:
            self.x = min(self.target_x, self.x + self.speed * dt)
        elif self.x > self.target_x:
            self.x = max(self.target_x, self.x - self.speed * dt)

        self.btn_rect.y = self.height // 2 - self.btn_size // 2
        self.btn_rect.x = int(self.x - self.btn_size)

        self.run_rect.centerx = self.base_width // 2
        self.run_rect.bottom = self.base_height - 20

    # ==================================================
    # ================= EVENT ==========================
    # ==================================================

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(event.pos):
                self.toggle()

            # RUN button
            mx, my = event.pos
            local_x = int((mx - self.x) / self.scale)
            local_y = int(my / self.scale)

            if self.run_rect.collidepoint((local_x, local_y)):
                return "RUN"

        return None

    # ==================================================
    # ================= TEXT WRAP ======================
    # ==================================================

    def draw_wrapped(self, surf, font, text, x, y, max_w, color, line_h):
        words = text.split(" ")
        line = ""

        for word in words:
            test = line + word + " "
            if font.size(test)[0] <= max_w:
                line = test
            else:
                surf.blit(font.render(line, True, color), (x, y))
                y += line_h
                line = word + " "

        if line:
            surf.blit(font.render(line, True, color), (x, y))
            y += line_h

        return y

    # ==================================================
    # ================= DRAW ===========================
    # ==================================================

    def draw(self, screen):
        self.surface.fill((30, 30, 40))
        pygame.draw.rect(
            self.surface, (120, 120, 140),
            (0, 0, self.base_width, self.base_height), 2
        )

        x = 20
        y = 20
        max_w = self.base_width - 40

        # TITLE
        y = self.draw_wrapped(
            self.surface,
            self.title_font,
            self.title.upper(),
            x, y, max_w,
            (255, 220, 120),
            32
        )

        y += 6

        # MISSION
        self.surface.blit(
            self.font.render("MISSION", True, (180, 180, 200)),
            (x, y)
        )
        y += 22

        for line in self.instructions:
            y = self.draw_wrapped(
                self.surface,
                self.font,
                "- " + line,
                x + 10, y,
                max_w - 10,
                (230, 230, 235),
                22
            )

        # HINT
        if self.hints:
            y += 8
            self.surface.blit(
                self.font.render("HINT", True, (180, 180, 200)),
                (x, y)
            )
            y += 22

            for line in self.hints:
                y = self.draw_wrapped(
                    self.surface,
                    self.font,
                    "* " + line,
                    x + 10, y,
                    max_w - 10,
                    (200, 220, 255),
                    22
                )

        # CODE
        y += 10
        self.surface.blit(
            self.font.render("CODE", True, (180, 180, 200)),
            (x, y)
        )
        y += 22

        for line in self.code_lines:
            y = self.draw_wrapped(
                self.surface,
                self.font,
                line,
                x + 10, y,
                max_w - 10,
                (150, 255, 150),
                22
            )

        # RUN BUTTON
        self.surface.blit(self.run_img, self.run_rect)

        # ===== SCALE + BLIT =====
        scaled = pygame.transform.scale(
            self.surface,
            (self.width, self.height)
        )

        screen.blit(scaled, (int(self.x), 0))

        # TOGGLE BUTTON
        screen.blit(
            self.btn_close_img if self.opened else self.btn_open_img,
            self.btn_rect
        )
