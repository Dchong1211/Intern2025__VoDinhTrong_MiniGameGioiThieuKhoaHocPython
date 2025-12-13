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

        # ===== STATE =====
        self.state = "NO_FLAG"
        self.frames = None
        self.frame_index = 0

        self.anim_speed = 0.05
        self.anim_timer = 0

        self.finished = False

    # ======================================================
    def load_sheet(self, path, fw, fh):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), fw):
            frame = sheet.subsurface((x, 0, fw, fh))
            frames.append(frame)
        return frames

    # ======================================================
    def activate(self):
        if self.state == "NO_FLAG":
            self.state = "ACTIVATING"
            self.frames = self.active_frames
            self.frame_index = 0
            self.anim_timer = 0
            self.finished = False

    # ======================================================
    def update(self, dt):
        if self.state == "ACTIVATING":
            self.anim_timer += dt

            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index += 1

                if self.frame_index >= len(self.frames):
                    # animation xong
                    self.state = "ACTIVE"
                    self.frames = self.idle_frames
                    self.frame_index = 0
                    self.finished = True

        elif self.state == "ACTIVE":
            # idle animation loop
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    # ======================================================
    def animation_finished(self):
        return self.finished

    # ======================================================
    def draw(self, surf):
        if self.state == "NO_FLAG":
            surf.blit(self.no_flag, (self.rect.x, self.rect.y))
        else:
            image = self.frames[self.frame_index]
            surf.blit(image, (self.rect.x, self.rect.y))
