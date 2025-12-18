import pygame
class Animation:
    def __init__(self, sheet, frame_w, frame_h, speed, loop=True):
        self.frames = [
            sheet.subsurface((x, 0, frame_w, frame_h))
            for x in range(0, sheet.get_width(), frame_w)
        ]

        self.speed = speed
        self.loop = loop

        self.index = 0
        self.timer = 0
        self.finished = False

    # ================= CONTROL =================
    def reset(self):
        self.index = 0
        self.timer = 0
        self.finished = False

    # ================= UPDATE =================
    def update(self):
        if self.finished:
            return

        self.timer += self.speed
        if self.timer < 1:
            return

        self.timer = 0
        self.index += 1

        if self.index >= len(self.frames):
            if self.loop:
                self.index = 0
            else:
                self.index = len(self.frames) - 1
                self.finished = True

    # ================= RENDER =================
    def get_image(self):
        return self.frames[self.index]
