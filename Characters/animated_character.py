
from typing import Tuple
import pygame
from Characters.action import Action
from Characters.character import  Character
from Characters.animation2 import AnimatedObject
from levels import GameObject
from Characters.type_object import ObjectType
from custom_logging import Logger

class AnimatedCharacter(GameObject):
    """Класс, объединяющий Character и AnimatedObject через композицию"""

    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        obj_type: ObjectType,
        speed: float,
        jump_force: float,
        gravity: float,
        ground_level: int,
        animation_config: dict
    ):
        """
        Инициализация игрового персонажа с анимацией.

        :param position: Позиция объекта (x, y)
        :param size: Размер объекта (ширина, высота)
        :param obj_type: Тип объекта
        :param speed: Скорость движения
        :param jump_force: Сила прыжка
        :param gravity: Гравитация
        :param ground_level: Уровень земли
        :param animation_config: Конфигурация анимаций
        """
        super().__init__(position, size, obj_type)

        # Создание Character
        self.character = Character(
            x=position[0],
            y=position[1],
            width=size[0],
            height=size[1],
            speed=speed,
            jump_force=jump_force,
            gravity=gravity,
            ground_level=ground_level
        )
        self.rect = self.character.rect
        # Создание AnimatedObject
        self.animated_object = AnimatedObject(self.character)

        # Загрузка анимаций
        for action_name, action_data in animation_config.items():
            action = getattr(Action, action_name)
            self.animated_object.load_action_frames(
                action=action,
                file_path=action_data['file_path'],
                frame_count=action_data['frame_count'],
                sit_frames=action_data.get('sit_frames', False)
            )

    def move(self, direction: int):
        """Делегирование управления движением Character"""
        self.character.move(direction)

    def jump(self):
        """Делегирование прыжка Character"""
        self.character.jump()

    def sit_down(self):
        """Делегирование присаживание Character"""
        self.character.sit_down()

    def is_sitting(self):
        return self.character.is_sitting

    def stand_up(self, platforms):
        """Делегирование вставание Character"""
        self.character.stand_up(platforms)

    def apply_physics(self, game_objects, screen_width, screen_height):
        """Делегирование физики Character"""
        self.character.apply_physics(game_objects, screen_width, screen_height)

    def update(self):
        """Обновление состояния объекта"""
        self.animated_object.update()

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Отрисовка объекта на поверхности"""
        self.animated_object.draw(surface, camera_offset)

    def check_collision(self, other_rect: pygame.Rect) -> bool:
        """Проверка коллизии с другим объектом"""
        return self.character.rect.colliderect(other_rect)