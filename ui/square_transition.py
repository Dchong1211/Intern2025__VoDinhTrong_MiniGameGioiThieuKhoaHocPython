import pygame
from enum import Enum


class TransitionPhase(Enum):
    IDLE = 0
    CLOSING = 1
    CLOSED = 2
    OPENING = 3


class SquareTransition:
    def __init__(self, size, duration=0.7, hold_time=0.15):
        self.width, self.height = size
        self.duration = duration
        self.hold_time = hold_time

        self.phase = TransitionPhase.IDLE
        self.progress = 0.0
        self.hold_timer = 0.0

        self.thickness = 0
        self.max_thickness = max(self.width, self.height) // 2

    # ================= LAYOUT =================
    def resize(self, size):
        self.width, self.height = size
        self.max_thickness = max(self.width, self.height) // 2
        self.thickness = min(self.thickness, self.max_thickness)

    # ================= CONTROL =================
    def start_close(self):
        self.phase = TransitionPhase.CLOSING
        self.progress = 0.0
        self.hold_timer = 0.0
        self.thickness = 0

    def start_open(self):
        self.phase = TransitionPhase.OPENING
        self.progress = 0.0

    # ================= UPDATE =================
    def update(self, dt):
        if self.phase == TransitionPhase.IDLE:
            return

        if self.phase == TransitionPhase.CLOSING:
            self._update_closing(dt)

        elif self.phase == TransitionPhase.CLOSED:
            self._update_hold(dt)

        elif self.phase == TransitionPhase.OPENING:
            self._update_opening(dt)

    def _update_closing(self, dt):
        self.progress = min(self.progress + dt / self.duration, 1.0)
        eased = self.progress ** 2  # ease-in
        self.thickness = int(self.max_thickness * eased)

        if self.progress >= 1.0:
            self.thickness = self.max_thickness
            self.phase = TransitionPhase.CLOSED
            self.hold_timer = 0.0

    def _update_hold(self, dt):
        self.hold_timer += dt
        if self.hold_timer >= self.hold_time:
            self.start_open()

    def _update_opening(self, dt):
        self.progress = min(self.progress + dt / self.duration, 1.0)
        eased = 1 - (1 - self.progress) ** 2  # ease-out
        self.thickness = int(self.max_thickness * (1 - eased))

        if self.progress >= 1.0:
            self.thickness = 0
            self.phase = TransitionPhase.IDLE

    # ================= QUERY =================
    def is_closed(self):
        return self.phase == TransitionPhase.CLOSED

    def is_active(self):
        return self.phase != TransitionPhase.IDLE

    # ================= DRAW =================
    def draw(self, surface):
        if self.phase == TransitionPhase.IDLE:
            return

        t = self.thickness
        w, h = self.width, self.height

        rects = (
            pygame.Rect(0, 0, w, t),               # top
            pygame.Rect(0, h - t, w, t),            # bottom
            pygame.Rect(0, t, t, h - 2 * t),         # left
            pygame.Rect(w - t, t, t, h - 2 * t),     # right
        )

        for r in rects:
            pygame.draw.rect(surface, (0, 0, 0), r)
