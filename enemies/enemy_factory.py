from enemies.enemy_base import EnemyBase
from enemies.enemy_config import ENEMY_CONFIG
from enemies.behaviors.patrol import PatrolBehavior
from enemies.behaviors.flying import FlyingBehavior
from enemies.behaviors.jumper import JumperBehavior
from enemies.behaviors.stationary import StationaryBehavior
from enemies.behaviors.shooter import ShooterBehavior
from enemies.behaviors.shell import ShellBehavior
from enemies.behaviors.ghost import GhostBehavior


def create_enemy(name, x, y):
    cfg = ENEMY_CONFIG[name].copy()
    cfg["name"] = name

    behavior_map = {
        "AngryPig": PatrolBehavior(x-80, x+80),
        "Chicken": PatrolBehavior(x-64, x+64),
        "Radish": PatrolBehavior(x-64, x+64),
        "Rino": PatrolBehavior(x-120, x+120),
        "Mushroom": PatrolBehavior(x-48, x+48),

        "Bat": FlyingBehavior(),
        "Bee": ShooterBehavior(90),
        "BlueBird": FlyingBehavior(),

        "Bunny": JumperBehavior(),
        "Slime": JumperBehavior(),

        "Plant": ShooterBehavior(120),
        "Trunk": ShooterBehavior(90),

        "Ghost": GhostBehavior(),

        "Snail": ShellBehavior(),
        "Turtle": ShellBehavior(),
    }

    return EnemyBase(x, y, cfg, behavior_map[name])
