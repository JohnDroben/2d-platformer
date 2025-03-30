from enum import Enum, auto

class ObjectType(Enum):
    """Класс для типов игровых объектов"""
    PLAYER = auto()  # Игрок
    ENEMY = auto()  # Враг

    PLATFORM = auto()  # Платформа
    PASSABLE_PLATFORM = auto()  # Платформа, сквозь которую можно прыгать снизу
    MOVING_PLATFORM = auto()  # Движущаяся платформа
    OBSTACLE = auto()  # Препятствие
    PIT = auto()  # Яма

    SPIKE = auto()  # Шипы
    CIRCULAR_SAW = auto()  # Дисковая пила

    COIN = auto()  # Монета
    ARTIFACT = auto()  # Артефакт
    PORTAL = auto()  # Портал

#    CHECKPOINT = auto()    # Контрольная точка
#    PROJECTILE = auto()    # Снаряд/пуля
#    POWERUP = auto()       # Улучшение

    def __str__(self):
        return self.name.lower()

    @property
    def is_solid(self):
        """Является ли объект твердым (непроходимым)"""
        return self in [
            ObjectType.ENEMY,
            ObjectType.PLATFORM,
            ObjectType.PASSABLE_PLATFORM,
            ObjectType.MOVING_PLATFORM,
            ObjectType.OBSTACLE,
            ObjectType.SPIKE,
            ObjectType.CIRCULAR_SAW,
            ObjectType.PORTAL,
        ]

    @property
    def is_dangerous(self):
        """Является ли объект опасным"""
        return self in [
            ObjectType.ENEMY,
            ObjectType.SPIKE,
            ObjectType.CIRCULAR_SAW,
        ]

    @property
    def is_collectible(self):
        """Можно ли собрать объект"""
        return self in [
            ObjectType.COIN,
            ObjectType.ARTIFACT,
   #         ObjectType.CHECKPOINT
        ]