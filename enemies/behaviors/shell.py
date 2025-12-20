class ShellBehavior:
    def __init__(self):
        self.shell = False

    def update(self, player, tiles):
        e = self.owner

        if self.shell:
            e.state = "shell"
            e.speed = 0
        else:
            e.state = "idle"

    def stomp(self):
        self.shell = True
