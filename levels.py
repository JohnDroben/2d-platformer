import pygame
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from Characters.type_object import ObjectType
from custom_logging import Logger
import os

# Константы
SCREEN_WIDTH = 1280  # Ширина экрана
SCREEN_HEIGHT = 960  # Высота экрана
LEVEL_WIDTH = SCREEN_WIDTH * 5  # Ширина уровня (в 5 раза больше ширины экрана)
PLATFORM_HEIGHT = 30  # Высота платформы
PLATFORM_COUNT = 3  # Количество уровней платформ
PLATFORM_GAP = 200  # Расстояние между платформами

# Типы для аннотаций
Color = Tuple[int, int, int]  # Цвет в формате RGB
Position = Tuple[int, int]  # Позиция объекта (x, y)
Size = Tuple[int, int]  # Размер объекта (ширина, высота)





def load_sprite(name: str, default_color: tuple) -> pygame.Surface:
    """Безопасная загрузка спрайтов с проверкой инициализации"""
    try:
        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode((1, 1))  # Минимальный дисплей

        path = os.path.join("assets", "imgs", name)
        Logger().debug(f"Пытаюсь загрузить {path}, существует? {os.path.exists(path)}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл {path} не найден")

        sprite = pygame.image.load(path)
        Logger().debug(f"✅ Успешно загружен {name}, размер {sprite.get_size()}")
        return sprite.convert_alpha() if pygame.display.get_init() else sprite

    except Exception as e:
        Logger().debug(f"Ошибка загрузки {name}: {e}")
        size = (SCREEN_WIDTH, SCREEN_HEIGHT) if name == "level_1.png" else (32, 32)
        stub = pygame.Surface(size)
        stub.fill(default_color)
        return stub


def load_coin_frames():
    frames = []
    base_size = None

    for i in range(1, 5):
        try:
            frame = pygame.image.load(f"assets/imgs/coin_{i}.png").convert_alpha()

            # Проверка одинаковости размеров
            if base_size is None:
                base_size = frame.get_size()
            elif frame.get_size() != base_size:
                Logger().debug(f"Ошибка: coin_{i}.png имеет размер {frame.get_size()}, ожидалось {base_size}")
                frame = pygame.transform.scale(frame, base_size)

            frames.append(frame)
        except Exception as e:
            Logger().debug(f"Ошибка загрузки coin_{i}.png: {e}")
            # Создаем заглушку
            stub = pygame.Surface(base_size or (32, 32), pygame.SRCALPHA)
            stub.fill((255, 215, 0))  # Золотой цвет
            frames.append(stub)

    return frames


coin_animation_frames = load_coin_frames()


# Загружаем оригинальный фон
original_bg = load_sprite("fon_1.jpg", (20, 30, 15))

# Создаем склеенный фон (7x ширины с чередованием оригинальной и отраженной картинки)
bg_width, bg_height = original_bg.get_size()
stitched_bg = pygame.Surface((bg_width * 7, bg_height))

# Флаг для чередования оригинальной и отраженной картинки
for i in range(7):
    if i % 2 == 0:
        # Оригинальная картинка
        stitched_bg.blit(original_bg, (i * bg_width, 0))
    else:
        # Отраженная по горизонтали картинка
        flipped_bg = pygame.transform.flip(original_bg, True, False)
        stitched_bg.blit(flipped_bg, (i * bg_width, 0))

background_sprite = stitched_bg

# Загружаем оригинальный спрайт платформы
original_pf = load_sprite("tile_1.png", (100, 100, 100))  # Исходный спрайт
pf_width, pf_height = original_pf.get_size()
platform_sprite = original_pf  # Используем оригинальный размер спрайта

# Загружаем оригинальный спрайт вертикальной платформы
original_vpf = load_sprite("tile_10.png", (100, 100, 100))  # Исходный спрайт
vpf_width, vpf_height = original_vpf.get_size()
vertical_platform_sprite = original_vpf  # Используем оригинальный размер спрайта

# Загружаем оригинальный спрайт горизонтальной платформы
original_gpf = load_sprite("tile_10.png", (100, 100, 100))  # Исходный спрайт
vpf_width, gpf_height = original_gpf.get_size()
vertical_platform_sprite = original_gpf  # Используем оригинальный размер спрайта

# coin_sprite = load_sprite("coin.png", (255, 215, 0))
spike_sprite = load_sprite("spike_3.png", (139, 0, 0))
moving_platform_sprite = load_sprite("moving_platform.png", (150, 75, 0))
saw_sprite = load_sprite("saw.png", (200, 200, 200))
artifact_sprite = load_sprite("artifact.png", (255, 215, 0))
portal_sprite = load_sprite("door.png", (0, 255, 0))
vertical_platform_sprite = load_sprite("tile_10.png", (120, 120, 120))
horizontal_platform_sprite = load_sprite("tile_1.png", (120, 120, 120))


# Загрузка кадров анимации монеты
coin_animation_frames = [
load_sprite("coin.png", (255, 215, 0)),
    load_sprite("coin_1.png", (255, 215, 0)),  # Желтый как цвет по умолчанию
    load_sprite("coin_2.png", (255, 215, 0)),
    load_sprite("coin_3.png", (255, 215, 0))

]

