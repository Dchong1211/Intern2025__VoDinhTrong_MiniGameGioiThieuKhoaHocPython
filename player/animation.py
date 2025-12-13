import pygame

class Animation:
    def __init__(self, sheet, frame_w, frame_h, speed, loop=True):
        self.frames = []
        self.speed = speed
        self.loop = loop
        self.index = 0

        sheet_w = sheet.get_width()

        for x in range(0, sheet_w, frame_w):
            frame = sheet.subsurface((x, 0, frame_w, frame_h))
            self.frames.append(frame)

    def reset(self):
        self.index = 0

    def update(self):
        self.index += self.speed
        if self.index >= len(self.frames):
            self.index = 0 if self.loop else len(self.frames) - 1

    def get_image(self):
        return self.frames[int(self.index)]
