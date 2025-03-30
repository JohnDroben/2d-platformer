from enum import Enum, auto

class Action(Enum):
    """Класс для описания возможных действий персонажа"""
    IDLE = auto()
    MOVE = auto()
    JUMP = auto()
    SIT = auto()
    SIT_MOVE = auto()
    SIT_IDLE = auto()
#    FALL = auto()
#    ATTACK = auto()
#    HURT = auto()
#    DIE = auto()

    def __str__(self):
        return self.name.lower()