class GameObject(ABC):
    """Базовый класс для всех игровых объектов"""

    def __init__(self, position: Position, size: Size, obj_type: ObjectType):
        """
        Инициализация игрового объекта.

        :param position: Позиция объекта (x, y)
        :param size: Размер объекта (ширина, высота)
        :param obj_type: Тип объекта
        """
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])  # Прямоугольник объекта
        self.is_active = True  # Флаг активности объекта
        self.object_type = obj_type  # Тип объекта

    @abstractmethod
    def update(self):
        """Обновление состояния объекта"""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Отрисовка объекта на поверхности"""
        pass

    def check_collision(self, other_rect: pygame.Rect) -> bool:
        """Проверка коллизии с другим объектом"""
        return self.rect.colliderect(other_rect)


class Bonus(GameObject):
    """Базовый класс бонусов"""

    def __init__(self, position: Position, size: Size, points: int, obj_type: ObjectType):
        """
        Инициализация бонуса.

        :param position: Позиция бонуса (x, y)
        :param size: Размер бонуса (ширина, высота)
        :param points: Количество очков, которое дает бонус
        :param obj_type: Тип объекта
        """
        super().__init__(position, size, obj_type)
        self.points = points  # Количество очков

    def collect(self) -> int:
        """Сбор бонуса"""
        self.is_active = False  # Делаем бонус неактивным
        return self.points  # Возвращаем количество очков


class Coin(Bonus):
    def __init__(self, position: Position):
        # Загружаем первый кадр для определения базового размера
        base_frame = coin_animation_frames[0]
        sprite_width, sprite_height = base_frame.get_size()

        # Создаем хитбокс ПРОПОРЦИОНАЛЬНО спрайту
        hitbox_width = max(7, sprite_width)  # Минимальная ширина 7 пикселей
        hitbox_height = sprite_height  # Высота как у спрайта

        super().__init__(position, (hitbox_width, hitbox_height), 100, ObjectType.COIN)

        self.frames = coin_animation_frames
        self.current_frame = 0
        self.animation_speed = 0.15
        self.last_update = pygame.time.get_ticks()

        # Центрируем хитбокс относительно спрайта
        self.sprite_offset_x = (hitbox_width - sprite_width) // 2
        self.sprite_offset_y = (hitbox_height - sprite_height) // 2

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

    def draw(self, surface: pygame.Surface):
        current_sprite = self.frames[self.current_frame]
        # Позиция отрисовки с учетом смещения
        surface.blit(current_sprite,
                     (self.rect.x + self.sprite_offset_x,
                      self.rect.y + self.sprite_offset_y))



class Obstacle(GameObject):
    """Базовый класс препятствий"""

    def __init__(self, position: Position, size: Size, obj_type: ObjectType):
        """
        Инициализация препятствия.

        :param position: Позиция препятствия (x, y)
        :param size: Размер препятствия (ширина, высота)
        :param obj_type: Тип объекта
        """
        super().__init__(position, size, obj_type)


class Hole(GameObject):
    """Класс люка без привязки к лифту"""

    def __init__(self, platform: 'Platform', width: int, position_x: int):
        super().__init__(
            (platform.rect.x + position_x, platform.rect.y),
            (width, PLATFORM_HEIGHT),
            ObjectType.HOLE
        )
        self.platform = platform
        self.sprite = pygame.Surface((width, PLATFORM_HEIGHT))
        self.sprite.fill((0, 5, 5))

    def update(self):
        """Реализация абстрактного метода - люк не требует обновления"""
        pass

    def draw(self, surface: pygame.Surface):
        """Реализация абстрактного метода"""
        surface.blit(self.sprite, self.rect)


class HoleWithLift(Hole):
    """Люк с автоматически движущимся лифтом"""

    def __init__(self, platform: 'Platform', width: int, position_x: int, lift_height: int = 30):
        """
        :param platform: Родительская платформа
        :param width: Ширина люка
        :param position_x: Смещение по X от левого края платформы
        :param lift_height: Высота лифта (по умолчанию 30px)
        """
        super().__init__(platform, width, position_x)

        # Позиция лифта (центрирован по X относительно люка)
        lift_x = self.rect.centerx - 50  # 50 = половина ширины лифта (100px)
        lift_y = platform.rect.top - lift_height  # Стартовая позиция - под платформой

        # Создаем лифт с указанной высотой
        self.lift = MovingPlatformVertical(
            position=(lift_x, lift_y),
            height=lift_height
        )

        # Настраиваем границы движения
        self.lift.upper_y = platform.rect.top - lift_height + 30
        self.lift.lower_y = platform.rect.top + 300

    def update(self):
        """Обновление состояния люка и лифта"""
        super().update()  # Вызываем базовый метод (хотя он пустой)
        if self.lift:
            # Синхронизация позиции по X
            self.lift.rect.centerx = self.rect.centerx
            self.lift.update()

    def draw(self, surface: pygame.Surface):
        """Отрисовка люка и лифта"""
        super().draw(surface)  # Рисуем сам люк
        if self.lift:
            self.lift.draw(surface)  # Рисуем лифт


class Platform(GameObject):
    """Платформа с возможностью создания отверстий"""


    def __init__(self, position: Position, width: int):
        super().__init__(position, (width, PLATFORM_HEIGHT), ObjectType.PLATFORM)
        self.sprite = platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (width, PLATFORM_HEIGHT))
        self.holes = []
        self.has_vertical_wall = False

    def update(self):
        """Обновление состояния платформы (пустая реализация, так как платформа статична)"""
        pass

    def add_hole(self, width: int, position_x: int) -> Hole:
        """Добавляет отверстие в платформе"""
        hole = Hole(self, width, position_x)
        self.holes.append(hole)
        return hole


    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы со склеенным спрайтом"""
        # Получаем размеры оригинального спрайта платформы
        sprite_width, sprite_height = platform_sprite.get_size()

        # Вычисляем сколько раз нужно повторить спрайт
        repeat_count = 200

        # Рисуем склеенные спрайты
        for i in range(repeat_count):
            surface.blit(platform_sprite, (self.rect.x + i * sprite_width, self.rect.y))

        # Отрисовка отверстий
        for hole in self.holes:
            hole.draw(surface)


