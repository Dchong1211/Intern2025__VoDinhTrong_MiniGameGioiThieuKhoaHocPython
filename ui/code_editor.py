# ui/code_editor.py
import pygame

class CodeEditor:
    def __init__(self, font, line_height):
        self.font = font
        self.line_h = line_height

        self.lines = [""]
        self.cursor_line = 0
        self.cursor_col = 0
        self.scroll = 0
        
        # Cấu hình IDE
        self.tab_width = 4
        self.history = [] # TODO: Undo/Redo nếu cần sau này

    def set_lines(self, lines):
        self.lines = lines
        self.clamp_cursor()
        self.scroll = 0

    def get_text(self):
        return [l for l in self.lines]

    def insert_text(self, text):
        # Xử lý chèn text (bao gồm cả copy paste nhiều dòng nếu cần)
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_col] + text + line[self.cursor_col:]
        self.cursor_col += len(text)

    def insert_new_line(self):
        line = self.lines[self.cursor_line]
        current_indent = self._get_indentation(line)
        
        new_content = line[self.cursor_col:]
        self.lines[self.cursor_line] = line[:self.cursor_col]
        
        # Tự động thụt đầu dòng (Auto-indent)
        next_line = current_indent + new_content
        # Nếu dòng cũ kết thúc bằng ':', thêm indent cho dòng mới
        if self.lines[self.cursor_line].strip().endswith(':'):
             next_line = current_indent + " " * self.tab_width + new_content
             
        self.lines.insert(self.cursor_line + 1, next_line)
        self.cursor_line += 1
        self.cursor_col = len(next_line) - len(new_content)

    def backspace(self):
        line = self.lines[self.cursor_line]
        if self.cursor_col > 0:
            # Xóa 1 ký tự
            self.lines[self.cursor_line] = line[:self.cursor_col - 1] + line[self.cursor_col:]
            self.cursor_col -= 1
        elif self.cursor_line > 0:
            # Nối dòng hiện tại lên dòng trên
            prev_line = self.lines[self.cursor_line - 1]
            self.cursor_col = len(prev_line)
            self.lines[self.cursor_line - 1] = prev_line + line
            self.lines.pop(self.cursor_line)
            self.cursor_line -= 1

    def move_cursor(self, dx, dy):
        self.cursor_line += dy
        self.cursor_col += dx
        self.clamp_cursor()

    def set_cursor(self, line, col):
        self.cursor_line = line
        self.cursor_col = col
        self.clamp_cursor()

    def clamp_cursor(self):
        # Giữ con trỏ trong phạm vi hợp lệ
        if self.cursor_line < 0:
            self.cursor_line = 0
        elif self.cursor_line >= len(self.lines):
            self.cursor_line = len(self.lines) - 1
            
        line_len = len(self.lines[self.cursor_line])
        if self.cursor_col < 0:
            self.cursor_col = 0
        elif self.cursor_col > line_len:
            self.cursor_col = line_len

    def _get_indentation(self, line):
        # Lấy khoảng trắng đầu dòng để auto-indent
        return line[:len(line) - len(line.lstrip())]

    def handle_key(self, event):
        # === NAVIGATION ===
        if event.key == pygame.K_UP:
            self.move_cursor(0, -1)
        elif event.key == pygame.K_DOWN:
            self.move_cursor(0, 1)
        elif event.key == pygame.K_LEFT:
            if self.cursor_col > 0:
                self.move_cursor(-1, 0)
            elif self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = len(self.lines[self.cursor_line])
        elif event.key == pygame.K_RIGHT:
            if self.cursor_col < len(self.lines[self.cursor_line]):
                self.move_cursor(1, 0)
            elif self.cursor_line < len(self.lines) - 1:
                self.cursor_line += 1
                self.cursor_col = 0
        
        # === EDITING ===
        elif event.key == pygame.K_BACKSPACE:
            self.backspace()
        elif event.key == pygame.K_RETURN:
            self.insert_new_line()
        elif event.key == pygame.K_TAB:
            self.insert_text(" " * self.tab_width)
        elif event.key == pygame.K_HOME:
            self.cursor_col = 0
        elif event.key == pygame.K_END:
            self.cursor_col = len(self.lines[self.cursor_line])
        
        # === TYPING ===
        elif event.unicode and event.unicode.isprintable():
            self.insert_text(event.unicode)