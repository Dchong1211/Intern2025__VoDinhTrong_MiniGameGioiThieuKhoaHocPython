from enum import Enum

class GameState(Enum):
    MENU = "MENU"
    LEVEL_SELECT = "LEVEL_SELECT"
    CHARACTER_SELECT = "CHARACTER_SELECT"

    LEVEL_CODE = "LEVEL_CODE"     # Phase 1: học + viết code
    LEVEL_PLAY = "LEVEL_PLAY"     # Phase 2: chơi platform

    PAUSE = "PAUSE"
