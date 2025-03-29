from enum import Enum, auto

class Action(Enum):
    """Класс для описания возможных действий персонажа"""
    IDLE = auto()
    MOVE = auto()
    JUMP = auto()
    SIT = auto()
#    FALL = auto()
#    ATTACK = auto()
#    HURT = auto()
#    DIE = auto()

    def __str__(self):
        return self.name.lower()