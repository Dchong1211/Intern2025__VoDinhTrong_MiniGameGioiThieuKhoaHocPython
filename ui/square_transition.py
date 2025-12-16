import pygame


class SquareTransition:
    def __init__(self, size, duration=0.7, hold_time=0.15):
        self.w, self.h = size
        self.duration = duration
        self.hold_time = hold_time

        self.phase = "idle"          # idle | closing | closed | opening
        self.t = 0.0
        self.hold_t = 0.0

        self.thickness = 0
        self.max_thickness = max(self.w, self.h) // 2

    # =============================
    def resize(self, size):
        self.w, self.h = size
        self.max_thickness = max(self.w, self.h) // 2

        # giữ thickness trong giới hạn mới
        if self.thickness > self.max_thickness:
            self.thickness = self.max_thickness

    # =============================
    def start_close(self):
        self.phase = "closing"
        self.t = 0.0
        self.hold_t = 0.0
        self.thickness = 0

    def start_open(self):
        self.phase = "opening"
        self.t = 0.0

    # =============================
    def update(self, dt):
        if self.phase == "idle":
            return

        # ---------- CLOSING ----------
        if self.phase == "closing":
            self.t += dt
            p = min(self.t / self.duration, 1.0)

            # ease-in (thu mượt)
            eased = p * p
            self.thickness = int(self.max_thickness * eased)

            if p >= 1.0:
                self.thickness = self.max_thickness
                self.phase = "closed"
                self.hold_t = 0.0

        # ---------- HOLD (GIỮ ĐEN) ----------
        elif self.phase == "closed":
            self.hold_t += dt
            if self.hold_t >= self.hold_time:
                self.start_open()

        # ---------- OPENING ----------
        elif self.phase == "opening":
            self.t += dt
            p = min(self.t / self.duration, 1.0)

            # ease-out (mở mượt)
            eased = 1 - (1 - p) * (1 - p)
            self.thickness = int(self.max_thickness * (1 - eased))

            if p >= 1.0:
                self.thickness = 0
                self.phase = "idle"

    # =============================
    def is_closed(self):
        return self.phase == "closed"

    # =============================
    def draw(self, screen):
        if self.phase == "idle":
            return

        t = self.thickness

        rects = [
            pygame.Rect(0, 0, self.w, t),                  # trên
            pygame.Rect(0, self.h - t, self.w, t),         # dưới
            pygame.Rect(0, t, t, self.h - 2 * t),          # trái
            pygame.Rect(self.w - t, t, t, self.h - 2 * t)  # phải
        ]

        for r in rects:
            pygame.draw.rect(screen, (0, 0, 0), r)
