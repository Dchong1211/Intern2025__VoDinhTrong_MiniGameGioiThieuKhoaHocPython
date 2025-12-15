class Progress:
    def __init__(self):
        self.unlocked_level = 1  # ban đầu chỉ mở level 1

    def is_unlocked(self, level):
        return level <= self.unlocked_level

    def unlock_next(self, level):
        if level == self.unlocked_level:
            self.unlocked_level += 1
