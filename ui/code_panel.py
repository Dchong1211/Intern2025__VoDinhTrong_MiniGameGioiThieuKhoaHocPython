import pygame
import json

from ui.ui_text import UITextLayout
from ui.code_editor import CodeEditor


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
        self.disabled = False      # không cho tương tác
        self.lock_close = False   # không cho đóng panel


        # ================= SURFACE =================
        self.surface = pygame.Surface(
            (self.base_width, self.base_height), pygame.SRCALPHA
        )

        # ================= FONT =================
        self.font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 15)
        self.title_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 17)
        self.code_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 15)

        self.line_h = self.code_font.get_height() + 3

        # Font nhỏ riêng cho nút Hướng dẫn
        self.hint_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 12)

        self.hint_text = self.hint_font.render("Hướng dẫn", True, (255, 255, 255))

        # Padding nhỏ lại để không vượt panel
        self.hint_padding_x = 5
        self.hint_padding_y = 3


        self.hint_btn_rect = self.hint_text.get_rect()
        self.hint_btn_rect.width  += self.hint_padding_x * 2
        self.hint_btn_rect.height += self.hint_padding_y * 2
        # ================= HELPERS =================
        self.text_layout = UITextLayout(self.font, line_height=18)
        self.editor = CodeEditor(self.code_font, self.line_h)

        # ================= DATA =================
        self.title = ""
        self.instructions = []

        # ===== HINT DATA =====
        self.hint_title = ""
        self.hints = []
        self.hint_examples = []

        # ================= STATE =================
        self.show_hint = False
        self.cursor_timer = 0
        self.cursor_visible = True

        # ================= UI RECTS =================
        self.snippet_rects = []
        self.example_rects = []

        self.control_mode = "hybrid"

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
            (140, 48),
        )
        self.run_rect = pygame.Rect(0, 0, 140, 48)
        self.title_text = UITextLayout(self.title_font, line_height=self.title_font.get_height() + 4)
        self.body_text  = UITextLayout(self.font, line_height=18)
    # ================= LOAD JSON =================
    def load_from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.title = data.get("title", "")
        self.instructions = data.get("instruction", [])

        hint_data = data.get("hint", {})
        self.hint_title = hint_data.get("title", "")
        self.hints = hint_data.get("description", [])
        self.hint_examples = hint_data.get("examples", [])
        self.control_mode = data.get("control_mode", "hybrid")
        self.editor.set_lines(data.get("solution", [""]))
        self.show_hint = False

    # ================= TOGGLE =================
    def open(self):
        self.opened = True
        self.target_x = self.visible_x

    def close(self):
        self.opened = False
        self.target_x = self.hidden_x
        self.show_hint = False

    def toggle(self):
        if self.disabled:
            return

        if self.lock_close and self.opened:
            return

        self.open() if not self.opened else self.close()


    # ================= INPUT =================
    def handle_event(self, event):
        if self.disabled:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(event.pos):
                self.toggle()
                return None

            if not self.opened:
                return None

            mx, my = event.pos
            local_x = int((mx - self.x) / self.scale)
            local_y = int(my / self.scale)

            # QUICK INSERT
            for rect, code in self.example_rects:
                if rect.collidepoint((local_x, local_y)):
                    self.editor.insert_line(code)
                    return None

            # RUN
            if self.run_rect.collidepoint((local_x, local_y)):
                return [l for l in self.editor.lines if l.strip()]

            # HINT
            if self.hint_btn_rect.collidepoint((local_x, local_y)):
                self.show_hint = not self.show_hint
                return None

        if event.type == pygame.KEYDOWN and self.opened:
            self.editor.handle_key(event)

        return None

    # ================= UPDATE =================
    def update(self, dt):
        self.hint_btn_rect.midright = (
            self.run_rect.left - 10,
            self.run_rect.centery
        )

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

        self.hint_btn_rect.midright = (
            self.run_rect.left - 10,
            self.run_rect.centery
        )

    # ================= DRAW =================
    def draw(self, screen):
        self.surface.fill((25, 25, 35))

        x = 20
        y = 20
        max_w = self.base_width - 40

        # ===== TITLE =====
        for line in self.title_text.wrap_words(
            self.title.upper(), max_w
        ):
            self.surface.blit(
                self.title_font.render(line, True, (255, 220, 120)),
                (x, y)
            )
            y += self.title_text.line_height
        y += 6


        # ===== INSTRUCTION =====
        y = self.text_layout.draw_paragraphs(
            self.surface,
            ["- " + i for i in self.instructions],
            x + 6,
            y,
            max_w - 20,
            (220, 220, 230),
        )

        # ===== EDITOR =====
        FOOTER_H = 120   # trước 80 → tăng để chừa chỗ nút Run + Hint
        QUICK_H  = 140   # trước 90 → chừa đủ chỗ gợi ý code

        editor_y = y + 8
        editor_h = self.base_height - editor_y - FOOTER_H - QUICK_H
        editor_rect = pygame.Rect(x, editor_y, max_w, editor_h)


        pygame.draw.rect(
            self.surface, (50, 50, 70), editor_rect, border_radius=6
        )

        self.draw_editor(editor_rect)

        # ===== QUICK INSERT =====
        self.draw_quick_insert(editor_rect)

        # ===== HINT BUTTON =====
        pygame.draw.rect(
            self.surface, (80, 120, 80), self.hint_btn_rect, border_radius=6
        )
        self.surface.blit(
            self.hint_text,
            (
                self.hint_btn_rect.centerx - self.hint_text.get_width() // 2,
                self.hint_btn_rect.centery - self.hint_text.get_height() // 2,
            )
        )


        # ===== RUN =====
        self.surface.blit(self.run_img, self.run_rect)

        # ===== BLIT =====
        scaled = pygame.transform.scale(self.surface, (self.width, self.height))
        screen.blit(scaled, (int(self.x), 0))
        screen.blit(
            self.btn_close_img if self.opened else self.btn_open_img,
            self.btn_rect,
        )

    # ================= EDITOR DRAW =================
    def draw_editor(self, rect):
        padding_x = 8
        padding_y = 6
        max_text_w = rect.width - padding_x * 2

        visual_lines = []
        cursor_vy = cursor_vx = 0

        for li, line in enumerate(self.editor.lines):
            wrapped = self.text_layout.wrap_words(line, max_text_w)
            remain = self.editor.cursor_col
            for w in wrapped:
                visual_lines.append((li, w))
                if li == self.editor.cursor_line and remain <= len(w):
                    cursor_vy = len(visual_lines) - 1
                    cursor_vx = self.code_font.size(w[:remain])[0]
                remain -= len(w)

        visible = rect.height // self.line_h
        self.editor.scroll = max(
            0, min(self.editor.scroll, len(visual_lines) - visible)
        )

        clip = self.surface.get_clip()
        self.surface.set_clip(rect)

        cy = rect.y + padding_y
        for i in range(
            self.editor.scroll,
            min(len(visual_lines), self.editor.scroll + visible),
        ):
            _, text = visual_lines[i]
            self.surface.blit(
                self.code_font.render(text, True, (150, 255, 150)),
                (rect.x + padding_x, cy),
            )
            if i == cursor_vy and self.cursor_visible:
                cx = rect.x + padding_x + cursor_vx
                pygame.draw.line(
                    self.surface,
                    (255, 255, 255),
                    (cx, cy),
                    (cx, cy + self.code_font.get_height()),
                )
            cy += self.line_h

        self.surface.set_clip(clip)

    # ================= QUICK INSERT DRAW =================
    def draw_quick_insert(self, editor_rect):
        self.example_rects.clear()

        y = editor_rect.bottom + 8
        max_w = self.base_width - 40

        if not self.hint_examples:
            return

        title = self.font.render("GỢI Ý CODE:", True, (180, 200, 255))
        self.surface.blit(title, (20 + 6, y))
        y += title.get_height() + 8

        line_h = self.code_font.get_height()
        box_h = line_h + 8   # padding trên + dưới

        for code in self.hint_examples[:3]:
            r = pygame.Rect(20 + 16, y, max_w - 32, box_h)

            pygame.draw.rect(self.surface, (55, 55, 75), r, border_radius=5)

            text_surf = self.code_font.render(code, True, (160, 235, 160))
            self.surface.blit(
                text_surf,
                (
                    r.x + 6,
                    r.y + (box_h - line_h) // 2 - 2
                ),
            )

            self.example_rects.append((r, code))
            y += box_h + 6

    # ================= POPUP HINT =================
    def draw_hint_popup(self, screen):
        if not self.show_hint:
            return

        popup_w = 260
        max_text_w = popup_w - 24

        popup_h = self.text_layout.calc_block_height(
            self.hints,
            max_text_w,
            has_title=bool(self.hint_title),
        )

        btn_x = self.x + self.hint_btn_rect.left * self.scale
        btn_y = self.hint_btn_rect.top * self.scale
        btn_h = self.hint_btn_rect.height * self.scale

        open_down = btn_y + btn_h + 8
        open_up = btn_y - popup_h * self.scale - 8

        py = open_down if open_down + popup_h * self.scale <= screen.get_height() else max(8, open_up)
        px = btn_x - popup_w * self.scale - 10

        popup = pygame.Rect(
            px, py, popup_w * self.scale, popup_h * self.scale
        )

        pygame.draw.rect(screen, (30, 30, 45), popup, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 160), popup, 2, border_radius=8)

        ty = popup.y + 12 * self.scale

        if self.hint_title:
            t = self.font.render(self.hint_title, True, (255, 220, 120))
            t = pygame.transform.scale_by(t, self.scale)
            screen.blit(t, (popup.x + 12 * self.scale, ty))
            ty += 22 * self.scale

        self.text_layout.draw_paragraphs(
            screen,
            self.hints,
            popup.x + 12 * self.scale,
            ty,
            max_text_w,
            (230, 230, 240),
        )
    def on_resize(self, screen_w, screen_h):
        # cập nhật scale theo chiều cao
        self.scale = screen_h / self.base_height

        self.width = int(self.base_width * self.scale)
        self.height = screen_h

        # cập nhật vị trí panel
        self.hidden_x = screen_w
        self.visible_x = screen_w - self.width

        if self.opened:
            self.x = self.visible_x
            self.target_x = self.visible_x
        else:
            self.x = self.hidden_x
            self.target_x = self.hidden_x
