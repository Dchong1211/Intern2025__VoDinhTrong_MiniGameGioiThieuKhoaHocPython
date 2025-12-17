class Skills:
    def __init__(self):
        self.move = True
        self.jump = True
        self.double_jump = True
        self.wall_slide = False
        self.wall_jump = False
        self.dash = False

    def unlock(self, skill_name):
        if hasattr(self, skill_name):
            setattr(self, skill_name, True)
            print(f"[SKILL UNLOCKED] {skill_name}")
