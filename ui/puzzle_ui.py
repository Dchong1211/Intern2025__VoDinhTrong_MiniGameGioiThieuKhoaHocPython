import pygame
import random
import os

class PuzzleUI:
    BOX_SIZE = 80
    GAP = 10

    def __init__(self, player, skill_name, fragments):
        self.player = player
        self.skill_name = skill_name
        self.fragments = fragments
        self.active = True

        surf = pygame.display.get_surface()
        self.sw, self.sh = surf.get_width(), surf.get_height()

        self.total = len(fragments)

        # ================= LOAD PIXEL FONT TTF ==================
        base = os.path.dirname(os.path.dirname(__file__))
        font_path = os.path.join(base, "assets\Menu\Text\FVF Fernando 08.ttf")

        self.font_big = pygame.font.Font(font_path, 25)   # Title + Button
        self.font_small = pygame.font.Font(font_path, 20) # Text trong mảnh puzzle

        # ================= CREATE TARGET BOXES ==================
        center_x = self.sw // 2
        center_y = self.sh // 2 - 40

        self.targets = []
        total_width = self.total * (self.BOX_SIZE + self.GAP)

        for i in range(self.total):
            x = center_x - total_width // 2 + i * (self.BOX_SIZE + self.GAP)
            y = center_y
            self.targets.append(pygame.Rect(x, y, self.BOX_SIZE, self.BOX_SIZE))

        # ================= CREATE PIECES ==================
        self.pieces = []

        indices = list(range(self.total))
        random.shuffle(indices)

        spawn_y = 100
        spawn_width = self.total * (self.BOX_SIZE + self.GAP)
        spawn_start_x = center_x - spawn_width // 2

        for pos, idx in enumerate(indices):

            frag = self.fragments[idx]
            code_text = str(frag.code)

            px = spawn_start_x + pos * (self.BOX_SIZE + self.GAP)
            py = spawn_y

            rect = pygame.Rect(px, py, self.BOX_SIZE, self.BOX_SIZE)

            surf_box = pygame.Surface((self.BOX_SIZE, self.BOX_SIZE), pygame.SRCALPHA)
            surf_box.fill((230, 230, 230))

            # Render text bằng font pixel nhỏ
            text_img = self.font_small.render(code_text, True, (0, 0, 0))
            surf_box.blit(
                text_img,
                (
                    self.BOX_SIZE//2 - text_img.get_width()//2,
                    self.BOX_SIZE//2 - text_img.get_height()//2
                )
            )

            self.pieces.append({
                "index": frag.index,
                "rect": rect,
                "img": surf_box,
                "locked": False
            })

        self.dragging = None
        self.drag_offset = (0, 0)

        # Nút GHÉP
        self.button_rect = pygame.Rect(self.sw//2 - 100, self.sh//2 + 120, 200, 60)

    # ---------------------- EVENTS ----------------------
    def handle_event(self, e):
        if not self.active:
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos

            if self.button_rect.collidepoint(mx, my):
                self.check_result()
                return

            for p in reversed(self.pieces):
                if p["rect"].collidepoint(mx, my):
                    self.dragging = p
                    self.drag_offset = (p["rect"].x - mx, p["rect"].y - my)
                    p["drag_start"] = p["rect"].topleft

                    self.pieces.remove(p)
                    self.pieces.append(p)
                    break

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.dragging:
                self.snap_piece(self.dragging)
                self.dragging = None

        elif e.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx, my = e.pos
                self.dragging["rect"].x = mx + self.drag_offset[0]
                self.dragging["rect"].y = my + self.drag_offset[1]

    # ---------------------- SNAP ----------------------
    def snap_piece(self, piece):
        old_pos = piece.get("drag_start", piece["rect"].topleft)
        hit_any = False

        for target in self.targets:
            if piece["rect"].colliderect(target.inflate(20, 20)):
                hit_any = True
                tx, ty = target.topleft

                other = None
                for p in self.pieces:
                    if p is piece:
                        continue
                    if p["rect"].colliderect(target):
                        other = p
                        break

                if other:
                    piece["rect"].topleft = (tx, ty)
                    other["rect"].topleft = old_pos
                else:
                    piece["rect"].topleft = (tx, ty)

                break

        if not hit_any:
            piece["rect"].topleft = old_pos

        if "drag_start" in piece:
            del piece["drag_start"]

    # ---------------------- CHECK ----------------------
    def check_result(self):
        correct = True

        for p in self.pieces:
            correct_pos = self.targets[p["index"]].topleft
            if p["rect"].topleft != correct_pos:
                correct = False
                break

        if correct:
            print(f">>> Puzzle đúng → Unlock skill: {self.skill_name}")
            self.player.unlock_skill(self.skill_name)
            self.active = False
        else:
            print(">>> Sai thứ tự!")

    def update(self):
        pass

    # ---------------------- DRAW ----------------------
    def draw(self, surf):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        # TITLE – font pixel tiếng Việt
        title = self.font_big.render("Sắp xếp đúng thứ tự!", True, (255, 255, 255))
        surf.blit(title, (
            self.sw//2 - title.get_width()//2,
            self.sh//2 - 170
        ))

        # Targets
        for t in self.targets:
            pygame.draw.rect(surf, (200, 200, 200), t, 3)

        # Pieces
        for p in self.pieces:
            surf.blit(p["img"], p["rect"])

        # Button
        pygame.draw.rect(surf, (60, 180, 60), self.button_rect)
        pygame.draw.rect(surf, (0, 0, 0), self.button_rect, 3)

        btn_text = self.font_big.render("G H É P", True, (255, 255, 255))
        surf.blit(btn_text, (
            self.button_rect.centerx - btn_text.get_width()//2,
            self.button_rect.centery - btn_text.get_height()//2
        ))