class MovingPlatformVertical(Obstacle):
    """Вертикально движущаяся платформа (лифт)"""

    def __init__(self, position: Position, height: int):
        """
        :param position: Начальная позиция (x, y)
        :param height: Высота платформы
        """
        super().__init__(position, (100, height), ObjectType.MOVING_PLATFORM)
        self.sprite = moving_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (100, height))

        # Границы движения
        self.lower_y = position[1]  # Нижняя граница (начальная позиция)
        self.upper_y = position[1] + 200  # Верхняя граница (на 200px выше)
        self.speed = 2
        self.direction = 1  # 1 = вверх, -1 = вниз
        self.rect.y = position[1]

    def update(self):
        """Обновление позиции лифта"""
        self.rect.y += self.speed * self.direction

        # Проверка границ и смена направления
        if self.rect.y >= self.lower_y:
            self.direction = -1  # Двигаемся вверх
        elif self.rect.y <= self.upper_y:
            self.direction = 1  # Двигаемся вниз

    def draw(self, surface: pygame.Surface):
        """Отрисовка лифта"""
        surface.blit(self.sprite, self.rect)


class StaticVerticalPlatform(Obstacle):
    """Статичная вертикальная платформа (стена/колонна)"""

    def __init__(self, position: Position, height: int):
        """
        Инициализация вертикальной платформы.

        :param position: Позиция платформы (x, y)
        :param height: Высота платформы
        """
        super().__init__(position, (30, 100), ObjectType.PLATFORM)
        # Оригинальный спрайт без масштабирования
        self.original_sprite = vertical_platform_sprite
        self.tile_height = self.original_sprite.get_height()  # Высота одного тайла

    def update(self):
        """Обновление состояния (пустое, так как платформа статична)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка с повторением текстуры по вертикали"""
        # Сколько целых тайлов помещается
        full_tiles = self.rect.height // self.tile_height
        # Остаток (последний неполный тайл)
        remainder = self.rect.height % self.tile_height

        # Рисуем целые тайлы
        for i in range(full_tiles):
            surface.blit(self.original_sprite,
                         (self.rect.x,
                          self.rect.y + i * self.tile_height))

        # Рисуем остаток (если есть)
        if remainder > 0:
            # Вырезаем нужную часть из спрайта
            partial_tile = pygame.Surface((self.rect.width, remainder), pygame.SRCALPHA)
            partial_tile.blit(self.original_sprite, (0, 0),
                              (0, 0, self.rect.width, remainder))
            surface.blit(partial_tile,
                         (self.rect.x,
                          self.rect.y + full_tiles * self.tile_height))


class StaticHorizontalPlatform(Obstacle):
    """Статичная горизонтальная платформа (балка/перемычка)"""

    def __init__(self, position: Position, width: int):
        """
        Инициализация горизонтальной платформы.

        :param position: Позиция платформы (x, y)
        :param width: Ширина платформы
        """
        super().__init__(position, (width, 20), ObjectType.PLATFORM)
        # Оригинальный спрайт без масштабирования
        self.original_sprite = horizontal_platform_sprite
        self.tile_height = self.original_sprite.get_height()  # Высота одного тайла

    def update(self):
        """Обновление состояния (пустое, так как платформа статична)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка с повторением текстуры по горизонтали"""
        # Получаем ширину одного тайла из спрайта
        tile_width = self.original_sprite.get_width()
        # Сколько целых тайлов помещается
        full_tiles = self.rect.width // tile_width
        # Остаток (последний неполный тайл)
        remainder = self.rect.width % tile_width

        # Рисуем целые тайлы
        for i in range(full_tiles):
            surface.blit(self.original_sprite,
                    (self.rect.x + i * tile_width,  # X увеличивается вправо
                     self.rect.y))                  # Y остается постоянным

        # Рисуем остаток (если есть)
        if remainder > 0:
            # Вырезаем нужную часть из спрайта
            partial_tile = pygame.Surface((self.rect.width, remainder), pygame.SRCALPHA)
            partial_tile.blit(self.original_sprite, (0, 0),
                              (0, 0, remainder, self.rect.height))
            surface.blit(partial_tile,
                         (self.rect.x + full_tiles * tile_width,  # Позиция остатка
                          self.rect.y))


