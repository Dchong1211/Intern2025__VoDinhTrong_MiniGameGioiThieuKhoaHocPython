class GhostBehavior:
    def __init__(self, timer=120):
        self.timer = timer
        self.counter = 0
        self.visible = True

    def update(self, player, tiles):
        e = self.owner
        self.counter += 1

        if self.counter >= self.timer:
            self.visible = not self.visible
            self.counter = 0

        if self.visible:
            e.state = "idle"
        else:
            e.state = "disappear"
