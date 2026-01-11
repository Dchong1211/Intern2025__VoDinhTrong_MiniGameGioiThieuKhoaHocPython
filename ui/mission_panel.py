import pygame

class MissionPanel:
    BASE_H = 720
    # Đảm bảo đường dẫn font đúng, nếu lỗi hãy thay bằng None để dùng font mặc định
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf" 

    def __init__(self, screen_w, objective, icons):
        self.screen_w = screen_w
        self.objective = objective # Object chứa dữ liệu nhiệm vụ
        self.icons = icons         # Dictionary chứa hình ảnh icon

        # ===== SIZE =====
        self.width = 240           # Thu gọn chiều rộng một chút cho gọn
        self.height = 120          # Sẽ được tính lại tự động

        # ===== SLIDE LEFT -> RIGHT =====
        self.hidden_x = -self.width
        self.visible_x = 0

        self.x = self.hidden_x
        self.target_x = self.hidden_x

        self.speed = 1200          # Tốc độ trượt
        self.opened = False

        # ===== FONT =====
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, 18)
            self.font_item = pygame.font.Font(self.FONT_PATH, 12) # Font nhỏ hơn chút để vừa vặn
        except:
            self.font_title = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_item = pygame.font.SysFont("Arial", 12)

        # ===== TOGGLE BUTTON =====
        self.btn_size = 40
        self.btn_rect = pygame.Rect(0, 0, self.btn_size, self.btn_size)

        # Load hình nút (Dùng try-except để tránh crash nếu thiếu ảnh)
        try:
            self.btn_show = pygame.transform.scale(
                pygame.image.load("assets/Menu/Buttons/Hide.png").convert_alpha(),
                (self.btn_size, self.btn_size)
            )
            self.btn_hide = pygame.transform.scale(
                pygame.image.load("assets/Menu/Buttons/Show.png").convert_alpha(),
                (self.btn_size, self.btn_size)
            )
        except:
            self.btn_show = pygame.Surface((self.btn_size, self.btn_size))
            self.btn_show.fill((255, 255, 0)) # Vàng
            self.btn_hide = pygame.Surface((self.btn_size, self.btn_size))
            self.btn_hide.fill((200, 200, 200)) # Xám

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
        if self.opened:
            self.close()
        else:
            self.open()

    # ==================================================
    # EVENT
    # ==================================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Cộng thêm offset self.x vì btn_rect di chuyển theo panel
            # Tuy nhiên trong update ta đã gán btn_rect.x chuẩn rồi nên chỉ cần check collide
            if self.btn_rect.collidepoint(event.pos):
                self.toggle()

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, dt):
        # Hiệu ứng trượt mượt mà
        if self.x != self.target_x:
            if self.x < self.target_x:
                self.x += self.speed * dt
                if self.x > self.target_x: self.x = self.target_x
            elif self.x > self.target_x:
                self.x -= self.speed * dt
                if self.x < self.target_x: self.x = self.target_x

        # Cập nhật vị trí nút Toggle luôn dính bên cạnh Panel
        self.btn_rect.x = int(self.x + self.width)
        # Nút nằm giữa theo chiều dọc panel (hoặc cố định ở trên cùng tùy bạn)
        # Ở đây mình để cố định cách top 10px cho dễ bấm
        self.btn_rect.y = 10 

    # ==================================================
    # SIZE CALCULATION
    # ==================================================
    def recalc_height(self):
        """Tính toán chiều cao bảng dựa trên số lượng nhiệm vụ"""
        if not self.objective or not hasattr(self.objective, 'objectives'):
            self.height = 80
            return

        items = self.objective.objectives
        if not items:
            self.height = 80
            return

        pad = 14
        gap = 6
        title_h = self.font_title.get_height()
        # Chiều cao mỗi dòng item (lấy max giữa text và icon)
        item_h = 32 # Cố định chiều cao dòng cho đều

        # Công thức: Padding trên + Title + Gap + (Số dòng * chiều cao dòng) + Padding dưới
        self.height = (pad * 2) + title_h + gap + (len(items) * (item_h + gap))

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self, screen):
        # 1. QUAN TRỌNG: Tính lại chiều cao trước khi vẽ
        # Để đảm bảo nếu có thêm trái cây mới, bảng sẽ dài ra
        self.recalc_height()

        if not self.objective:
            return

        # Lấy dữ liệu
        objectives_data = getattr(self.objective, 'objectives', {})
        
        # Tạo bề mặt Panel (Background)
        panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180)) # Màu đen trong suốt
        
        # Viền trang trí (Optional)
        pygame.draw.rect(panel, (255, 215, 0), (0, 0, self.width, self.height), 2)

        pad = 14
        gap = 6
        current_y = pad

        # ===== VẼ TITLE "MISSION" =====
        title_surf = self.font_title.render("MISSION", True, (255, 215, 0))
        # Căn giữa title
        title_x = (self.width - title_surf.get_width()) // 2
        panel.blit(title_surf, (title_x, current_y))
        
        current_y += title_surf.get_height() + gap

        # ===== VẼ DANH SÁCH FRUITS =====
        icon_size = 28 # Kích thước icon vẽ ra
        line_height = 32 # Chiều cao dành cho 1 dòng

        for name, data in objectives_data.items():
            current_val = data.get("collected", 0)
            target_val = data.get("required", 1)
            is_done = current_val >= target_val
            
            # Màu sắc: Xanh lá nếu xong, Trắng nếu chưa
            text_color = (100, 255, 100) if is_done else (255, 255, 255)

            # 1. Tên trái cây (Căn lề trái)
            name_surf = self.font_item.render(name, True, text_color)
            # Căn giữa theo chiều dọc của dòng
            name_y = current_y + (line_height - name_surf.get_height()) // 2
            panel.blit(name_surf, (pad, name_y))

            # 2. Số lượng "0/6" (Căn lề phải ngoài cùng)
            count_str = f"{current_val}/{target_val}"
            count_surf = self.font_item.render(count_str, True, text_color)
            
            count_x = self.width - pad - count_surf.get_width()
            count_y = current_y + (line_height - count_surf.get_height()) // 2
            panel.blit(count_surf, (count_x, count_y))

            # 3. Icon (Nằm bên trái của số lượng)
            if name in self.icons:
                original_icon = self.icons[name]
                if original_icon:
                    scaled_icon = pygame.transform.scale(original_icon, (icon_size, icon_size))
                    # Vị trí icon: Bên trái text số lượng - 5px padding
                    icon_x = count_x - icon_size - 8
                    icon_y = current_y + (line_height - icon_size) // 2
                    panel.blit(scaled_icon, (icon_x, icon_y))

            # Tăng Y để vẽ dòng tiếp theo
            current_y += line_height + gap

        # ===== VẼ PANEL LÊN MÀN HÌNH CHÍNH =====
        screen.blit(panel, (int(self.x), 0))

        # ===== VẼ NÚT TOGGLE =====
        # Vẽ nút nằm đè lên layer cuối cùng
        btn_img = self.btn_hide if self.opened else self.btn_show
        screen.blit(btn_img, self.btn_rect)