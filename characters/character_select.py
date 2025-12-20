import pygame
from player.animation import Animation
from characters.character_data import CHARACTERS


class CharacterSelect:
    def __init__(self, char_manager, item_manager):
        self.cm = char_manager
        self.item_manager = item_manager

        # ===== VIRTUAL RESOLUTION =====
        self.VW = 1280
        self.VH = 720
        self.ui_surface = pygame.Surface(
            (self.VW, self.VH), pygame.SRCALPHA
        )

        # ===== BACKGROUND =====
        self.bg = pygame.image.load(
            "assets/Background/Level/Green.png"
        ).convert()

        # ===== UI ASSETS =====
        self.card_img = pygame.image.load(
            "assets/Menu/Buttons/UI Border.png"
        ).convert_alpha()

        self.btn_buy = pygame.image.load(
            "assets/Menu/Buttons/Answer.png"
        ).convert_alpha()

        self.btn_back = pygame.image.load(
            "assets/Menu/Buttons/Previous.png"
        ).convert_alpha()

        # ===== FONTS =====
        self.title_font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 56
        )
        self.text_font = pygame.font.Font(
            "assets/Font/FVF Fernando 08.ttf", 25
        )

        # ===== SIZE CONFIG =====
        self.card_size = 170
        self.char_size = 140
        self.btn_size = (230, 72)

        # ===== RUNTIME RECTS =====
        self.cards = {}
        self.buy_buttons = {}
        self.back_rect = pygame.Rect(0, 0, 0, 0)

        # ===== LOAD CHARACTER ANIM =====
        self.anims = {}
        for name, info in CHARACTERS.items():
            self.anims[name] = Animation(
                pygame.image.load(info["idle"]).convert_alpha(),
                32, 32,
                speed=0.25,
                loop=True
            )

        # ===== LOAD FRUIT ICONS – ĐÚNG FRAME ĐẦU =====
        self.fruit_icons = {}
        base = "assets/Items/Fruits"

        FRAME_SIZE = 32
        FRAME_X = 32   # 🔥 offset đúng của frame đầu (quan trọng)

        for fruit in self.item_manager.count:
            sheet = pygame.image.load(
                f"{base}/{fruit}.png"
            ).convert_alpha()

            # cắt đúng frame đầu
            frame = sheet.subsurface(
                (FRAME_X, 0, FRAME_SIZE, FRAME_SIZE)
            )

            self.fruit_icons[fruit] = frame


    # ================= EVENT =================
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        # ===== LẤY THÔNG TIN SCALE HIỆN TẠI =====
        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()

        scale = min(sw / self.VW, sh / self.VH)
        draw_w = int(self.VW * scale)
        draw_h = int(self.VH * scale)

        offset_x = (sw - draw_w) // 2
        offset_y = (sh - draw_h) // 2

        # ===== CHUYỂN CHUỘT VỀ TỌA ĐỘ ẢO =====
        mx, my = event.pos
        mx = int((mx - offset_x) / scale)
        my = int((my - offset_y) / scale)

        # ===== CLICK BACK =====
        if self.back_rect.collidepoint(mx, my):
            pygame.event.post(
                pygame.event.Event(
                    pygame.KEYDOWN, key=pygame.K_ESCAPE
                )
            )
            return

        # ===== CLICK CARD =====
        for name, rect in self.cards.items():
            if rect.collidepoint(mx, my):
                if self.cm.is_owned(name):
                    self.cm.select(name)
                return

        # ===== CLICK BUY =====
        for name, rect in self.buy_buttons.items():
            if rect.collidepoint(mx, my):
                self.cm.buy(name)
                return


    # ================= DRAW =================
    def draw(self, screen):
        surf = self.ui_surface
        surf.fill((0, 0, 0, 0))
        sw, sh = self.VW, self.VH

        # ===== TILE BACKGROUND =====
        bg_w, bg_h = self.bg.get_size()
        for y in range(0, sh, bg_h):
            for x in range(0, sw, bg_w):
                surf.blit(self.bg, (x, y))

        # ===== TITLE =====
        title = self.title_font.render(
            "CHARACTER", True, (255, 215, 0)
        )
        surf.blit(
            title,
            title.get_rect(center=(sw // 2, 80))
        )

        # ===== BACK BUTTON =====
        back = pygame.transform.scale(self.btn_back, (56, 56))
        self.back_rect = back.get_rect(topleft=(30, 30))
        surf.blit(back, self.back_rect)

        # ===== GRID CONFIG =====
        cols = 4
        gap_x = 260

        ITEM_HEIGHT = (
            self.card_size
            + 10   # name
            + 44   # button
            + 30   # fruit row
        )

        rows = (len(CHARACTERS) + cols - 1) // cols
        gap_y = ITEM_HEIGHT

        SAFE_TOP = 100
        SAFE_BOTTOM = 40

        grid_height = rows * gap_y
        usable_h = sh - SAFE_TOP - SAFE_BOTTOM

        start_y = SAFE_TOP + max(
            0, (usable_h - grid_height) // 2
        )

        grid_width = (cols - 1) * gap_x
        start_x = sw // 2 - grid_width // 2

        self.cards.clear()
        self.buy_buttons.clear()

        # ===== DRAW ITEMS =====
        for i, name in enumerate(CHARACTERS):
            row = i // cols
            col = i % cols

            cx = start_x + col * gap_x
            item_top = start_y + row * gap_y

            # ----- CARD -----
            card = pygame.transform.scale(
                self.card_img,
                (self.card_size, self.card_size)
            )
            card_rect = card.get_rect(
                midtop=(cx, item_top)
            )
            surf.blit(card, card_rect)
            self.cards[name] = card_rect

            # ----- CHARACTER -----
            anim = self.anims[name]
            anim.update()
            img = pygame.transform.scale(
                anim.get_image(),
                (self.char_size, self.char_size)
            )

            if not self.cm.is_owned(name):
                overlay = pygame.Surface(
                    img.get_size(), pygame.SRCALPHA
                )
                overlay.fill((0, 0, 0, 120))
                img.blit(overlay, (0, 0))

            surf.blit(
                img,
                img.get_rect(center=card_rect.center)
            )

            # ----- SELECT BORDER -----
            if self.cm.selected == name:
                pygame.draw.rect(
                    surf,
                    (255, 215, 0),
                    card_rect.inflate(10, 10),
                    4
                )

            # ----- NAME -----
            name_txt = self.text_font.render(
                name, True, (255, 255, 255)
            )
            name_rect = name_txt.get_rect(
                midtop=(cx, card_rect.bottom + 6)
            )
            surf.blit(name_txt, name_rect)

            y_cursor = name_rect.bottom + 6

            # ----- STATUS / BUTTON -----
            if self.cm.selected == name:
                txt = self.text_font.render(
                    "ĐANG SỬ DỤNG", True, (255, 215, 0)
                )

                # 🔥 đẩy xuống ngang với nút MUA
                rect = txt.get_rect(
                    center=(cx, y_cursor + self.btn_size[1] // 2)
                )

                surf.blit(txt, rect)
                y_cursor = rect.bottom


            elif self.cm.is_owned(name):
                txt = self.text_font.render(
                    "SỬ DỤNG", True, (180, 255, 180)
                )
                rect = txt.get_rect(
                    center=(cx, y_cursor + self.btn_size[1] // 2)
                )
                surf.blit(txt, rect)
                y_cursor = rect.bottom

            else:
                price = CHARACTERS[name]["price"]
                btn = pygame.transform.scale(
                    self.btn_buy, self.btn_size
                )
                btn_rect = btn.get_rect(
                    midtop=(cx, y_cursor)
                )
                surf.blit(btn, btn_rect)

                price_txt = self.text_font.render(
                    f"MUA ({price})", True, (255, 255, 255)
                )
                surf.blit(
                    price_txt,
                    price_txt.get_rect(center=btn_rect.center)
                )

                self.buy_buttons[name] = btn_rect
                y_cursor = btn_rect.bottom

            # ===== FRUIT ROW – CENTER THEO CỬA SỔ =====
            if self.cm.selected == name:

                fruits = [
                    (fruit, self.item_manager.count[fruit])
                    for fruit in self.fruit_icons
                    if self.item_manager.count[fruit] > 0
                ]

                if fruits:
                    ICON_SIZE = 72
                    BLOCK_GAP = 44
                    TEXT_GAP = 12

                    # đo width text
                    sample_txt = self.text_font.render("99", True, (255, 255, 255))
                    BLOCK_W = ICON_SIZE + TEXT_GAP + sample_txt.get_width()

                    TOTAL_W = len(fruits) * BLOCK_W + (len(fruits) - 1) * BLOCK_GAP

                    # 🔥 TÂM CỬA SỔ ẢO
                    center_x = self.VW // 2
                    fx = center_x - TOTAL_W // 2

                    # 🔥 DỊCH XUỐNG DƯỚI CHO THOÁNG
                    fy = y_cursor + 26

                    for fruit, count in fruits:
                        # ICON
                        icon = pygame.transform.scale(
                            self.fruit_icons[fruit],
                            (ICON_SIZE, ICON_SIZE)
                        )
                        surf.blit(icon, (fx, fy))

                        # TEXT – căn giữa icon
                        txt = self.text_font.render(
                            str(count), True, (255, 255, 255)
                        )
                        txt_rect = txt.get_rect(
                            midleft=(fx + ICON_SIZE + TEXT_GAP,
                                    fy + ICON_SIZE // 2)
                        )
                        surf.blit(txt, txt_rect)

                        fx += BLOCK_W + BLOCK_GAP


        # ===== SCALE TO REAL SCREEN =====
        screen_w, screen_h = screen.get_size()
        scale = min(
            screen_w / self.VW,
            screen_h / self.VH
        )

        draw_w = int(self.VW * scale)
        draw_h = int(self.VH * scale)

        scaled = pygame.transform.scale(
            self.ui_surface, (draw_w, draw_h)
        )

        x = (screen_w - draw_w) // 2
        y = (screen_h - draw_h) // 2

        screen.fill((0, 0, 0))
        screen.blit(scaled, (x, y))
