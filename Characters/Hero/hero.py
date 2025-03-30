from typing import Tuple
from Characters.animated_character import AnimatedCharacter
from Characters.type_object import ObjectType
from custom_logging import Logger


class Hero(AnimatedCharacter):
    """Класс для создания главного персонажа игры"""

    def __init__(
        self,
        position: Tuple[int, int],
        ground_level: int = 2000,
        size: Tuple[int, int] = (60, 80),
        speed: float = 8.0,
        jump_force: float = 12,
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
            "IDLE": {"file_path": f"{path_to_assets}/idle.png", "frame_count": 7},
            "MOVE": {"file_path": f"{path_to_assets}/idle.png", "frame_count": 7},
            "JUMP": {"file_path": f"{path_to_assets}/jump.png", "frame_count": 13},
            "SIT": {"file_path": f"{path_to_assets}/sit.png", "frame_count": 4, "sit_frames": True},
            "SIT_MOVE": {"file_path": f"{path_to_assets}/sit.png", "frame_count": 4, "sit_frames": True},
            "SIT_IDLE": {"file_path": f"{path_to_assets}/sit.png", "frame_count": 4, "sit_frames": True},
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

        Logger().info(f"Hero created at position {position}")

    def take_damage(self, amount: int):
        """Метод для получения урона"""
        Logger().warning(f"Hero took {amount} damage!")

    def collect_coin(self, amount: int = 1):
        """Метод для сбора монет"""
        Logger().info(f"Hero collected {amount} coin(s).")

    def heal(self, amount: int):
        """Метод для восстановления здоровья"""
        Logger().info(f"Hero healed for {amount} HP.")