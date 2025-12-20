class PatrolBehavior:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.dir = 1

    def update(self, player, tiles):
        e = self.owner
        e.state = "run"
        e.rect.x += e.speed * self.dir

        if e.rect.left <= self.left or e.rect.right >= self.right:
            self.dir *= -1
