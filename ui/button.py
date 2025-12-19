import pygame


class Button:
    def __init__(
        self,
        image,
        anchor=("center", "center"),
        offset=(0, 0),
        origin=None
    ):
        self.image = image

        # ===== MODE =====
        self.anchor = anchor        # screen-based (cũ)
        self.origin = origin        # panel-based (mới)

        self.base_offset = offset

        # ===== BOUNCE =====
        self.offset_y = 0.0
        self.target_offset_y = 0.0
        self.bounce_speed = 12.0

        self.rect = self.image.get_rect()

    # =====================================
    def handle_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.target_offset_y = -14
        else:
            self.target_offset_y = 0

    # =====================================
    def _compute_rect(self, screen):
        ox, oy = self.base_offset

        # ===== MODE 1: PANEL / ORIGIN =====
        if self.origin is not None:
            px, py = self.origin
            return self.image.get_rect(
                center=(px + ox, py + oy + int(self.offset_y))
            )

        # ===== MODE 2: SCREEN / ANCHOR =====
        sw, sh = screen.get_size()
        ax, ay = self.anchor

        x = sw // 2 if ax == "center" else (0 if ax == "left" else sw)
        y = sh // 2 if ay == "center" else (0 if ay == "top" else sh)

        return self.image.get_rect(
            center=(x + ox, y + oy + int(self.offset_y))
        )

    # =====================================
    def update(self, dt, screen):
        # spring Y
        self.offset_y += (
            self.target_offset_y - self.offset_y
        ) * self.bounce_speed * dt

        self.rect = self._compute_rect(screen)

    # =====================================
    def update_layout(self, screen):
        """
        BACKWARD COMPAT:
        - Dùng cho LevelSelect, MainMenu cũ
        - Không animation, chỉ set rect
        """
        self.rect = self._compute_rect(screen)

    # =====================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    # =====================================
    def draw(self, screen):
        screen.blit(self.image, self.rect)
