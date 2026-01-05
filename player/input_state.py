# input_state.py
class InputState:
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False
        self.dash = False
        self.down = False

        # dùng để bắt "pressed"
        self._prev_jump = False
        self._prev_dash = False

    def jump_pressed(self):
        pressed = self.jump and not self._prev_jump
        self._prev_jump = self.jump
        return pressed

    def dash_pressed(self):
        pressed = self.dash and not self._prev_dash
        self._prev_dash = self.dash
        return pressed
    