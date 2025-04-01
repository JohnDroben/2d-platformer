from typing import Tuple
from Characters.animated_character import AnimatedCharacter
from Characters.type_object import ObjectType
from custom_logging import Logger
from time import sleep

class Hero(AnimatedCharacter):
    """Класс для создания главного персонажа игры"""

    def __init__(
        self,
        position: Tuple[int, int],
        ground_level: int = 2000,
        size: Tuple[int, int] = (60, 80),
        speed: float = 8.0,
        jump_force: float = 13,
        gravity: float = 0.6,
        obj_type: ObjectType = ObjectType.PLAYER
    ):
        """
        Инициализация главного персонажа.

        :param position: Позиция объекта (x, y)
        :param ground_level: Уровень земли
        :param size: Размер объекта (ширина, высота)
        :param speed: Скорость движения
        :param jump_force: Сила прыжка
        :param gravity: Гравитация
        :param obj_type: Тип объекта
        """
        # Конфигурация анимаций для героя
        path_to_assets = "Characters/assets/sprites"
        animation_config = {
            "IDLE": {"file_path": f"{path_to_assets}/player_stand.png", "frame_count": 1},
            "MOVE": {"file_path": f"{path_to_assets}/player_walk.png", "frame_count": 2},
            "JUMP": {"file_path": f"{path_to_assets}/player_jump.png", "frame_count": 1},
            "SIT": {"file_path": f"{path_to_assets}/player_duck.png", "frame_count": 1, "sit_frames": True},
            "SIT_MOVE": {"file_path": f"{path_to_assets}/player_duck.png", "frame_count": 1, "sit_frames": True},
            "SIT_IDLE": {"file_path": f"{path_to_assets}/player_duck.png", "frame_count": 1, "sit_frames": True},
        }

        # Вызов конструктора родительского класса
        super().__init__(
            position=position,
            size=size,
            obj_type=obj_type,
            speed=speed,
            jump_force=jump_force,
            gravity=gravity,
            ground_level=ground_level,
            animation_config=animation_config
        )
        self.INIT_LIVES = 5
        self.lives = self.INIT_LIVES
        Logger().info(f"Hero created at position {position}")

    def lose_life(self):
        """Метод для получения урона"""

        if self.lives > 0:
            self.lives = self.lives - 1
            Logger().debug(f"The hero loses a life")
        else:
            Logger().debug(f"The hero dies")
        sleep(1)

    def is_live(self):
        return self.lives > 0

    def get_lives(self):
        return self.lives, self.INIT_LIVES

    def collect_coin(self, amount: int = 1):
        """Метод для сбора монет"""
        Logger().info(f"Hero collected {amount} coin(s).")

    def heal(self, amount: int):
        """Метод для восстановления здоровья"""
        Logger().info(f"Hero healed for {amount} HP.")