class Spike(Obstacle):
    def __init__(self, position: Position, is_floor_spike: bool = True):
        """
        :param position: Позиция шипов (x, y)
        :param is_floor_spike: True - шипы на полу (смотрят вверх), False - на стене (смотрят вправо)
        """
        # Размеры для разных ориентаций
        size = (32, 32)  # Базовый размер

        super().__init__(position, size, ObjectType.SPIKE)

        # Загружаем оригинальный спрайт
        original_sprite = spike_sprite

        # Трансформируем спрайт в зависимости от ориентации
        if is_floor_spike:
            # Шипы на полу (нормальная ориентация)
            self.sprite = pygame.transform.scale(original_sprite, (32, 32))
        else:
            # Шипы на стене (повернуты на 90 градусов)
            self.sprite = pygame.transform.rotate(
                pygame.transform.scale(original_sprite, (32, 32)),
                -90  # Поворот против часовой стрелки
            )

        # Хитбокс должен соответствовать спрайту
        self.rect = self.sprite.get_rect(topleft=position)

    def update(self):
        """Обновление состояния шипов (пустое, так как шипы не движутся)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка шипов на поверхности"""
        surface.blit(self.sprite, self.rect)


class CircularSaw(Obstacle):
    """Дисковая пила"""

    def __init__(self, position: Position, move_range: int):
        """
        Инициализация дисковой пилы.

        :param position: Позиция пилы (x, y)
        :param move_range: Диапазон движения пилы
        """
        # Загружаем спрайт внутри класса
        try:
            self.sprite = pygame.image.load("assets/images/circular_saw.png").convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (50, 50))
        except:
            # Создаем временный спрайт, если загрузка не удалась
            self.sprite = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, (255, 0, 0), (25, 25), 25)
            pygame.draw.circle(self.sprite, (200, 200, 200), (25, 25), 20)

        super().__init__(position, (50, 50), ObjectType.CIRCULAR_SAW)
        self.original_y = position[1]
        self.move_range = move_range
        self.speed = 3
        self.direction = 1
        self.rotation_angle = 0

    def update(self):
        """Обновление состояния пилы"""
        self.rect.y += self.speed * self.direction
        if self.rect.y > self.original_y + self.move_range:
            self.direction = -1
        elif self.rect.y < self.original_y - self.move_range:
            self.direction = 1

        # Обновляем угол вращения
        self.rotation_angle = (self.rotation_angle + 10) % 360

    def draw(self, surface: pygame.Surface):
        """Отрисовка пилы с вращением"""
        rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation_angle)
        new_rect = rotated_sprite.get_rect(center=self.rect.center)
        surface.blit(rotated_sprite, new_rect.topleft)


class Artifact(Bonus):
    """Артефакт - специальный бонус"""

    def __init__(self, position: Position):
        """
        Инициализация артефакта.

        :param position: Позиция артефакта (x, y)
        """
        super().__init__(position, (40, 40), 1000, ObjectType.ARTIFACT)
        self.sprite = artifact_sprite
        self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        self.animation_angle = 0  # Угол анимации

    def update(self):
        """Обновление состояния артефакта"""
        self.animation_angle = (self.animation_angle + 2) % 360  # Изменение угла анимации

    def draw(self, surface: pygame.Surface):
        """Отрисовка артефакта на поверхности"""
        # Вращаем спрайт артефакта
        rotated_sprite = pygame.transform.rotate(self.sprite, self.animation_angle)
        new_rect = rotated_sprite.get_rect(center=self.rect.center)
        surface.blit(rotated_sprite, new_rect.topleft)


class Portal(GameObject):
    """Класс, представляющий портал в игре. Может быть входным или выходным."""

    def __init__(self, position: Position, is_exit: bool):
        """
        Инициализация портала.

        :param position: Позиция портала (x, y)
        :param is_exit: Флаг, является ли портал выходом
        """
        super().__init__(position, (50, 100), ObjectType.PORTAL)
        self.sprite = portal_sprite
        self.is_exit = is_exit  # True - выходной портал, False - входной
        self.is_finish = is_exit  # Синоним для совместимости с существующим кодом
        self.disappear_timer = None  # Таймер исчезновения
        self.visible = True  # Флаг видимости
        self.color = (0, 255, 0) if is_exit else (255, 0, 0)  # Зеленый для выхода, красный для входа
        self.disappear_alpha = 255  # Полностью непрозрачный

        try:
            self.sprite = pygame.image.load("assets/imgs/door.png").convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (50, 100))
            Logger().debug(f"Портал: изображение успешно загружено, размер {self.sprite.get_size()}")
        except Exception as e:
            Logger().debug(f"Ошибка загрузки изображения портала: {e}")
            # Создаем заглушку
            self.sprite = pygame.Surface((50, 100), pygame.SRCALPHA)
            self.sprite.fill((0, 255, 0) if is_exit else (255, 0, 0))
            Logger().debug("Создана заглушка для портала")

    def disappear_after(self, milliseconds: int):
        """Устанавливает таймер исчезновения портала"""
        self.disappear_timer = pygame.time.get_ticks() + milliseconds

    def update(self):
        """Обновление состояния портала"""
        if self.disappear_timer and pygame.time.get_ticks() >= self.disappear_timer:
            progress = (pygame.time.get_ticks() - self.disappear_timer) / self.disappear_delay
            self.disappear_alpha = max(0, 255 - int(255 * progress))



    def draw(self, surface: pygame.Surface):
        """Отрисовка портала"""
        Logger().debug(f"Отрисовка портала: pos={self.rect.topleft}, видимый={self.disappear_alpha > 0}")
        if self.visible:
            if self.sprite:
                Logger().debug(f"✅ sprite существует, размер: {self.sprite.get_size()}")
                surface.blit(self.sprite, self.rect)  # <-- Здесь рисуем
            else:
                Logger().debug("❌ Ошибка: sprite = None, рисуем заглушку")
                s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.color, self.disappear_alpha), (0, 0, self.rect.width, self.rect.height))
                surface.blit(s, self.rect)


