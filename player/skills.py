class Skills:
    DEFAULT = {
        "move": True,
        "jump": True,
        "double_jump": True,
        "wall_slide": False,
        "wall_jump": False,
        "dash": False,
    }

    def __init__(self):
        self._skills = self.DEFAULT.copy()

    # ================= QUERY =================
    def has(self, name):
        return self._skills.get(name, False)

    def all(self):
        return self._skills.copy()

    # ================= MODIFY =================
    def unlock(self, name):
        if name in self._skills:
            self._skills[name] = True
            return True
        return False
