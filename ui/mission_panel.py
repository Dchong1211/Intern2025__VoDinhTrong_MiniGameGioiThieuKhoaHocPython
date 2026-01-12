import pygame

class MissionPanel:
    BASE_H = 720
    FONT_PATH = "assets/Font/FVF Fernando 08.ttf" 

    def __init__(self, screen_w, objective, icons):
        self.screen_w = screen_w
        self.objective = objective
        self.icons = icons 

        # ===== SIZE =====
        self.width = 240 
        self.height = 120 

        # ===== SLIDE =====
        self.hidden_x = -self.width
        self.visible_x = 0
        self.x = self.hidden_x
        self.target_x = self.hidden_x
        self.speed = 1200 
        self.opened = False

        # ===== FONT =====
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, 18)
            self.font_item = pygame.font.Font(self.FONT_PATH, 12)
        except:
            self.font_title = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_item = pygame.font.SysFont("Arial", 12)

        # ===== TOGGLE BUTTON =====
        self.btn_size = 40
        # Rect sẽ được cập nhật liên tục
        self.btn_rect = pygame.Rect(0, 0, self.btn_size, self.btn_size)

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
            self.btn_show.fill((255, 255, 0)) 
            self.btn_hide = pygame.Surface((self.btn_size, self.btn_size))
            self.btn_hide.fill((200, 200, 200))

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

    def recalc_height(self):
        """Tính chiều cao thực tế của Panel"""
        if not self.objective or not hasattr(self.objective, 'objectives'):
            return 80 

        items = self.objective.objectives
        if not items:
            return 80

        pad = 14
        gap = 6
        title_h = self.font_title.get_height()
        item_h = 32 

        total_h = (pad * 2) + title_h + gap + (len(items) * (item_h + gap))
        return total_h

    # =========================================================
    # SỬA LỖI TƯƠNG TÁC TẠI ĐÂY
    # =========================================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 1. Tính toán ngay lập tức vị trí hiện tại của nút
            # Lý do: Đôi khi update chạy sau handle_event, dẫn đến rect bị lệch 1 frame
            current_height = self.recalc_height()
            center_y = (current_height - self.btn_size) // 2
            
            # Tạo một rect tạm thời chính xác tại vị trí hình ảnh đang hiển thị
            # self.x là vị trí panel, self.width là chiều rộng panel
            btn_x = int(self.x + self.width)
            btn_y = int(center_y)
            
            check_rect = pygame.Rect(btn_x, btn_y, self.btn_size, self.btn_size)
            
            # 2. Kiểm tra va chạm với rect vừa tính
            if check_rect.collidepoint(event.pos):
                self.toggle()
                return True 
        return False

    def update(self, dt):
        # 1. Slide logic
        if self.x != self.target_x:
            if self.x < self.target_x:
                self.x += self.speed * dt
                if self.x > self.target_x: self.x = self.target_x
            elif self.x > self.target_x:
                self.x -= self.speed * dt
                if self.x < self.target_x: self.x = self.target_x

        # 2. Update Height
        self.height = self.recalc_height()

        # 3. Update Visual Rect (Để vẽ)
        self.btn_rect.x = int(self.x + self.width)
        center_y = (self.height - self.btn_size) // 2
        self.btn_rect.y = int(center_y)

    def draw(self, screen):
        if not self.objective:
            return

        objectives_data = getattr(self.objective, 'objectives', {})
        
        # Vẽ nền Panel
        panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180)) 
        pygame.draw.rect(panel, (255, 215, 0), (0, 0, self.width, self.height), 2)

        pad = 14
        gap = 6
        current_y = pad

        # Title
        title_surf = self.font_title.render("MISSION", True, (255, 215, 0))
        title_x = (self.width - title_surf.get_width()) // 2
        panel.blit(title_surf, (title_x, current_y))
        current_y += title_surf.get_height() + gap

        # Items
        icon_size = 28
        line_height = 32

        for name, data in objectives_data.items():
            current_val = data.get("collected", 0)
            target_val = data.get("required", 1)
            is_done = current_val >= target_val
            text_color = (100, 255, 100) if is_done else (255, 255, 255)

            name_surf = self.font_item.render(name, True, text_color)
            name_y = current_y + (line_height - name_surf.get_height()) // 2
            panel.blit(name_surf, (pad, name_y))

            count_str = f"{current_val}/{target_val}"
            count_surf = self.font_item.render(count_str, True, text_color)
            count_x = self.width - pad - count_surf.get_width()
            count_y = current_y + (line_height - count_surf.get_height()) // 2
            panel.blit(count_surf, (count_x, count_y))

            if name in self.icons:
                original_icon = self.icons[name]
                if original_icon:
                    scaled_icon = pygame.transform.scale(original_icon, (icon_size, icon_size))
                    icon_x = count_x - icon_size - 8
                    icon_y = current_y + (line_height - icon_size) // 2
                    panel.blit(scaled_icon, (icon_x, icon_y))

            current_y += line_height + gap

        # Vẽ Panel lên màn hình
        screen.blit(panel, (int(self.x), 0))

        # Vẽ Nút (sử dụng rect đã update)
        btn_img = self.btn_hide if self.opened else self.btn_show
        screen.blit(btn_img, self.btn_rect)