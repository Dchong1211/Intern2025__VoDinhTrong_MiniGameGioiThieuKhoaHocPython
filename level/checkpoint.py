import pygame
import os


class Checkpoint:
    def __init__(self, x, y, w=64, h=64):
        self.rect = pygame.Rect(x, y, w, h)

        base = "assets/Checkpoints/Checkpoint"

        # ===== LOAD SPRITES =====
        self.no_flag = pygame.image.load(
            os.path.join(base, "Checkpoint (No Flag).png")
        ).convert_alpha()

        self.idle_frames = self.load_sheet(
            os.path.join(base, "Checkpoint (Flag Idle)(64x64).png"),
            64, 64
        )

        self.active_frames = self.load_sheet(
            os.path.join(base, "Checkpoint (Flag Out)(64x64).png"),
            64, 64
        )

        # ===== VISUAL STATE =====
        self.state = "NO_FLAG"   # NO_FLAG | WAIT_QUEST | ACTIVATING | ACTIVE
        self.frames = None
        self.frame_index = 0
        self.player_inside = False

        self.anim_speed = 0.06
        self.anim_timer = 0
        self.finished = False

        # ===== LOGIC STATE =====
        self.ready = False        # objective đã xong chưa
        self.active = False       # checkpoint đã active chưa
        self.waiting_quest = False

    # ======================================================
    def load_sheet(self, path, fw, fh):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), fw):
            frame = sheet.subsurface((x, 0, fw, fh))
            frames.append(frame)
        return frames

    # ======================================================
    def on_player_touch(self, quest_panel):
        """
        Gọi khi player chạm checkpoint
        """
        # ❌ nếu chưa đủ điều kiện
        if not self.ready:
            return

        # ❌ nếu đã active thì khỏi hỏi quest
        if self.active:
            return

        # mở quest
        if not self.waiting_quest:
            self.waiting_quest = True
            self.state = "WAIT_QUEST"
            quest_panel.open()

    # ======================================================
    def activate(self):
        """
        Gọi KHI TRẢ LỜI ĐÚNG QUEST
        """
        if self.active:
            return

        self.active = True
        self.ready = True               # 🔥 CỰC KỲ QUAN TRỌNG
        self.state = "ACTIVATING"
        self.frames = self.active_frames
        self.frame_index = 0
        self.anim_timer = 0
        self.finished = False
        self.waiting_quest = False

    # ======================================================
    def force_active(self):
        """
        Level đã hoàn thành từ trước → chơi lại
        """
        self.active = True
        self.ready = True               # 🔥 FIX LỖI ĐỨNG YÊN
        self.state = "ACTIVE"
        self.frames = self.idle_frames
        self.frame_index = 0
        self.anim_timer = 0
        self.finished = True
        self.waiting_quest = False

    # ======================================================
    def update(self, dt):
        if self.state == "ACTIVATING":
            self.anim_timer += dt

            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index += 1

                if self.frame_index >= len(self.frames):
                    self.state = "ACTIVE"
                    self.frames = self.idle_frames
                    self.frame_index = 0
                    self.finished = True

        elif self.state == "ACTIVE":
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    # ======================================================
    def animation_finished(self):
        return self.finished

    # ======================================================
    def draw(self, surf):
        if self.state in ("NO_FLAG", "WAIT_QUEST"):
            surf.blit(self.no_flag, self.rect.topleft)
        else:
            surf.blit(self.frames[self.frame_index], self.rect.topleft)