class Level(ABC):
    """Абстрактный базовый класс уровня"""

    def __init__(self, level_num: int):

        if not pygame.display.get_init():
            pygame.init()
            pygame.display.set_mode((1, 1))

            # Теперь безопасно загружаем спрайты
        self.background = load_sprite("level_1.png", (20, 30, 15))
        Logger().debug(f"Размер фона: {self.background.get_size()}")  # Должно быть (1280, 960)

        """
        Инициализация уровня.

        :param level_num: Номер уровня
        """
        self.level_num = level_num  # Номер уровня
        self.width = LEVEL_WIDTH  # Ширина уровня
        self.height = SCREEN_HEIGHT  # Высота уровня
        self.completed = False  # Флаг завершения уровня
        self.score = 0  # Счет
        self.artifacts_collected = 0  # Количество собранных артефактов
        self.artifacts_required = level_num  # Требуемое количество артефактов
        self.start_portal_removed = False  # Убираем стартовый портал
        self.portal_remove_timer = None
        self.portal_remove_delay = 3000  # 3 секунды в миллисекундах

        # Игровые объекты
        self.platforms: List[Platform] = []  # Список платформ
        self.obstacles: List[Obstacle] = []  # Список препятствий
        self.bonuses: List[Bonus] = []  # Список бонусов
        self.artifacts: List[Artifact] = []  # Список артефактов
        self.portals: List[Portal] = []  # Список порталов

        # Генерация уровня
        self.generate_level()

        # Будем хранить занятые позиции (x, y)
        self.used_positions = []

    @abstractmethod
    def generate_level(self):
        """Генерация элементов уровня"""
        pass

    def is_position_valid(self, x: int, y: int, width: int, height: int) -> bool:
        """Проверяет, что новая позиция не пересекается с существующими объектами"""
        new_rect = pygame.Rect(x, y, width, height).inflate(100, 100)  # Добавляем отступы
        for (used_x, used_y, used_w, used_h) in self.used_positions:
            existing_rect = pygame.Rect(used_x, used_y, used_w, used_h).inflate(100, 100)
            if new_rect.colliderect(existing_rect):
                return False
        return True

    def get_valid_position(self, width: int, height: int, platform: Platform = None) -> tuple:
        """Генерирует валидную позицию с привязкой к платформе (если указана)"""
        max_attempts = 100
        for _ in range(max_attempts):
            if platform:
                x = random.randint(50, self.width - width - 50)
                y = random.randint(platform.rect.top - 300, platform.rect.top - 50)
            else:
                x = random.randint(50, self.width - width - 50)
                y = random.randint(50, self.height - height - 50)

            if self.is_position_valid(x, y, width, height):
                self.used_positions.append((x, y, width, height))
                return (x, y)

        # Если не нашли идеальную позицию, возвращаем случайную с большими отступами
        return (random.randint(100, self.width - width - 100),
                random.randint(100, self.height - height - 100))

    def remove_start_portal(self):
        """Устанавливает таймер удаления стартового портала через 3 секунды"""
        if not self.start_portal_removed:
            for i, portal in enumerate(self.portals):
                if not portal.is_exit:
                    Logger().debug(f"Найден стартовый портал: {portal.rect}")

                    # Удаляем портал из списка
                    self.portals.pop(i)
                    self.start_portal_removed = True
                    Logger().info("Стартовый портал успешно удалён!")
                    return  # Выходим после удаления

            Logger().warning("Стартовый портал не найден!")

    def update(self):
        """Обновление состояния активных объектов"""
        for obstacle in self.obstacles:
            if obstacle.is_active:
                obstacle.update()

        for bonus in self.bonuses:
            if bonus.is_active:
                bonus.update()

        for artifact in self.artifacts:
            if artifact.is_active:
                artifact.update()

        for portal in self.portals:
            portal.update()

        if self.portal_remove_timer and not self.start_portal_removed:
            if pygame.time.get_ticks() - self.portal_remove_timer >= self.portal_remove_delay:
                for i, portal in enumerate(self.portals[:]):
                    if not portal.is_exit:
                        self.portals.pop(i)
                        self.start_portal_removed = True
                        Logger().info("Стартовый портал удален по таймеру")
                        break

    def draw(self, surface: pygame.Surface):
        """Отрисовка уровня"""
        # Фон
        surface.blit(background_sprite, (0, 0))
        Logger().debug(f"Фон: {background_sprite.get_size()} at (0, 0)")

        # Отрисовка объектов
        for platform in self.platforms:
            platform.draw(surface)

        for obstacle in self.obstacles:
            if obstacle.is_active:
                obstacle.draw(surface)

        for bonus in self.bonuses:
            if bonus.is_active:
                bonus.draw(surface)

        for artifact in self.artifacts:
            if artifact.is_active:
                artifact.draw(surface)

        for portal in self.portals:
            portal.draw(surface)

    def check_finish(self, player_rect: pygame.Rect) -> bool:
        """Проверка достижения финиша"""
        finish_portal = next((p for p in self.portals if p.is_exit and p.visible), None)
        if finish_portal:
            return player_rect.colliderect(finish_portal.rect)
        return False

    def collect_bonuses(self, player_rect: pygame.Rect) -> int:
        """Сбор бонусов игроком"""
        collected_points = 0
        for bonus in self.bonuses[:]:  # Используем копию списка для безопасного удаления
            if bonus.is_active and bonus.check_collision(player_rect):
                collected_points += bonus.collect()
                self.bonuses.remove(bonus)  # Удаляем собранный бонус
        return collected_points

    def collect_artifacts(self, player_rect: pygame.Rect) -> bool:
        """Сбор артефактов игроком"""
        collected = False
        for artifact in self.artifacts:
            if artifact.is_active and artifact.check_collision(player_rect):
                artifact.collect()
                self.artifacts_collected += 1
                collected = True

                # Активируем финишный портал если собраны все артефакты
                if self.artifacts_collected >= self.artifacts_required:
                    for portal in self.portals:
                        if portal.is_exit:
                            portal.visible = True  # Делаем портал видимым
                            portal.is_active = True  # Активируем портал
                            # Отменяем таймер исчезновения, если он был
                            portal.disappear_timer = None
        return collected

    def check_hazard_collision(self, player_rect: pygame.Rect) -> bool:
        """Проверка опасных столкновений (шипы, пилы)"""
        for obstacle in self.obstacles:
            if isinstance(obstacle, (Spike, CircularSaw)) and obstacle.check_collision(player_rect):
                return True
        return False

    def check_fall_into_pit(self, player_rect: pygame.Rect) -> bool:
        """Альтернативная проверка с учетом центра игрока"""
        for platform in self.platforms:
            for hole in platform.holes:
                # Проверяем, что центр игрока внутри люка
                if hole.rect.collidepoint(player_rect.center):
                    return False


    def check_player_fell(self, player_rect: pygame.Rect) -> bool:
        """Проверка, упал ли игрок за нижнюю границу экрана"""
        return player_rect.top > SCREEN_HEIGHT

    def get_active_artifacts_count(self) -> int:
        """Количество оставшихся артефактов"""
        return sum(1 for artifact in self.artifacts if artifact.is_active)

    def get_all_game_objects(self) -> List[GameObject]:
        """
        Возвращает все игровые объекты в виде одного списка.

        :return: Список, содержащий все игровые объекты.
        """
        # Объединяем все списки в один
        all_objects = (
                self.platforms +
                self.obstacles +
                self.bonuses +
                self.artifacts +
                self.portals
        )
        return all_objects


