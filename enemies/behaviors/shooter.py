class ShooterBehavior:
    def __init__(self, cooldown):
        self.cooldown = cooldown
        self.timer = 0

    def update(self, player, tiles):
        e = self.owner
        e.state = "attack" if "attack" in e.animations else "idle"

        self.timer += 1
        if self.timer >= self.cooldown:
            self.timer = 0
            # spawn bullet ở đây
