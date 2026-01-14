import pygame
import json
import os
from ui.ui_text import UITextLayout
from ui.code_editor import CodeEditor

# === COLOR PALETTE ===
COLOR_BG = (25, 27, 35)
COLOR_BTN_DEFAULT = (60, 65, 80)
COLOR_TEXT_MAIN = (230, 230, 240)
COLOR_ACCENT = (80, 200, 255)
COLOR_SELECTION = (60, 100, 150) 

class CommandBtn:
    def __init__(self, text, code_snippet, color):
        self.text = text
        self.code = code_snippet
        self.base_color = color
        self.rect = pygame.Rect(0, 0, 0, 0)
        try:
            self.font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 12)
        except:
            self.font = pygame.font.SysFont("arial", 12, bold=True)

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
    def __init__(self, x_pos, width, height, config_path="data/levels_config.json"):
        self.width = width
        self.height = height 
        self.x = x_pos 
        self.surface = pygame.Surface((self.width, self.height))

        # --- SETUP KEY REPEAT ---
        pygame.key.set_repeat(400, 30)

        # --- FONTS ---
        try:
            self.code_font = pygame.font.Font("assets/Font/Consolas.ttf", 16)
        except:
            self.code_font = pygame.font.SysFont("consolas", 16)

        try:
            self.ui_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 16)
            self.small_font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 12)
        except:
            self.ui_font = pygame.font.SysFont("arial", 16, bold=True)
            self.small_font = pygame.font.SysFont("arial", 12)

        self.line_h = self.code_font.get_height() + 6
        
        # --- COMPONENTS ---
        self.editor = CodeEditor(self.code_font, self.line_h)
        self.text_layout = UITextLayout(self.ui_font, line_height=24)

        # --- DATA STORAGE ---
        self.all_quests_data = {} 
        self.title = "MISSION CONTROL"
        self.instructions = []
        self.hint_title = ""
        self.hints = []
        self.show_hint = False
        
        # Biến trạng thái điều khiển
        self.control_mode = "code" 

        # --- COMMAND BUTTONS ---
        self.commands = [
            CommandBtn("MOVE RIGHT", "move_right(1)", (50, 120, 180)),
            CommandBtn("MOVE LEFT", "move_left(1)", (50, 120, 180)),
            CommandBtn("JUMP UP", "jump()", (180, 80, 80)),
            CommandBtn("LOOP 3x", "for i in range(3):", (200, 140, 40)),
            CommandBtn("INDENT (TAB)", "    ", (100, 100, 110)), 
        ]

        # --- RECTS & ASSETS ---
        self.run_btn_rect = pygame.Rect(0, 0, 160, 50)
        self.hint_btn_rect = pygame.Rect(0, 0, 40, 40)
        self.editor_rect_cache = pygame.Rect(0,0,0,0)
        
        self.cmd_label_y = 160 

        self.icon_run = self._make_run_button_img((160, 50))
        self.lbl_hint = self.ui_font.render("?", True, COLOR_ACCENT)

        # --- STATE ---
        self.cursor_timer = 0
        self.cursor_visible = True
        
        self.load_all_quests(config_path) 
        self.on_resize(x_pos + width, height)

    def _make_run_button_img(self, size):
        s = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(s, (40, 200, 100), (0,0,size[0], size[1]), border_radius=10)
        pygame.draw.rect(s, (255,255,255), (0,0,size[0], size[1]), 3, border_radius=10)
        try:
            font = pygame.font.Font("assets/Font/FVF Fernando 08.ttf", 20)
        except:
            font = pygame.font.SysFont("arial", 20, bold=True)
            
        txt = font.render("RUN CODE", True, (255,255,255))
        s.blit(txt, ((size[0]-txt.get_width())//2, (size[1]-txt.get_height())//2))
        return s

    def _calc_text_height(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = font.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        line_height = font.get_height() + 4
        return len(lines) * line_height

    def recalculate_layout(self):
        padding = 20
        max_w = self.width - padding * 2
        current_y = 50 

        if self.instructions:
            for line in self.instructions:
                h = self._calc_text_height(line, self.small_font, max_w)
                current_y += h + 5 
        else:
            h = self._calc_text_height("No instructions.", self.small_font, max_w)
            current_y += h + 5
            
        self.cmd_label_y = current_y + 10
        
        start_y_buttons = self.cmd_label_y + 25
        btn_h = 40
        cols = 2
        col_w = (self.width - padding*3) // cols
        
        for i, cmd in enumerate(self.commands):
            row = i // cols
            col = i % cols
            bx = padding + col * (col_w + padding)
            by = start_y_buttons + row * (btn_h + 15)
            cmd.update_rect(bx, by, col_w, btn_h)
            
        rows = (len(self.commands) + cols - 1) // cols
        buttons_bottom = start_y_buttons + rows * (btn_h + 15)
        
        self.run_btn_rect.midbottom = (self.width // 2, self.height - 25)
        
        y_editor = buttons_bottom + 20
        footer_h = 90
        editor_h = max(50, self.height - y_editor - footer_h)
        
        self.editor_rect_cache = pygame.Rect(padding, y_editor, self.width - padding*2, editor_h)

    def load_all_quests(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.all_quests_data = json.load(f)
            print(f"[CodePanel] Loaded quests from {path}")
        except FileNotFoundError:
            print(f"[CodePanel] ERROR: Không tìm thấy file config tại '{path}'")
            self.all_quests_data = {}
        except Exception as e:
            print(f"[CodePanel] Error loading config JSON: {e}")
            self.all_quests_data = {}

    def load_level(self, level_id):
        str_id = str(level_id)
        
        # Reset editor state (scroll, cursor) nhưng KHÔNG reset text
        self.editor.clear_selection()
        self.editor.scroll = 0
        self.editor.cursor_line = 0
        self.editor.cursor_col = 0
        
        if str_id in self.all_quests_data:
            data = self.all_quests_data[str_id]
            
            # Load thông tin level
            self.title = data.get("title", f"Level {level_id}")
            raw_instr = data.get("instruction", [])
            self.instructions = raw_instr if isinstance(raw_instr, list) else [str(raw_instr)]
            
            guide_data = data.get("guide", data.get("hint", {}))
            self.hint_title = guide_data.get("title", "Tài liệu kỹ thuật")
            self.hints = guide_data.get("description", ["Không có tài liệu."])
            
            # Cập nhật Control Mode
            self.control_mode = data.get("control_mode", "code")
            
            if self.control_mode == "keyboard":
                self.title += " (Phím)"
                # Đã loại bỏ việc gán self.editor.lines tại đây
            else:
                # Đã loại bỏ việc gán self.editor.lines tại đây
                pass
            
            print(f"[CodePanel] Displaying Level {level_id} (Mode: {self.control_mode})")
        else:
            print(f"[CodePanel] WARNING: Không tìm thấy level {level_id}")
            self.title = "No Data"
            self.control_mode = "code"
            self.instructions = ["Chưa có dữ liệu level này."]
            # Giữ nguyên text hiện tại của editor hoặc để CodeEditor tự xử lý
        
        self.recalculate_layout()

    def on_resize(self, screen_w, screen_h):
        self.height = screen_h
        self.width = 320 
        self.x = screen_w - self.width
        self.surface = pygame.Surface((self.width, self.height))

        padding = 20
        self.hint_btn_rect.topright = (self.width - padding, padding)

        self.recalculate_layout()

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx < self.x:
                return None
            
            local_x = mx - self.x
            local_y = my
            
            # Run Button - Vẫn trả về lines từ editor để Main xử lý
            if self.run_btn_rect.collidepoint(local_x, local_y):
                return [l for l in self.editor.lines if l.strip()]

            if self.hint_btn_rect.collidepoint(local_x, local_y):
                self.show_hint = not self.show_hint
                return None

            # Logic chặn click khi ở chế độ Keyboard
            if self.control_mode != "keyboard":
                for cmd in self.commands:
                    if cmd.rect.collidepoint(local_x, local_y):
                        self.editor.insert_text(cmd.code)
                        return None
                
                if self.editor_rect_cache.collidepoint(local_x, local_y):
                    line, col = self._get_line_col_at(local_x, local_y)
                    self.editor.cursor_line = line
                    self.editor.cursor_col = col
                    self.editor.sel_start = (line, col)
                    self.editor.sel_end = (line, col)
                    self.editor.is_dragging = True
                else:
                    self.editor.clear_selection()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.editor.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.editor.is_dragging and self.control_mode != "keyboard":
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
            if self.control_mode != "keyboard":
                self.editor.handle_key(event)
                self.cursor_visible = True

        return None

    def _get_line_col_at(self, local_x, local_y):
        gutter_w = 40
        text_x = self.editor_rect_cache.x + gutter_w + 5
        rel_y = local_y - self.editor_rect_cache.y
        
        line_idx = int(rel_y // self.line_h) + self.editor.scroll
        if line_idx < 0: line_idx = 0
        if line_idx >= len(self.editor.lines): line_idx = len(self.editor.lines) - 1
        
        line_text = self.editor.lines[line_idx]
        rel_x = local_x - text_x
        if rel_x < 0: return line_idx, 0
        
        cum_w = 0
        for i, char in enumerate(line_text):
            cw = self.code_font.size(char)[0]
            if cum_w + cw / 2 > rel_x:
                return line_idx, i
            cum_w += cw
        return line_idx, len(line_text)

    def _draw_wrapped_text(self, surface, text, x, y, max_width, font, color):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = font.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        current_y = y
        line_height = font.get_height() + 4
        for line in lines:
            txt_surf = font.render(line, True, color)
            surface.blit(txt_surf, (x, current_y))
            current_y += line_height
        
        return current_y

    def draw(self, screen):
        self.surface.fill(COLOR_BG)
        pygame.draw.line(self.surface, (100, 100, 100), (0,0), (0, self.height), 2)
        padding = 20
        
        # 1. Header Title
        title_surf = self.ui_font.render(self.title, True, COLOR_ACCENT)
        self.surface.blit(title_surf, (padding, padding))
        
        # 2. Hint Button
        pygame.draw.rect(self.surface, (60, 60, 70), self.hint_btn_rect, border_radius=20)
        pygame.draw.rect(self.surface, COLOR_ACCENT, self.hint_btn_rect, 2, border_radius=20)
        lbl_rect = self.lbl_hint.get_rect(center=self.hint_btn_rect.center)
        self.surface.blit(self.lbl_hint, lbl_rect)
        
        # 3. Instructions
        instr_y = 50
        max_w = self.width - padding * 2 
        
        if self.instructions:
            for line in self.instructions:
                instr_y = self._draw_wrapped_text(
                    self.surface, line, padding, instr_y, max_w, self.small_font, (200, 200, 200)
                )
                instr_y += 5 
        else:
            instr_y = self._draw_wrapped_text(
                self.surface, "No instructions.", padding, instr_y, max_w, self.small_font, (150, 150, 150)
            )
            
        # 4. Commands Buttons
        if self.control_mode != "keyboard":
            instr_lbl = self.small_font.render("Click buttons to code:", True, (150, 150, 150))
            self.surface.blit(instr_lbl, (padding, self.cmd_label_y))
            
            for cmd in self.commands:
                cmd.draw(self.surface)

        # 5. Editor
        lbl_code_y = self.editor_rect_cache.y - 25
        lbl_code = self.small_font.render("YOUR SOLUTION:", True, (255, 255, 255))
        self.surface.blit(lbl_code, (padding, lbl_code_y))

        pygame.draw.rect(self.surface, (20, 22, 28), self.editor_rect_cache)
        pygame.draw.rect(self.surface, (60, 65, 80), self.editor_rect_cache, 2)
        
        self._draw_editor_text(self.editor_rect_cache)
        
        if self.control_mode != "keyboard":
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
        
        pygame.draw.rect(self.surface, (30, 32, 40), (rect.x, rect.y, gutter_w, rect.height))
        pygame.draw.line(self.surface, (60, 60, 60), (rect.x + gutter_w, rect.y), (rect.x + gutter_w, rect.y + rect.height))
        
        sel_range = self.editor.get_selection_range()

        for i in range(start_line, end_line):
            line = self.editor.lines[i]
            
            if sel_range and self.control_mode != "keyboard":
                s, e = sel_range
                if s[0] <= i <= e[0]:
                    col_start = 0 if i > s[0] else s[1]
                    col_end = len(line) if i < e[0] else e[1]
                    px_start = self.code_font.size(line[:col_start])[0]
                    px_w = self.code_font.size(line[col_start:col_end])[0]
                    if px_w == 0 and i < e[0]: px_w = 10 
                    highlight_rect = pygame.Rect(text_x + px_start, ty, px_w, self.line_h)
                    pygame.draw.rect(self.surface, COLOR_SELECTION, highlight_rect)

            num_s = self.code_font.render(str(i+1), True, (100, 100, 100))
            self.surface.blit(num_s, (rect.x + gutter_w - num_s.get_width() - 5, ty))
            
            color = COLOR_TEXT_MAIN
            if line.strip().startswith("#"):
                color = (100, 150, 100) 
            
            code_s = self.code_font.render(line, True, color)
            self.surface.blit(code_s, (text_x, ty))
            
            if i == self.editor.cursor_line and self.cursor_visible and self.control_mode != "keyboard":
                w = self.code_font.size(line[:self.editor.cursor_col])[0]
                cx = text_x + w
                pygame.draw.line(self.surface, (255, 255, 0), (cx, ty), (cx, ty + self.line_h), 2)
            
            ty += self.line_h
        
        self.surface.set_clip(old_clip)

    def draw_hint_popup(self, screen):
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