class Level1(Level):
    """Первый уровень игры"""

    def __init__(self, level_num: int = 1):
        super().__init__(level_num)
        self.exit_checked = False
        self.used_x_positions = []  # Для хранения занятых позиций по X

    def get_valid_x_position(self, width: int, min_distance: int = 300) -> int:  # Увеличено с 50 до 300
        """Генерирует X-позицию с минимальным расстоянием от других объектов"""
        max_attempts = 20
        for _ in range(max_attempts):
            x = random.randint(50, self.width - width - 50)

            if all(abs(x - used_x) >= min_distance for used_x in self.used_x_positions):
                self.used_x_positions.append(x)
                return x

        return random.randint(500, self.width - width - 500)

        # Если не удалось найти позицию, возвращаем случайную
        return random.randint(500, self.width - width - 500)

    def generate_level(self):
        """Генерация уровня с правильным размещением объектов"""
        self.width = LEVEL_WIDTH
        self.height = SCREEN_HEIGHT
        self.artifacts_required = 1
        self.exit_checked = False
        self.used_x_positions = []
        self.used_positions = []

        # Основные платформы
        platform_positions = [
            (0, SCREEN_HEIGHT - 150),  # Нижняя
            (0, SCREEN_HEIGHT - 450),  # Средняя
            (0, SCREEN_HEIGHT - 750)  # Верхняя
        ]
        self.platforms = [Platform(pos, LEVEL_WIDTH) for pos in platform_positions]
        lower, middle, upper = self.platforms

        # Разбиваем уровень на 5 вертикальных зон для лучшего распределения
        zone_width = self.width // 5
        zones = [(i * zone_width, (i + 1) * zone_width) for i in range(5)]

        # Словарь для отслеживания занятых зон на каждой платформе
        used_zones = {
            lower: [],
            middle: [],
            upper: []
        }

        # Генерация HoleWithLift для среднего и верхнего уровня (по одному в разных зонах)
        for platform in [middle, upper]:
            available_zones = [z for z in zones if z not in used_zones[platform]]
            if available_zones:
                zone = random.choice(available_zones)
                x = random.randint(zone[0] + 150, zone[1] - 270)  # 270 = 120 (ширина) + 150 (отступ)
                hole = HoleWithLift(
                    platform=platform,
                    width=120,
                    position_x=x,
                    lift_height=40
                )
                platform.holes.append(hole)
                self.obstacles.append(hole.lift)
                used_zones[platform].append(zone)

        # Генерация Hole для нижнего уровня (в разных зонах)
        available_zones = [z for z in zones if z not in used_zones[lower]]
        if len(available_zones) >= 2:
            for _ in range(2):
                zone = random.choice(available_zones)
                available_zones.remove(zone)
                x = random.randint(zone[0] + 150, zone[1] - 270)
                hole = Hole(
                    platform=lower,
                    width=120,
                    position_x=x,
                )
                lower.holes.append(hole)

        # Генерация шипов на платформах (по одному в разных зонах)
        for platform in [lower, middle, upper]:
            available_zones = [z for z in zones if z not in used_zones[platform]]
            if len(available_zones) >= 2:
                for _ in range(4):
                    zone = random.choice(available_zones)
                    available_zones.remove(zone)
                    x = random.randint(zone[0] + 50, zone[1] - 50)
                    self.obstacles.append(Spike((x, platform.rect.y - 30), True))

        # Генерация дисковых пил (по одной на уровне в разных зонах)
        saw_zones = zones.copy()
        for _ in range(3):
            if saw_zones:
                zone = random.choice(saw_zones)
                saw_zones.remove(zone)
                x = random.randint(zone[0] + 100, zone[1] - 100)
                y = random.choice([middle.rect.y - 150, upper.rect.y - 200])
                move_range = random.randint(80, 150)
                self.obstacles.append(CircularSaw((x, y), move_range))

        # Генерация вертикальных стен (в разных зонах)
        wall_zones = zones.copy()
        for _ in range(1):
            if wall_zones:
                zone = random.choice(wall_zones)
                wall_zones.remove(zone)
                x = random.randint(zone[0] + 50, zone[1] - 50)
                height = random.randint(100, 200)
                self.obstacles.append(
                    StaticVerticalPlatform((x, middle.rect.y - height), height)
                )

        # Генерация горизонтальных платформ (в разных зонах)
        platform_zones = zones.copy()
        for _ in range(2):
            if platform_zones:
                zone = random.choice(platform_zones)
                platform_zones.remove(zone)
                x = random.randint(zone[0] + 100, zone[1] - 200)
                height = random.randint(100, 200)
                self.obstacles.append(
                    StaticHorizontalPlatform((x, middle.rect.y - height), 200)
                )

        # Генерация бонусов (монет) с равномерным распределением
        for platform in self.platforms:
            coins_per_platform = 30
            step = (self.width - 200) // coins_per_platform

            for i in range(coins_per_platform):
                x = 100 + i * step + random.randint(-30, 30)
                y = platform.rect.y - random.randint(50, 150)
                self.bonuses.append(Coin((x, y)))

        # Генерация артефакта в свободной зоне
        artifact_zone = random.choice(zones)
        artifact_x = random.randint(artifact_zone[0] + 100, artifact_zone[1] - 100)
        self.artifacts.append(Artifact((
            artifact_x,
            middle.rect.y - 50
        )))

        # Портал входа и выхода в разных зонах
        start_zone = random.choice(zones)
        start_x = random.randint(start_zone[0] + 100, start_zone[0] + 300)
        start_portal = Portal((start_x, lower.rect.top - 100), False)

        exit_zone = random.choice([z for z in zones if z != start_zone])
        finish_x = random.randint(exit_zone[0] + 100, exit_zone[0] + 300)
        finish_portal = Portal((finish_x, upper.rect.top - 100), True)
        finish_portal.visible = False

        self.portals.extend([start_portal, finish_portal])


