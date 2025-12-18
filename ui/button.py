import pygame


class Button:
    def __init__(self, image, anchor=("center", "center"), offset=(0, 0)):
        self.image = image
        self.anchor = anchor

        self.base_offset = offset
        self.offset_y = 0.0
        self.target_offset_y = 0.0

        self.bounce_speed = 12.0
        self.rect = self.image.get_rect()

    # =====================================
    def update_layout(self, screen):
        sw, sh = screen.get_size()
        ax, ay = self.anchor
        ox, oy = self.base_offset

        x = sw // 2 if ax == "center" else (0 if ax == "left" else sw)
        y = sh // 2 if ay == "center" else (0 if ay == "top" else sh)

        self.rect = self.image.get_rect(
            center=(x + ox, y + oy + int(self.offset_y))
        )

    # =====================================
    def handle_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.target_offset_y = -14
        else:
            self.target_offset_y = 0

    # =====================================
    def update(self, dt, screen):
        # spring Y
        self.offset_y += (
            self.target_offset_y - self.offset_y
        ) * self.bounce_speed * dt

        self.update_layout(screen)

    # =====================================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    # =====================================
    def draw(self, screen):
        screen.blit(self.image, self.rect)
