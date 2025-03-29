from enum import Enum, auto

class ObjectType(Enum):
    """Класс для типов игровых объектов"""
    PLATFORM = auto()      # Твердая платформа
#    PASSABLE_PLATFORM = auto()  # Платформа, сквозь которую можно прыгать снизу
    ENEMY = auto()         # Враг
    COIN = auto()          # Монетка/коллекционный предмет
#    SPIKE = auto()         # Шипы/опасность
#    CHECKPOINT = auto()    # Контрольная точка
#    DOOR = auto()          # Дверь/переход между уровнями
    PLAYER = auto()        # Игрок
#    PROJECTILE = auto()    # Снаряд/пуля
#    POWERUP = auto()       # Улучшение

    def __str__(self):
        return self.name.lower()

    @property
    def is_solid(self):
        """Является ли объект твердым (непроходимым)"""
        return self in [
            ObjectType.PLATFORM,
            ObjectType.ENEMY,
  #          ObjectType.SPIKE,
  #          ObjectType.DOOR
        ]

    @property
    def is_dangerous(self):
        """Является ли объект опасным"""
        return self in [
            ObjectType.ENEMY,
  #          ObjectType.SPIKE,
   #         ObjectType.PROJECTILE
        ]

    @property
    def is_collectible(self):
        """Можно ли собрать объект"""
        return self in [
            ObjectType.COIN,
   #         ObjectType.POWERUP,
   #         ObjectType.CHECKPOINT
        ]