class Level2(Level1):
    """Второй уровень игры (требуется 2 артефакта)"""

    def __init__(self, level_num: int = 2):
        super().__init__(level_num)

    def generate_level(self):
        super().generate_level()
        self.artifacts_required = 2  # Явно указываем необходимое количество

        # Добавляем второй артефакт
        artifact_x = self.get_valid_x_position(40)
        self.artifacts.append(Artifact((
            artifact_x,
            self.platforms[1].rect.y - 150  # Размещаем на другой высоте
        )))
        # Добавляем дополнительные пилы
        for _ in range(1):
            x = self.get_valid_x_position(50)
            y = random.choice([self.platforms[0].rect.y - 180, self.platforms[2].rect.y - 250])
            self.obstacles.append(CircularSaw((x, y), random.randint(100, 180)))

        # Увеличиваем скорость лифтов
        for obstacle in self.obstacles:
            if isinstance(obstacle, MovingPlatformVertical):
                obstacle.speed = 3


class Level3(Level2):
    """Третий уровень игры (требуется 3 артефакта)"""

    def __init__(self, level_num: int = 3):
        super().__init__(level_num)

    def generate_level(self):
        super().generate_level()
        self.artifacts_required = 3

        # Добавляем третий артефакт
        artifact_x = self.get_valid_x_position(40)
        self.artifacts.append(Artifact((
            artifact_x,
            self.platforms[0].rect.y - 100  # Размещаем на нижнем уровне
        )))

        # Еще больше пил с увеличенным диапазоном движения
        for _ in range(1):
            x = self.get_valid_x_position(50)
            y = random.choice([p.rect.y - random.randint(150, 300) for p in self.platforms])
            self.obstacles.append(CircularSaw((x, y), random.randint(150, 250)))

        # Максимальная скорость лифтов
        for obstacle in self.obstacles:
            if isinstance(obstacle, MovingPlatformVertical):
                obstacle.speed = 4


