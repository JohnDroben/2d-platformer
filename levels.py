import pygame
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from Characters.type_object import ObjectType
from custom_logging import Logger

# Константы
SCREEN_WIDTH = 1280  # Ширина экрана
SCREEN_HEIGHT = 960  # Высота экрана
LEVEL_WIDTH = SCREEN_WIDTH * 3  # Ширина уровня (в 3 раза больше ширины экрана)
PLATFORM_HEIGHT = 30  # Высота платформы
PLATFORM_COUNT = 3  # Количество уровней платформ
PLATFORM_GAP = 200  # Расстояние между платформами

# Типы для аннотаций
Color = Tuple[int, int, int]  # Цвет в формате RGB
Position = Tuple[int, int]  # Позиция объекта (x, y)
Size = Tuple[int, int]  # Размер объекта (ширина, высота)


# Функция загрузки спрайтов
def load_sprite(name: str, default_color: Color) -> pygame.Surface:
    """Загрузка спрайта или создание заглушки с указанным цветом"""
    try:
        # Здесь будет реальная загрузка изображений, пока используем заглушки
        sprite = pygame.Surface((32, 32)) if name != "background" else pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        sprite.fill(default_color)
        return sprite
    except:
        # В случае ошибки возвращаем заглушку
        sprite = pygame.Surface((32, 32)) if name != "background" else pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        sprite.fill(default_color)
        return sprite


