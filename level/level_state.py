from enum import IntEnum


class LevelState(IntEnum):
    PLAYING = 0
    CHECKPOINT_ANIM = 1
    FADING_OUT = 2
    LOADING = 3
    FADING_IN = 4
