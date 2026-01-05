import pygame
import json


class CodePanel:
    def __init__(self, screen_w, screen_h):
        # ================= SIZE =================
        self.base_width = 360
        self.base_height = 720

        self.scale = screen_h / self.base_height
        self.width = int(self.base_width * self.scale)
        self.height = screen_h

        self.hidden_x = screen_w
        self.visible_x = screen_w - self.width
        self.x = self.hidden_x
        self.target_x = self.hidden_x
        self.speed = 1600
        self.opened = False

        # ================= SURFACE =================
        self.surface = pygame.Surface(
            (self.base_width, self.base_height), pygame.SRCALPHA
        )

        # ================= FONT =================
        self.font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 15)
        self.title_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 22)
        self.code_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 15)

        self.line_h = self.code_font.get_height() + 6

        # ================= DATA =================
        self.title = ""
        self.instructions = []
        self.hints = []

        # ================= EDITOR =================
        self.code_lines = [""]
        self.cursor_line = 0
        self.cursor_col = 0

        self.scroll = 0
        self.cursor_timer = 0
        self.cursor_visible = True

        # ================= BUTTON =================
        self.btn_size = 48
        self.btn_open_img = pygame.transform.scale(
            pygame.image.load("assets/Menu/Buttons/Show.png").convert_alpha(),
            (48, 48),
        )
        self.btn_close_img = pygame.transform.scale(
            pygame.image.load("assets/Menu/Buttons/Hide.png").convert_alpha(),
            (48, 48),
        )
        self.btn_rect = pygame.Rect(0, 0, 48, 48)

        self.run_img = pygame.transform.scale(
            pygame.image.load("assets/Menu/Buttons/Run.png").convert_alpha(),
            (160, 56),
        )
        self.run_rect = pygame.Rect(0, 0, 160, 56)

    # ================= LOAD JSON =================
    def load_from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.title = data.get("title", "")
        self.instructions = data.get("instruction", [])
        self.hints = data.get("hint", [])
        self.code_lines = data.get("solution", [""])

        self.cursor_line = len(self.code_lines) - 1
        self.cursor_col = len(self.code_lines[-1])
        self.scroll = 0

    # ================= TOGGLE =================
    def open(self):
        self.opened = True
        self.target_x = self.visible_x

    def close(self):
        self.opened = False
        self.target_x = self.hidden_x

    def toggle(self):
        self.open() if not self.opened else self.close()

    # ================= INPUT =================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(event.pos):
                self.toggle()

            mx, my = event.pos
            local_x = int((mx - self.x) / self.scale)
            local_y = int(my / self.scale)

            if self.run_rect.collidepoint((local_x, local_y)):
                return [l for l in self.code_lines if l.strip()]

        if event.type == pygame.KEYDOWN and self.opened:
            self._handle_key(event)

        return None

    def _handle_key(self, event):
        line = self.code_lines[self.cursor_line]

        if event.key == pygame.K_BACKSPACE:
            if self.cursor_col > 0:
                self.code_lines[self.cursor_line] = (
                    line[: self.cursor_col - 1] + line[self.cursor_col :]
                )
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                prev = self.code_lines[self.cursor_line - 1]
                self.cursor_col = len(prev)
                self.code_lines[self.cursor_line - 1] = prev + line
                self.code_lines.pop(self.cursor_line)
                self.cursor_line -= 1

        elif event.key == pygame.K_RETURN:
            new = line[self.cursor_col :]
            self.code_lines[self.cursor_line] = line[: self.cursor_col]
            self.code_lines.insert(self.cursor_line + 1, new)
            self.cursor_line += 1
            self.cursor_col = 0

        elif event.key == pygame.K_LEFT:
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = len(self.code_lines[self.cursor_line])

        elif event.key == pygame.K_RIGHT:
            if self.cursor_col < len(line):
                self.cursor_col += 1
            elif self.cursor_line < len(self.code_lines) - 1:
                self.cursor_line += 1
                self.cursor_col = 0

        elif event.key == pygame.K_UP:
            if self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = min(
                    self.cursor_col, len(self.code_lines[self.cursor_line])
                )

        elif event.key == pygame.K_DOWN:
            if self.cursor_line < len(self.code_lines) - 1:
                self.cursor_line += 1
                self.cursor_col = min(
                    self.cursor_col, len(self.code_lines[self.cursor_line])
                )

        elif event.unicode and event.unicode.isprintable():
            self.code_lines[self.cursor_line] = (
                line[: self.cursor_col] + event.unicode + line[self.cursor_col :]
            )
            self.cursor_col += 1

    # ================= UPDATE =================
    def update(self, dt):
        if self.x < self.target_x:
            self.x = min(self.target_x, self.x + self.speed * dt)
        elif self.x > self.target_x:
            self.x = max(self.target_x, self.x - self.speed * dt)

        self.btn_rect.x = int(self.x - self.btn_size)
        self.btn_rect.y = self.height // 2 - self.btn_size // 2

        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        self.run_rect.centerx = self.base_width // 2
        self.run_rect.bottom = self.base_height - 16

    # ================= TEXT WRAP =================
    def wrap_line(self, text, max_width):
        lines = []
        current = ""

        for ch in text:
            if self.code_font.size(current + ch)[0] <= max_width:
                current += ch
            else:
                lines.append(current)
                current = ch

        lines.append(current)
        return lines

    def wrap_text(self, text, font, max_width):
        lines = []
        current = ""

        for ch in text:
            if font.size(current + ch)[0] <= max_width:
                current += ch
            else:
                lines.append(current)
                current = ch

        lines.append(current)
        return lines

    # ================= DRAW =================
    def draw(self, screen):
        self.surface.fill((25, 25, 35))

        x = 20
        y = 20
        max_w = self.base_width - 40

        # ===== TITLE =====
        max_text_w = self.base_width - 40

        title_lines = self.wrap_text(
            self.title.upper(),
            self.title_font,
            max_text_w
        )

        for line in title_lines:
            txt = self.title_font.render(line, True, (255, 220, 120))
            self.surface.blit(txt, (x, y))
            y += txt.get_height() + 4

        y += 6


        instruction_x = x + 6
        instruction_max_w = self.base_width - instruction_x - 20

        for ins in self.instructions:
            wrapped_lines = self.wrap_text(
                "- " + ins,
                self.font,
                instruction_max_w
            )

            for line in wrapped_lines:
                txt = self.font.render(line, True, (220, 220, 230))
                self.surface.blit(txt, (instruction_x, y))
                y += txt.get_height() + 2

            y += 4


        # ===== EDITOR RECT =====
        editor_y = y + 8
        editor_h = self.base_height - editor_y - 90
        editor = pygame.Rect(x, editor_y, max_w, editor_h)
        pygame.draw.rect(self.surface, (50, 50, 70), editor, border_radius=6)

        padding_x = 8
        padding_y = 6
        max_text_w = editor.width - padding_x * 2

        # ===== BUILD VISUAL LINES =====
        visual_lines = []
        cursor_vy = 0
        cursor_vx = 0

        for li, line in enumerate(self.code_lines):
            wrapped = self.wrap_line(line, max_text_w)
            remaining = self.cursor_col

            for w in wrapped:
                visual_lines.append((li, w))

                if li == self.cursor_line:
                    if remaining <= len(w):
                        cursor_vy = len(visual_lines) - 1
                        cursor_vx = self.code_font.size(w[:remaining])[0]
                    remaining -= len(w)

        visible_lines = editor_h // self.line_h

        if cursor_vy < self.scroll:
            self.scroll = cursor_vy
        elif cursor_vy >= self.scroll + visible_lines:
            self.scroll = cursor_vy - visible_lines + 1

        self.scroll = max(0, min(self.scroll, len(visual_lines) - visible_lines))

        clip = self.surface.get_clip()
        self.surface.set_clip(editor)

        cy = editor_y + padding_y
        for i in range(self.scroll, min(self.scroll + visible_lines, len(visual_lines))):
            _, text = visual_lines[i]
            self.surface.blit(
                self.code_font.render(text, True, (150, 255, 150)),
                (x + padding_x, cy),
            )

            if i == cursor_vy and self.cursor_visible:
                cx = x + padding_x + cursor_vx
                pygame.draw.line(
                    self.surface,
                    (255, 255, 255),
                    (cx, cy),
                    (cx, cy + self.code_font.get_height()),
                )

            cy += self.line_h

        self.surface.set_clip(clip)

        # ===== RUN BUTTON =====
        self.surface.blit(self.run_img, self.run_rect)

        scaled = pygame.transform.scale(self.surface, (self.width, self.height))
        screen.blit(scaled, (int(self.x), 0))

        screen.blit(
            self.btn_close_img if self.opened else self.btn_open_img, self.btn_rect
        )
