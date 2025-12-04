# player/animation.py
class Animation:
    def __init__(self, sprite_sheet, frame_width, frame_height, speed=0.15):
        self.frames = []
        self.speed = speed
        self.index = 0

        sheet_width = sprite_sheet.get_width()

        for x in range(0, sheet_width, frame_width):
            frame = sprite_sheet.subsurface((x, 0, frame_width, frame_height))
            self.frames.append(frame)

        self.current_frame = self.frames[0]

    def reset(self):
        self.index = 0
        self.current_frame = self.frames[0]

    def update(self):
        self.index += self.speed
        if self.index >= len(self.frames):
            self.index = 0
        self.current_frame = self.frames[int(self.index)]

    def get_image(self):
        return self.current_frame