class DebugLevel(Level):
    """Отладочный уровень для тестирования"""

    def __init__(self, level_num: int = 0):
        super().__init__(level_num)

    def generate_level(self):
        """Генерация отладочного уровня"""
        self.width = 800
        self.height = SCREEN_HEIGHT
        self.artifacts_required = 1

        platform_width = 2000
        platform_positions = [
            (0, SCREEN_HEIGHT - 75),
            (0, SCREEN_HEIGHT - 350)
        ]

        self.platforms = [Platform(pos, platform_width) for pos in platform_positions]
        lower_platform, upper_platform = self.platforms

        # Добавляем HoleWithLift
        holes = [
            HoleWithLift(lower_platform, 100, 250, 30),
            HoleWithLift(upper_platform, 100, 450, 30)
        ]

        for hole in holes:
            hole.platform.holes.append(hole)
            self.obstacles.append(hole.lift)

        # Остальные объекты...
        self.obstacles.append(Spike((500, lower_platform.rect.y - 16), True))
        self.bonuses.extend([Coin((400, SCREEN_HEIGHT - 200)) for _ in range(3)])
        self.artifacts.append(Artifact((550, SCREEN_HEIGHT - 200)))
        self.obstacles.append(CircularSaw((950, SCREEN_HEIGHT - 250), 80))
        self.obstacles.append(StaticVerticalPlatform((700, lower_platform.rect.y - 200), 200))

        Logger().debug("Пытаюсь загрузить:portal_entry.png")  # Добавьте эту строку перед загрузкой
        self.portals.append(Portal((1500, SCREEN_HEIGHT - 175), True))
        self.portals.append(Portal((120, SCREEN_HEIGHT - 175), False))


class LevelManager:
    # Классы уровней (теперь это атрибут класса)
    level_classes = {
        1: Level1,
        2: Level2,
        3: Level3,
        0: DebugLevel  # Отладочный уровень
    }

    def __init__(self, debug_mode=False):
        """Инициализация менеджера уровней"""
        self.current_level_num = 0 if debug_mode else 1  # 0 - debug, 1 - первый уровень
        self.total_score = 0
        self.total_artifacts = 0
        self.game_over = False
        self.current_level = self.create_level(self.current_level_num)

    def create_level(self, level_num: int) -> Level:
        """Создает уровень по номеру"""
        level_class = self.level_classes.get(level_num, Level1)  # По умолчанию Level1
        return level_class(level_num)

    def set_debug_level(self):
        """Переключает на отладочный уровень, сохраняя состояние"""
        self.current_level_num = 0
        self.current_level = self.create_level(0)
        self.game_over = False

    def reset(self, debug_mode=False):
        """Сбрасывает менеджер уровней"""
        self.current_level_num = 0 if debug_mode else 1
        self.total_score = 0
        self.total_artifacts = 0
        self.game_over = False
        self.current_level = self.create_level(self.current_level_num)

    def next_level(self) -> bool:
        """Переходит на следующий уровень"""
        if self.current_level_num == 0:  # Если текущий уровень - debug
            self.current_level_num = 1  # Переключаем на обычный уровень

        if self.current_level_num < 3:
            self.total_score += self.current_level.score
            self.total_artifacts += self.current_level.artifacts_collected
            self.current_level_num += 1
            self.current_level = self.create_level(self.current_level_num)
            return True
        return False

    def update(self, player_rect=None):
        """Обновляет текущий уровень"""
        if hasattr(self, 'current_level'):
            self.current_level.update()
            if player_rect is not None:
                if self.current_level.check_player_fell(player_rect):
                    self.game_over = True

    def draw(self, surface: pygame.Surface):
        """Отрисовывает текущий уровень"""
        self.current_level.draw(surface)

        # Отображаем режим debug
        if self.current_level_num == 0:
            debug_font = pygame.font.SysFont('Arial', 24)  # Создаем шрифт здесь
            debug_text = debug_font.render("DEBUG MODE", True, (255, 0, 0))
            surface.blit(debug_text, (SCREEN_WIDTH - 150, 20))

    def is_game_over(self) -> bool:
        """Проверка завершения игры (игрок упал)"""
        return self.game_over

    def get_level_completion_message(self) -> str:
        """Возвращает сообщение о завершении уровня"""
        if self.current_level.completed:
            if self.current_level_num < 3:
                return f"Level {self.current_level_num} complete! Score: {self.total_score}"
            else:
                return f"Game completed! Final score: {self.total_score}"
        return ""