# gameplay/code_runner.py

from player.commands import (
    MoveCommand,
    JumpCommand,
    WaitCommand
)


class CodeRunner:
    def __init__(self, player):
        self.player = player
        self.queue = []
        self.running = False

    # ================= LOAD CODE =================
    def load(self, lines):
        if not self.player:
            return

        self.queue.clear()
        self.running = True
        self.player.code_active = True

        for line in lines:
            self._parse_line(line.strip())

        # DEBUG (có thể xóa sau)
        print("[CodeRunner] QUEUE:", self.queue)

    # ================= PARSER =================
    def _parse_line(self, line):
        if not line or line.startswith("#"):
            return

        # move_right(3)
        if line.startswith("move_right"):
            n = self._get_number(line, default=1)
            self.queue.append(MoveCommand("right", n))

        # move_left(2)
        elif line.startswith("move_left"):
            n = self._get_number(line, default=1)
            self.queue.append(MoveCommand("left", n))

        # jump()
        elif line.startswith("jump"):
            self.queue.append(JumpCommand())

        # wait(1.5)
        elif line.startswith("wait"):
            t = self._get_number(line, default=1)
            self.queue.append(WaitCommand(t))

        else:
            print("[CodeRunner] UNKNOWN COMMAND:", line)

    def _get_number(self, line, default=1):
        if "(" not in line or ")" not in line:
            return default
        try:
            return int(float(line[line.find("(")+1 : line.find(")")]))
        except:
            return default

    # ================= UPDATE =================
    def update(self):
        if not self.running:
            return

        # nếu player chưa có command đang chạy → cấp command mới
        if not self.player.current_command and self.queue:
            cmd = self.queue.pop(0)
            self.player.enqueue_command(cmd)

        # CHỈ KẾT THÚC khi:
        # - không còn command trong CodeRunner
        # - không còn command trong Player
        # - player đã xử lý xong command hiện tại
        if (
            not self.queue
            and not self.player.command_queue
            and not self.player.current_command
        ):
            self.running = False
            self.player.code_active = False
