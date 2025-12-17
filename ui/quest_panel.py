import pygame

class QuestPanel:
    def __init__(self, quest_manager, skills, checkpoint):
        self.qm = quest_manager
        self.skills = skills
        self.checkpoint = checkpoint

        self.visible = False
        self.selected = 0
        self.keys = ["A", "B", "C", "D"]

        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 28)

        # panel rect (giữa màn hình)
        self.panel_rect = pygame.Rect(0, 0, 520, 260)

    def open(self):
        self.visible = True
        self.selected = 0

    def close(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_LEFT and self.selected % 2 == 1:
            self.selected -= 1
        elif event.key == pygame.K_RIGHT and self.selected % 2 == 0:
            self.selected += 1
        elif event.key == pygame.K_UP and self.selected >= 2:
            self.selected -= 2
        elif event.key == pygame.K_DOWN and self.selected <= 1:
            self.selected += 2
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.submit()

    def submit(self):
        chosen = self.keys[self.selected]
        correct = self.qm.answer()

        if chosen == correct:
            if self.qm.is_key():
                skill = self.qm.unlock_skill()
                if skill:
                    self.skills.unlock(skill)

            self.checkpoint.activate()  # <<< CHỖ NÀY
            self.close()
        else:
            print("Sai rồi 😢")

    def draw(self, surf):
        if not self.visible:
            return

        sw, sh = surf.get_size()
        self.panel_rect.center = (sw // 2, sh // 2)

        # nền mờ
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surf.blit(overlay, (0, 0))

        # panel
        pygame.draw.rect(surf, (30, 30, 30), self.panel_rect, border_radius=10)
        pygame.draw.rect(surf, (200, 200, 200), self.panel_rect, 2, border_radius=10)

        # text câu hỏi
        title = self.title_font.render(self.qm.text(), True, (255, 255, 255))
        surf.blit(title, (self.panel_rect.x + 20, self.panel_rect.y + 20))

        # vẽ đáp án (2 cột × 2 hàng)
        choices = self.qm.choices()
        col_w = self.panel_rect.width // 2
        start_y = self.panel_rect.y + 80
        row_h = 40

        for i, key in enumerate(self.keys):
            row = i // 2
            col = i % 2

            x = self.panel_rect.x + col * col_w + 20
            y = start_y + row * row_h

            rect = pygame.Rect(x - 10, y - 6, col_w - 40, 32)

            if self.selected == i:
                pygame.draw.rect(surf, (80, 80, 160), rect, border_radius=6)

            text = f"[{key}] {choices[key]}"
            txt = self.font.render(text, True, (255, 255, 255))
            surf.blit(txt, (x, y))
