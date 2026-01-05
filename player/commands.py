# player/commands.py

class BaseCommand:
    def start(self, player):
        pass

    def update(self, player):
        return True


# ================= MOVE =================
class MoveCommand(BaseCommand):
    def __init__(self, direction, steps):
        self.direction = direction          # "left" | "right"
        self.steps = max(1, steps)
        self.step_size = 32                 # 1 bước = 32px
        self.moved = 0
        self.started = False

    def start(self, player):
        if self.direction == "right":
            player.facing_right = True
            player.vel_x = player.speed
        else:
            player.facing_right = False
            player.vel_x = -player.speed
        self.started = True

    def update(self, player):
        # tích lũy quãng đường đã đi
        self.moved += abs(player.vel_x)

        if self.moved >= self.steps * self.step_size:
            player.vel_x = 0
            return True

        return False


# ================= JUMP =================
class JumpCommand(BaseCommand):
    def __init__(self):
        self.done = False

    def start(self, player):
        # chỉ cho jump khi đang đứng đất
        if player.on_ground:
            player.vel_y = player.jump_force
            player.jump_count = 1
        self.done = True

    def update(self, player):
        # jump là instant → xong ngay
        return self.done


# ================= WAIT =================
class WaitCommand(BaseCommand):
    def __init__(self, time_sec):
        self.timer = max(0.0, float(time_sec))

    def start(self, player):
        player.vel_x = 0

    def update(self, player):
        self.timer -= 1 / 60  # assume 60 FPS
        return self.timer <= 0
