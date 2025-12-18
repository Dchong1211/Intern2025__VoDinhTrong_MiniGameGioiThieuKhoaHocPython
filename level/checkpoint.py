import pygame
import os
class Checkpoint:
    SIZE = 64

    STATE_IDLE = "IDLE"
    STATE_WAIT = "WAIT"
    STATE_ACTIVATING = "ACTIVATING"
    STATE_ACTIVE = "ACTIVE"

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)

        base = "assets/Checkpoints/Checkpoint"

        self.no_flag = pygame.image.load(
            os.path.join(base, "Checkpoint (No Flag).png")
        ).convert_alpha()

        self.idle_frames = self._load_sheet(
            os.path.join(base, "Checkpoint (Flag Idle)(64x64).png")
        )

        self.activate_frames = self._load_sheet(
            os.path.join(base, "Checkpoint (Flag Out)(64x64).png")
        )

        # ===== STATE =====
        self.state = self.STATE_IDLE

        self.frames = self.idle_frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.08

        self.ready = False
        self.active = False
        self.waiting_quest = False
        self._finished = False
        self.player_inside = False
        self.pending_next_level = False

    # ==================================================
    def _load_sheet(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []

        sheet_w = sheet.get_width()
        for x in range(0, sheet_w, self.SIZE):
            frame = sheet.subsurface((x, 0, self.SIZE, self.SIZE))
            frames.append(frame)

        return frames

    # ================= PUBLIC API =====================
    def on_player_touch(self, quest_panel):
        if not self.ready or self.active or self.waiting_quest:
            return

        self.waiting_quest = True
        self.state = self.STATE_WAIT
        quest_panel.open()

    def activate(self):
        if self.active:
            return

        self.active = True
        self.ready = True
        self.waiting_quest = False

        self.state = self.STATE_ACTIVATING
        self.frames = self.activate_frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self._finished = False
        self.pending_next_level = True


    def force_active(self):
        self.active = True
        self.ready = True
        self.waiting_quest = False

        self.state = self.STATE_ACTIVE
        self.frames = self.idle_frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self._finished = True

    def animation_finished(self):
        return self._finished

    # ================= UPDATE =========================
    def update(self, dt):
        if self.state == self.STATE_ACTIVATING:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index += 1

                if self.frame_index >= len(self.frames):
                    self.state = self.STATE_ACTIVE
                    self.frames = self.idle_frames
                    self.frame_index = 0
                    self._finished = True

                    if self.pending_next_level:
                        self.pending_next_level = False
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT,
                                {"action": "NEXT_LEVEL"}
                            )
                        )

        elif self.state == self.STATE_ACTIVE:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    # ================= DRAW ===========================
    def draw(self, surf):
        if self.state in (self.STATE_IDLE, self.STATE_WAIT):
            surf.blit(self.no_flag, self.rect.topleft)
        else:
            surf.blit(self.frames[self.frame_index], self.rect.topleft)