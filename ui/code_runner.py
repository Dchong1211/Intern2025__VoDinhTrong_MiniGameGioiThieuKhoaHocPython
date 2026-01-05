from level.level_manager import ControlPhase


class CodeRunner:
    def __init__(self, level_manager):
        self.level_manager = level_manager

        self.lines = []
        self.current_line = 0

        self.waiting = False
        self.wait_timer = 0
        self.step_delay = 0.25

        self.finished = True
        self.error = None

    def load(self, lines):
        self.lines = lines
        self.current_line = 0
        self.finished = False
        self.waiting = False
        self.wait_timer = 0
        self.error = None

        # 🔵 chuyển sang CODE phase
        self.level_manager.control_phase = ControlPhase.CODE

    def update(self, dt):
        if self.finished:
            return

        if self.waiting:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.waiting = False
            return

        if self.current_line >= len(self.lines):
            self.finished = True
            # 🟢 trả lại quyền cho PLAY phase
            self.level_manager.control_phase = ControlPhase.PLAY
            return

        try:
            self._exec_line(self.lines[self.current_line])
            self.current_line += 1
            self.waiting = True
            self.wait_timer = self.step_delay
        except Exception as e:
            self.error = str(e)
            self.finished = True
            self.level_manager.control_phase = ControlPhase.PLAY

    def _exec_line(self, line):
        exec(line, {}, self.level_manager.get_code_env())
