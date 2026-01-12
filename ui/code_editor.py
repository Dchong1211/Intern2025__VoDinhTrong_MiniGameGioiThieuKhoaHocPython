import pygame

class CodeEditor:
    def __init__(self, font, line_height):
        self.font = font
        self.line_h = line_height
        self.lines = [""]
        self.cursor_line = 0
        self.cursor_col = 0
        self.scroll = 0
        
        # --- SELECTION VARIABLES (Bôi đen) ---
        # start/end format: (line_index, col_index) hoặc None
        self.sel_start = None 
        self.sel_end = None
        self.is_dragging = False

    def set_lines(self, lines):
        """Hàm tiện ích để reset nội dung code"""
        self.lines = lines if lines else [""]
        self.cursor_line = 0
        self.cursor_col = 0
        self.clear_selection()

    # ==========================================
    # LOGIC BÔI ĐEN (SELECTION)
    # ==========================================
    def get_selection_range(self):
        """Trả về (start, end) đã được sắp xếp đúng thứ tự (dòng nhỏ trước, dòng lớn sau)"""
        if not self.sel_start or not self.sel_end:
            return None
        
        s, e = self.sel_start, self.sel_end
        
        # So sánh dòng trước
        if s[0] > e[0]:
            return e, s
        # Nếu cùng dòng thì so sánh cột
        if s[0] == e[0] and s[1] > e[1]:
            return e, s
            
        return s, e

    def has_selection(self):
        """Kiểm tra xem có đang bôi đen gì không"""
        return self.sel_start is not None and self.sel_end is not None and self.sel_start != self.sel_end

    def clear_selection(self):
        """Hủy bôi đen"""
        self.sel_start = None
        self.sel_end = None

    def remove_selection(self):
        """Xóa đoạn văn bản đang được bôi đen"""
        if not self.has_selection():
            return

        start, end = self.get_selection_range()
        s_line, s_col = start
        e_line, e_col = end

        # 1. Lấy phần đầu của dòng bắt đầu (giữ lại)
        prefix = self.lines[s_line][:s_col]
        # 2. Lấy phần đuôi của dòng kết thúc (giữ lại)
        suffix = self.lines[e_line][e_col:]
        
        # 3. Ghép lại
        self.lines[s_line] = prefix + suffix
        
        # 4. Xóa các dòng nằm giữa (nếu chọn nhiều dòng)
        if s_line != e_line:
            # Xóa từ dòng s_line + 1 đến e_line
            del self.lines[s_line + 1 : e_line + 1]

        # 5. Cập nhật con trỏ về vị trí bắt đầu xóa
        self.cursor_line = s_line
        self.cursor_col = s_col
        self.clear_selection()

    # ==========================================
    # LOGIC CHỈNH SỬA (EDITING)
    # ==========================================
    def insert_text(self, text):
        """Chèn văn bản tại con trỏ (xử lý cả tab và nhiều dòng)"""
        # Nếu đang bôi đen -> Xóa trước khi nhập
        if self.has_selection():
            self.remove_selection()

        lines_to_insert = text.split('\n')
        
        # Lấy dòng hiện tại
        if self.cursor_line >= len(self.lines):
            self.lines.append("")
            
        current_line_text = self.lines[self.cursor_line]
        prefix = current_line_text[:self.cursor_col]
        suffix = current_line_text[self.cursor_col:]

        if len(lines_to_insert) == 1:
            # Trường hợp 1: Chèn trên cùng 1 dòng
            new_text = lines_to_insert[0]
            self.lines[self.cursor_line] = prefix + new_text + suffix
            self.cursor_col += len(new_text)
        else:
            # Trường hợp 2: Chèn nhiều dòng (Paste code từ ngoài vào)
            self.lines[self.cursor_line] = prefix + lines_to_insert[0]
            
            # Chèn các dòng giữa
            for i in range(1, len(lines_to_insert) - 1):
                self.lines.insert(self.cursor_line + i, lines_to_insert[i])
            
            # Xử lý dòng cuối cùng của phần chèn
            last_idx = len(lines_to_insert) - 1
            self.lines.insert(self.cursor_line + last_idx, lines_to_insert[-1] + suffix)
            
            # Cập nhật vị trí con trỏ
            self.cursor_line += last_idx
            self.cursor_col = len(lines_to_insert[-1])

    def handle_key(self, event):
        # 1. Xử lý Select All (Ctrl + A)
        if event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
            self.sel_start = (0, 0)
            self.sel_end = (len(self.lines) - 1, len(self.lines[-1]))
            return

        # 2. Xử lý Backspace
        if event.key == pygame.K_BACKSPACE:
            if self.has_selection():
                self.remove_selection()
            else:
                self._backspace_single()
            return

        # 3. Xử lý Delete
        if event.key == pygame.K_DELETE:
            if self.has_selection():
                self.remove_selection()
            else:
                # Delete: Di chuyển sang phải 1 bước rồi backspace
                if self.cursor_col < len(self.lines[self.cursor_line]) or self.cursor_line < len(self.lines) - 1:
                    self._move_cursor(1, 0)
                    self._backspace_single()
            return

        # 4. Xử lý Enter
        if event.key == pygame.K_RETURN:
            if self.has_selection():
                self.remove_selection()
            current = self.lines[self.cursor_line]
            # Cắt phần sau con trỏ xuống dòng mới
            self.lines.insert(self.cursor_line + 1, current[self.cursor_col:])
            # Giữ phần đầu ở dòng cũ
            self.lines[self.cursor_line] = current[:self.cursor_col]
            self.cursor_line += 1
            self.cursor_col = 0
            return

        # 5. Xử lý Tab (Chèn 4 spaces)
        if event.key == pygame.K_TAB:
            self.insert_text("    ") 
            return

        # 6. Điều hướng (Arrows)
        is_shift = event.mod & pygame.KMOD_SHIFT
        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            # Nếu giữ Shift -> Bắt đầu hoặc cập nhật vùng chọn
            if is_shift:
                if self.sel_start is None:
                    self.sel_start = (self.cursor_line, self.cursor_col)
            else:
                # Nếu không giữ Shift -> Hủy chọn
                self.clear_selection()
            
            # Di chuyển
            if event.key == pygame.K_UP: self._move_cursor(0, -1)
            elif event.key == pygame.K_DOWN: self._move_cursor(0, 1)
            elif event.key == pygame.K_LEFT: self._move_cursor(-1, 0)
            elif event.key == pygame.K_RIGHT: self._move_cursor(1, 0)
            
            # Cập nhật điểm cuối vùng chọn
            if is_shift:
                self.sel_end = (self.cursor_line, self.cursor_col)
            return

        # 7. Nhập ký tự thường (Unicode)
        # Chỉ nhận các ký tự in được (chữ, số, ký tự đặc biệt)
        if event.unicode and event.unicode.isprintable():
            # Chặn các phím điều khiển lạ
            self.insert_text(event.unicode)

    def _backspace_single(self):
        """Xóa 1 ký tự bên trái con trỏ"""
        if self.cursor_col > 0:
            # Xóa trên cùng dòng
            line = self.lines[self.cursor_line]
            self.lines[self.cursor_line] = line[:self.cursor_col - 1] + line[self.cursor_col:]
            self.cursor_col -= 1
        elif self.cursor_line > 0:
            # Xóa dòng (nối dòng hiện tại vào cuối dòng trước)
            prev_line = self.lines[self.cursor_line - 1]
            current_line = self.lines[self.cursor_line]
            
            self.lines[self.cursor_line - 1] = prev_line + current_line
            self.cursor_col = len(prev_line) # Con trỏ nằm ở chỗ nối
            self.lines.pop(self.cursor_line) # Xóa dòng dư
            self.cursor_line -= 1

    def _move_cursor(self, dx, dy):
        """Hàm phụ trợ di chuyển con trỏ an toàn"""
        self.cursor_line += dy
        
        # Kẹp dòng trong giới hạn
        if self.cursor_line < 0: self.cursor_line = 0
        elif self.cursor_line >= len(self.lines): self.cursor_line = len(self.lines) - 1
        
        # Xử lý di chuyển trái/phải qua dòng
        if dx == -1: # Move Left
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = len(self.lines[self.cursor_line])
        elif dx == 1: # Move Right
            if self.cursor_col < len(self.lines[self.cursor_line]):
                self.cursor_col += 1
            elif self.cursor_line < len(self.lines) - 1:
                self.cursor_line += 1
                self.cursor_col = 0
        
        # Kẹp cột khi di chuyển lên/xuống (tránh con trỏ nhảy ra ngoài line ngắn)
        line_len = len(self.lines[self.cursor_line])
        if self.cursor_col > line_len:
            self.cursor_col = line_len