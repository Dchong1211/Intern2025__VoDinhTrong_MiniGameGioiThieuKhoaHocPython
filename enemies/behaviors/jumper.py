class JumperBehavior:
    def __init__(self, force=-10):
        self.force = force

    def update(self, player, tiles):
        e = self.owner
        e.state = "idle"

        if e.on_ground:
            e.vel_y = self.force
