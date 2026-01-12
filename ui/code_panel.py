import pygame
import json
from ui.ui_text import UITextLayout
from ui.code_editor import CodeEditor

# === COLOR PALETTE ===
COLOR_BG = (25, 27, 35)
COLOR_BTN_DEFAULT = (60, 65, 80)
COLOR_TEXT_MAIN = (230, 230, 240)
COLOR_ACCENT = (80, 200, 255)
COLOR_SELECTION = (60, 100, 150) # Màu nền khi bôi đen

class CommandBtn:
    def __init__(self, text, code_snippet, color):
        self.text = text
        self.code = code_snippet
        self.base_color = color
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 12)

    def update_rect(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, self.base_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        txt_surf = self.font.render(self.text, True, (255, 255, 255))
        tx = self.rect.x + (self.rect.width - txt_surf.get_width()) // 2
        ty = self.rect.y + (self.rect.height - txt_surf.get_height()) // 2
        surface.blit(txt_surf, (tx, ty))

class CodePanel:
    def __init__(self, x_pos, width, height):
        self.width = width
        self.height = height 
        self.x = x_pos 
        self.surface = pygame.Surface((self.width, self.height))

        # --- SETUP KEY REPEAT ---
        # Cho phép giữ phím để xóa/nhập liên tục (delay 400ms, speed 30ms)
        pygame.key.set_repeat(400, 30)

        # --- FONTS ---
        try:
            self.code_font = pygame.font.Font("assets/Font/Consolas.ttf", 16)
        except:
            self.code_font = pygame.font.SysFont("consolas", 16)

        self.ui_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 16)
        self.small_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 12)

        self.line_h = self.code_font.get_height() + 6
        
        # --- COMPONENTS ---
        self.editor = CodeEditor(self.code_font, self.line_h)
        self.text_layout = UITextLayout(self.ui_font, line_height=24)

        # --- DATA ---
        self.title = "MISSION CONTROL"
        self.instructions = []
        self.hint_title = ""
        self.hints = []
        self.show_hint = False

        # --- COMMAND BUTTONS (Đã sửa Indent thành 4 spaces) ---
        self.commands = [
            CommandBtn("MOVE RIGHT", "move_right(1)", (50, 120, 180)),
            CommandBtn("MOVE LEFT", "move_left(1)", (50, 120, 180)),
            CommandBtn("JUMP UP", "jump()", (180, 80, 80)),
            CommandBtn("LOOP 3x", "for i in range(3):", (200, 140, 40)),
            CommandBtn("INDENT (TAB)", "    ", (100, 100, 110)), 
        ]

        # --- RECTS ---
        self.run_btn_rect = pygame.Rect(0, 0, 160, 50)
        self.hint_btn_rect = pygame.Rect(0, 0, 40, 40)
        self.editor_rect_cache = pygame.Rect(0,0,0,0)
        
        # --- ASSETS ---
        self.icon_run = self._make_run_button_img((160, 50))
        self.lbl_hint = self.ui_font.render("?", True, COLOR_ACCENT)

        # --- STATE ---
        self.cursor_timer = 0
        self.cursor_visible = True
        
        self.on_resize(x_pos + width, height)

    def _make_run_button_img(self, size):
        s = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(s, (40, 200, 100), (0,0,size[0], size[1]), border_radius=10)
        pygame.draw.rect(s, (255,255,255), (0,0,size[0], size[1]), 3, border_radius=10)
        font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 20)
        txt = font.render("RUN CODE", True, (255,255,255))
        s.blit(txt, ((size[0]-txt.get_width())//2, (size[1]-txt.get_height())//2))
        return s

    def load_from_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.title = data.get("title", "Mission")
            self.instructions = data.get("instruction", [])
            hint_data = data.get("hint", {})
            self.hint_title = hint_data.get("title", "Gợi ý")
            self.hints = hint_data.get("description", [])
            self.editor.lines = data.get("solution", [""])
            self.editor.clear_selection()
        except Exception as e:
            print(f"Error loading level JSON: {e}")

    def on_resize(self, screen_w, screen_h):
        self.height = screen_h
        self.x = screen_w - self.width
        self.surface = pygame.Surface((self.width, self.height))

        padding = 20
        self.hint_btn_rect.topright = (self.width - padding, padding)

        btn_h = 40
        cols = 2
        col_w = (self.width - padding*3) // cols
        start_y = 100
        
        for i, cmd in enumerate(self.commands):
            row = i // cols
            col = i % cols
            bx = padding + col * (col_w + padding)
            by = start_y + row * (btn_h + 15)
            cmd.update_rect(bx, by, col_w, btn_h)
            
        rows = (len(self.commands) + cols - 1) // cols
        current_btn_bottom = start_y + rows * (btn_h + 15)

        self.run_btn_rect.midbottom = (self.width // 2, self.height - 25)

        y_editor = current_btn_bottom + 50
        footer_h = 90
        editor_h = self.height - y_editor - footer_h
        self.editor_rect_cache = pygame.Rect(padding, y_editor, self.width - padding*2, editor_h)

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            local_x = mx - self.x
            local_y = my
            
            if mx < self.x: return None
            
            # 1. RUN Button
            if self.run_btn_rect.collidepoint(local_x, local_y):
                return [l for l in self.editor.lines if l.strip()]

            # 2. HINT Button
            if self.hint_btn_rect.collidepoint(local_x, local_y):
                self.show_hint = not self.show_hint
                return None

            # 3. COMMAND Buttons
            for cmd in self.commands:
                if cmd.rect.collidepoint(local_x, local_y):
                    # Dùng insert_text của editor để đảm bảo đúng logic vùng chọn/cursor
                    self.editor.insert_text(cmd.code)
                    return None
            
            # 4. CLICK IN EDITOR (Bắt đầu bôi đen)
            if self.editor_rect_cache.collidepoint(local_x, local_y):
                line, col = self._get_line_col_at(local_x, local_y)
                self.editor.cursor_line = line
                self.editor.cursor_col = col
                self.editor.sel_start = (line, col)
                self.editor.sel_end = (line, col) # Reset selection point
                self.editor.is_dragging = True
            else:
                self.editor.clear_selection()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.editor.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            # Xử lý kéo chuột để bôi đen
            if self.editor.is_dragging:
                mx, my = event.pos
                local_x = mx - self.x
                local_y = my
                if self.editor_rect_cache.collidepoint(local_x, local_y):
                    line, col = self._get_line_col_at(local_x, local_y)
                    self.editor.cursor_line = line
                    self.editor.cursor_col = col
                    self.editor.sel_end = (line, col)

        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx > self.x: 
                self.editor.scroll -= event.y
                if self.editor.scroll < 0: self.editor.scroll = 0
                
        elif event.type == pygame.KEYDOWN:
            self.editor.handle_key(event)
            self.cursor_visible = True

        return None

    def _get_line_col_at(self, local_x, local_y):
        """Chuyển đổi toạ độ pixel -> dòng, cột"""
        gutter_w = 40
        text_x = self.editor_rect_cache.x + gutter_w + 5
        rel_y = local_y - self.editor_rect_cache.y
        
        line_idx = int(rel_y // self.line_h) + self.editor.scroll
        if line_idx < 0: line_idx = 0
        if line_idx >= len(self.editor.lines): line_idx = len(self.editor.lines) - 1
        
        line_text = self.editor.lines[line_idx]
        
        # Tìm cột dựa trên độ rộng font
        rel_x = local_x - text_x
        if rel_x < 0: return line_idx, 0
        
        # Duyệt từng ký tự để xem chuột đang ở ký tự thứ mấy
        cum_w = 0
        for i, char in enumerate(line_text):
            cw = self.code_font.size(char)[0]
            if cum_w + cw / 2 > rel_x:
                return line_idx, i
            cum_w += cw
        
        return line_idx, len(line_text)

    def draw(self, screen):
        self.surface.fill(COLOR_BG)
        pygame.draw.line(self.surface, (100, 100, 100), (0,0), (0, self.height), 2)
        padding = 20
        
        # Header & UI
        title_surf = self.ui_font.render(self.title, True, COLOR_ACCENT)
        self.surface.blit(title_surf, (padding, padding))
        
        pygame.draw.rect(self.surface, (60, 60, 70), self.hint_btn_rect, border_radius=20)
        pygame.draw.rect(self.surface, COLOR_ACCENT, self.hint_btn_rect, 2, border_radius=20)
        lbl_rect = self.lbl_hint.get_rect(center=self.hint_btn_rect.center)
        self.surface.blit(self.lbl_hint, lbl_rect)
        
        instr = self.small_font.render("Click buttons to code:", True, (180, 180, 180))
        self.surface.blit(instr, (padding, 60))
        
        for cmd in self.commands:
            cmd.draw(self.surface)

        lbl_code_y = self.editor_rect_cache.y - 25
        lbl_code = self.small_font.render("YOUR SOLUTION:", True, (255, 255, 255))
        self.surface.blit(lbl_code, (padding, lbl_code_y))

        # Editor BG
        pygame.draw.rect(self.surface, (20, 22, 28), self.editor_rect_cache)
        pygame.draw.rect(self.surface, (60, 65, 80), self.editor_rect_cache, 2)
        
        self._draw_editor_text(self.editor_rect_cache)
        self.surface.blit(self.icon_run, self.run_btn_rect)
        screen.blit(self.surface, (self.x, 0))

    def _draw_editor_text(self, rect):
        old_clip = self.surface.get_clip()
        self.surface.set_clip(rect)
        
        start_line = self.editor.scroll
        visible_lines = rect.height // self.line_h + 1
        end_line = min(len(self.editor.lines), start_line + visible_lines)
        
        gutter_w = 40
        text_x = rect.x + gutter_w + 5
        ty = rect.y + 10
        
        # Gutter
        pygame.draw.rect(self.surface, (30, 32, 40), (rect.x, rect.y, gutter_w, rect.height))
        pygame.draw.line(self.surface, (60, 60, 60), (rect.x + gutter_w, rect.y), (rect.x + gutter_w, rect.y + rect.height))
        
        # Get Selection Range
        sel_range = self.editor.get_selection_range()

        for i in range(start_line, end_line):
            line = self.editor.lines[i]
            
            # --- VẼ SELECTION HIGHLIGHT ---
            if sel_range:
                s, e = sel_range
                # Nếu dòng này nằm trong vùng chọn
                if s[0] <= i <= e[0]:
                    sel_x_start = text_x
                    sel_width = 0
                    
                    # Tính toán cột bắt đầu và kết thúc highlight trên dòng này
                    col_start = 0 if i > s[0] else s[1]
                    col_end = len(line) if i < e[0] else e[1]
                    
                    # Tính toạ độ pixel
                    # Đo độ rộng từ đầu dòng đến col_start
                    px_start = self.code_font.size(line[:col_start])[0]
                    # Đo độ rộng phần được chọn
                    px_w = self.code_font.size(line[col_start:col_end])[0]
                    
                    # Nếu là dòng trống mà đang được chọn (ví dụ chọn hết dòng) thì vẽ 1 cục nhỏ
                    if px_w == 0 and i < e[0]: 
                         px_w = 10 # Width ảo để thấy được dòng trống được chọn
                    
                    highlight_rect = pygame.Rect(text_x + px_start, ty, px_w, self.line_h)
                    pygame.draw.rect(self.surface, COLOR_SELECTION, highlight_rect)

            # --- DRAW LINE NUMBER ---
            num_s = self.code_font.render(str(i+1), True, (100, 100, 100))
            self.surface.blit(num_s, (rect.x + gutter_w - num_s.get_width() - 5, ty))
            
            # --- DRAW TEXT ---
            code_s = self.code_font.render(line, True, COLOR_TEXT_MAIN)
            self.surface.blit(code_s, (text_x, ty))
            
            # --- DRAW CURSOR ---
            if i == self.editor.cursor_line and self.cursor_visible:
                w = self.code_font.size(line[:self.editor.cursor_col])[0]
                cx = text_x + w
                pygame.draw.line(self.surface, (255, 255, 0), (cx, ty), (cx, ty + self.line_h), 2)

            ty += self.line_h

        self.surface.set_clip(old_clip)

    def draw_hint_popup(self, screen):
        # (Giữ nguyên code vẽ hint của bạn)
        if not self.show_hint: return
        popup_w = 400
        padding = 20
        text_height = self.text_layout.calc_block_height(self.hints, popup_w - padding*2, has_title=True)
        popup_h = text_height + padding*2
        px = self.x - popup_w - 20
        py = 50 
        rect = pygame.Rect(px, py, popup_w, popup_h)
        shadow_rect = rect.copy()
        shadow_rect.x += 4; shadow_rect.y += 4
        pygame.draw.rect(screen, (0,0,0, 100), shadow_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 35, 45), rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_ACCENT, rect, 2, border_radius=12)
        curr_y = rect.y + padding
        if self.hint_title:
            t = self.ui_font.render(self.hint_title, True, COLOR_ACCENT)
            screen.blit(t, (rect.x + padding, curr_y))
            curr_y += 30
        self.text_layout.draw_paragraphs(screen, self.hints, rect.x + padding, curr_y, popup_w - padding*2, (200, 200, 200))