# Спрайты для всех объектов
background_sprite = load_sprite("background", (20, 30, 15))
coin_sprite = load_sprite("coin", (255, 215, 0))
spike_sprite = load_sprite("spike", (139, 0, 0))
platform_sprite = load_sprite("platform", (100, 100, 100))
moving_platform_sprite = load_sprite("moving_platform", (150, 75, 0))
saw_sprite = load_sprite("saw", (200, 200, 200))
artifact_sprite = load_sprite("artifact", (255, 215, 0))
portal_sprite = load_sprite("portal", (0, 255, 0))
vertical_platform_sprite = load_sprite("vertical_platform", (120, 120, 120))
horizontal_platform_sprite = load_sprite("horizontal_platform", (120, 120, 120))


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
    """Монеты - базовые бонусы"""

    def __init__(self, position: Position):
        """
        Инициализация монеты.

        :param position: Позиция монеты (x, y)
        """
        super().__init__(position, (16, 16), 100, ObjectType.COIN)
        self.sprite = coin_sprite
        self.sprite = pygame.transform.scale(self.sprite, (16, 16))

    def update(self):
        """Обновление состояния монеты (пустое, так как монета не движется)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка монеты на поверхности"""
        surface.blit(self.sprite, self.rect)


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
        self.sprite.fill((50, 50, 50))

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
        self.lift.upper_y = platform.rect.top - lift_height
        self.lift.lower_y = platform.rect.top + 200

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

    def add_vertical_wall(self, height: int):
        """Добавляет вертикальную стену и генерирует люк с лифтом"""
        self.has_vertical_wall = True
        wall = StaticVerticalPlatform((self.rect.x, self.rect.y - height), height)

        # Генерируем люк перед стеной
        hole_width = 100
        hole = self.add_hole(hole_width, self.rect.width - hole_width - 30)

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы и её отверстий"""
        surface.blit(self.sprite, self.rect)
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
        super().__init__(position, (30, height), ObjectType.PLATFORM)
        self.sprite = vertical_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (30, height))

    def update(self):
        """Обновление состояния (пустое, так как платформа статична)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы"""
        surface.blit(self.sprite, self.rect)


class StaticHorizontalPlatform(Obstacle):
    """Статичная горизонтальная платформа (балка/перемычка)"""

    def __init__(self, position: Position, width: int):
        """
        Инициализация горизонтальной платформы.

        :param position: Позиция платформы (x, y)
        :param width: Ширина платформы
        """
        super().__init__(position, (width, 20), ObjectType.PLATFORM)
        self.sprite = horizontal_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (width, 20))

    def update(self):
        """Обновление состояния (пустое, так как платформа статична)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы"""
        surface.blit(self.sprite, self.rect)


class Spike(Obstacle):
    """Шипы - опасные препятствия"""

    def __init__(self, position: Position, horizontal: bool = False):
        """
        Инициализация шипов.

        :param position: Позиция шипов (x, y)
        :param horizontal: Флаг горизонтального расположения шипов
        """
        size = (32, 16) if horizontal else (32, 32)
        super().__init__(position, size, ObjectType.SPIKE)
        self.sprite = spike_sprite
        self.horizontal = horizontal
        if horizontal:
            self.sprite = pygame.transform.scale(self.sprite, (32, 16))
            self.sprite = pygame.transform.rotate(self.sprite, 90)
        else:
            self.sprite = pygame.transform.scale(self.sprite, (32, 32))

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
        super().__init__(position, (50, 50), ObjectType.CIRCULAR_SAW)
        self.sprite = saw_sprite
        self.sprite = pygame.transform.scale(self.sprite, (50, 50))
        self.original_y = position[1]  # Начальная позиция по y
        self.move_range = move_range  # Диапазон движения
        self.speed = 3  # Скорость движения
        self.direction = 1  # Направление движения (1 - вниз, -1 - вверх)

    def update(self):
        """Обновление состояния пилы"""
        self.rect.y += self.speed * self.direction  # Движение пилы
        if self.rect.y > self.original_y + self.move_range:
            self.direction = -1  # Изменение направления на противоположное
        elif self.rect.y < self.original_y - self.move_range:
            self.direction = 1  # Изменение направления на противоположное

    def draw(self, surface: pygame.Surface):
        """Отрисовка пилы на поверхности"""
        # Вращаем спрайт пилы для анимации
        rotated_sprite = pygame.transform.rotate(self.sprite, pygame.time.get_ticks() % 360)
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
        self.sprite = pygame.transform.scale(self.sprite, (50, 100))
        self.is_exit = is_exit  # True - выходной портал, False - входной
        self.is_finish = is_exit  # Синоним для совместимости с существующим кодом
        self.disappear_timer = None  # Таймер исчезновения
        self.visible = True  # Флаг видимости
        self.color = (0, 255, 0) if is_exit else (255, 0, 0)  # Зеленый для выхода, красный для входа
        self.disappear_alpha = 255  # Полностью непрозрачный

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
        if self.visible:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, self.disappear_alpha), (0, 0, self.rect.width, self.rect.height))
            surface.blit(s, self.rect)


class Level(ABC):
    """Абстрактный базовый класс уровня"""

    def __init__(self, level_num: int):
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
        new_rect = pygame.Rect(x, y, width, height)
        for (used_x, used_y, used_w, used_h) in self.used_positions:
            existing_rect = pygame.Rect(used_x, used_y, used_w, used_h)
            if new_rect.inflate(500, 500).colliderect(existing_rect):
                return False
        return True

    def get_valid_position(self, width: int, height: int, platform: Platform = None) -> tuple:
        """Генерирует валидную позицию с привязкой к платформе (если указана)"""
        max_attempts = 50
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

        # Если не нашли идеальную позицию, возвращаем хотя бы по X
        x = random.randint(50, self.width - width - 50)
        y = random.randint(50, self.height - height - 50)
        return (x, y)

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
        for bonus in self.bonuses:
            if bonus.is_active and bonus.check_collision(player_rect):
                collected_points += bonus.collect()
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

    def get_valid_x_position(self, width: int, min_distance: int = 400) -> int:
        """Генерирует X-позицию с минимальным расстоянием от других объектов"""
        max_attempts = 20
        for _ in range(max_attempts):
            x = random.randint(50, self.width - width - 50)

            # Проверяем расстояние до всех занятых позиций
            if all(abs(x - used_x) >= min_distance for used_x in self.used_x_positions):
                self.used_x_positions.append(x)
                return x

        # Если не удалось найти позицию, возвращаем случайную
        return random.randint(50, self.width - width - 50)

    def generate_level(self):
        """Генерация уровня с правильным размещением объектов"""
        self.width = LEVEL_WIDTH
        self.height = SCREEN_HEIGHT
        self.artifacts_required = 1
        self.exit_checked = False
        self.used_x_positions = []
        self.used_positions = []

        # Общие параметры генерации
        OBJECT_X_MARGIN = 50  # Отступ от краев платформы
        MIN_DISTANCE = 500  # Минимальное расстояние между объектами

        # Основные платформы
        platform_positions = [
            (0, SCREEN_HEIGHT - 150),  # Нижняя
            (0, SCREEN_HEIGHT - 400),  # Средняя
            (0, SCREEN_HEIGHT - 700)  # Верхняя
        ]
        self.platforms = [Platform(pos, LEVEL_WIDTH) for pos in platform_positions]
        lower, middle, upper = self.platforms

        # Генерация HoleWithLift для среднего и верхнего уровня
        for platform in [middle, upper]:
            for _ in range(3):
                hole_x = self.get_valid_x_position(120)
                hole = HoleWithLift(
                    platform=platform,
                    width=120,
                    position_x=hole_x,
                    lift_height=40
                )
                platform.holes.append(hole)
                self.obstacles.append(hole.lift)

        # Генерация шипов на платформах
        # Для КАЖДОЙ платформы (нижняя, средняя, верхняя) добавляем:
        for platform in [lower, middle, upper]:
            for _ in range(3):
                x = self.get_valid_x_position(300)
                y = platform.rect.y - random.randint(50, 150)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        # Генерация бонусов (монет)
        for platform in self.platforms:
            for _ in range(20):
                x = self.get_valid_x_position(50)
                y = platform.rect.y - random.randint(50, 150)
                self.bonuses.append(Coin((x, y)))

        # Генерация артефакта
        artifact_x = self.get_valid_x_position(40)
        self.artifacts.append(Artifact((
            artifact_x,
            middle.rect.y - 50
        )))

        # Генерация дисковых пил (CircularSaw)
        for _ in range(4):  # 3 пилы на уровне
            x = self.get_valid_x_position(500)
            y = random.choice([middle.rect.y - 150, upper.rect.y - 200])
            move_range = random.randint(80, 150)
            self.obstacles.append(CircularSaw((x, y), move_range))

        # Генерация вертикальных стен
        for _ in range(2):
            x = self.get_valid_x_position(300)
            height = random.randint(100, 200)
            self.obstacles.append(
                StaticVerticalPlatform((x, middle.rect.y - height), height)
            )

        # Стартовый портал на нижней платформе
        start_x = random.randint(lower.rect.left + 100, lower.rect.right - 150)
        start_portal = Portal((start_x, lower.rect.top - 100), False)

        # Финишный портал на верхней платформе
        finish_x = random.randint(upper.rect.left + 100, upper.rect.right - 150)
        finish_portal = Portal((finish_x, upper.rect.top - 100), True)
        finish_portal.visible = False

        self.portals.extend([start_portal, finish_portal])

        # # Горизонтальные платформы
        for _ in range(2):
            x = self.get_valid_x_position(100)
            height = random.randint(100, 200)
            self.obstacles.append(
                StaticHorizontalPlatform((x, middle.rect.y - height), height)
            )

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
        for _ in range(2):
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
        for _ in range(3):
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

        platform_width = 600
        platform_positions = [
            (100, SCREEN_HEIGHT - 150),
            (100, SCREEN_HEIGHT - 350)
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
        self.obstacles.append(Spike((150, lower_platform.rect.y - 16), True))
        self.bonuses.extend([Coin((400, SCREEN_HEIGHT - 200)) for _ in range(3)])
        self.artifacts.append(Artifact((550, SCREEN_HEIGHT - 200)))
        self.obstacles.append(CircularSaw((650, SCREEN_HEIGHT - 250), 80))
        self.obstacles.append(StaticVerticalPlatform((700, lower_platform.rect.y - 200), 200))
        self.portals.append(Portal((700, SCREEN_HEIGHT - 400), True))
        self.portals.append(Portal((120, SCREEN_HEIGHT - 250), False))


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
        """Переключает на отладочный уровень"""
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