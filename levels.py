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
    """Люк с привязанным лифтом"""

    def __init__(self, platform: 'Platform', width: int, position_x: int, all_platforms: List['Platform']):
        super().__init__(
            (platform.rect.x + position_x, platform.rect.y),
            (width, PLATFORM_HEIGHT),
            ObjectType.HOLE
        )
        self.platform = platform
        self.all_platforms = all_platforms
        self.lift = None  # Привязанный лифт
        self.sprite = pygame.Surface((width, PLATFORM_HEIGHT))
        self.sprite.fill((50, 50, 50))

    def set_lift(self, lift: 'MovingPlatformVertical'):
        """Жестко привязывает лифт к люку"""
        self.lift = lift
        # Центрируем лифт относительно люка
        self.lift.rect.midbottom = (self.rect.centerx, self.rect.top)
        # Настраиваем границы движения
        self.lift.lower_y = self.rect.top - self.lift.rect.height
        self.lift.upper_y = self.find_upper_platform().rect.bottom - self.lift.rect.height

    def find_upper_platform(self) -> 'Platform':
        """Находит ближайшую платформу выше"""
        for platform in self.all_platforms:
            if platform.rect.y < self.platform.rect.y:
                return platform
        return self.platform  # Если нет платформы выше, возвращаем текущую

    def update(self):
        if self.lift:
            # Всегда синхронизируем позицию X лифта с люком
            self.lift.rect.x = self.rect.centerx - self.lift.rect.width // 2
            self.lift.update()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.sprite, self.rect)


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

    def add_hole(self, width: int, position_x: int, all_platforms: List['Platform']) -> Hole:
        """Добавляет отверстие в платформе"""
        hole = Hole(self, width, position_x, all_platforms)
        self.holes.append(hole)
        return hole

    def add_vertical_wall(self, height: int):
        """Добавляет вертикальную стену и генерирует люк с лифтом"""
        self.has_vertical_wall = True
        wall = StaticVerticalPlatform((self.rect.x, self.rect.y - height), height)

        # Генерируем люк перед стеной
        hole_width = 100
        hole = self.add_hole(hole_width, self.rect.width - hole_width - 30)

        # Создаем лифт
        lift = MovingPlatformVertical(
            (hole.rect.centerx - 50, self.rect.y - 50),
            30,
            200  # Временное значение, будет пересчитано в set_lift
        )
        hole.set_lift(lift)

        return wall, hole, lift

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы и её отверстий"""
        surface.blit(self.sprite, self.rect)
        for hole in self.holes:
            hole.draw(surface)


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


class MovingPlatformVertical(Obstacle):
    """Лифт, жестко привязанный к люку"""

    def __init__(self, height: int):
        """
        Упрощенная инициализация - позиция будет задана через Hole.set_lift()

        :param height: Высота лифта
        """
        # Временная позиция, будет переопределена
        super().__init__((0, 0), (100, height), ObjectType.MOVING_PLATFORM)
        self.sprite = moving_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (100, height))

        # Границы движения (будут установлены Hole)
        self.lower_y = 0
        self.upper_y = 0
        self.speed = 2
        self.direction = 1  # 1 = вверх, -1 = вниз

    def update(self):
        """Движение между установленными границами"""
        self.rect.y += self.speed * self.direction

        if self.rect.y <= self.upper_y:  # Достигли верха
            self.direction = -1
        elif self.rect.y >= self.lower_y:  # Достигли низа
            self.direction = 1

    def draw(self, surface: pygame.Surface):
        surface.blit(self.sprite, self.rect)


class MovingPlatformVertical(Obstacle):
    """Вертикально движущаяся платформа (лифт)"""

    def __init__(self, position: Position, height: int, lower_platform: 'Platform', upper_platform: 'Platform'):
        """
        Инициализация вертикально движущейся платформы.

        :param position: Позиция (x, _) - y будет вычислен автоматически
        :param height: Высота платформы
        :param lower_platform: Нижняя платформа (где находится люк)
        :param upper_platform: Верхняя платформа (куда должен подниматься лифт)
        """
        # Стартовая позиция - сразу над нижней платформой (на уровне люка)
        start_y = lower_platform.rect.y - height
        super().__init__((position[0], start_y), (100, height), ObjectType.MOVING_PLATFORM)

        self.sprite = moving_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (100, height))

        # Границы движения
        self.lower_y = lower_platform.rect.y - height  # Нижняя граница (уровень люка)
        self.upper_y = upper_platform.rect.y - height  # Верхняя граница (у верхней платформы)
        self.speed = 2
        self.direction = 1  # 1 = вверх, -1 = вниз

    def update(self):
        """Обновление состояния платформы"""
        self.rect.y += self.speed * self.direction

        # Проверяем границы движения
        if self.rect.y <= self.upper_y:  # Достигли верхней платформы
            self.direction = -1  # Меняем направление вниз

        elif self.rect.y >= self.lower_y:  # Вернулись к нижней платформе
            self.direction = 1  # Меняем направление вверх

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы на поверхности"""
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
    """Портал для старта и финиша"""

    def __init__(self, position: Position, is_finish: bool = False):
        """
        Инициализация портала.

        :param position: Позиция портала (x, y)
        :param is_finish: Флаг финишного портала
        """
        super().__init__(position, (60, 100), ObjectType.PORTAL)
        self.sprite = portal_sprite
        self.sprite = pygame.transform.scale(self.sprite, (60, 100))
        self.is_finish = is_finish  # Флаг финишного портала
        self.animation_phase = 0  # Фаза анимации
        self.active = not is_finish  # Флаг активности портала

    def update(self):
        """Обновление состояния портала"""
        self.animation_phase = (self.animation_phase + 0.1) % 360  # Изменение фазы анимации

    def draw(self, surface: pygame.Surface):
        """Отрисовка портала на поверхности"""
        if not self.active:
            return

        # Основа портала
        surface.blit(self.sprite, self.rect)

        # Анимированные частицы
        for i in range(0, 360, 30):
            angle = (self.animation_phase + i) % 360
            radius = 20 + 10 * abs(pygame.math.Vector2(1, 0).rotate(angle).x)
            pos = (
                self.rect.centerx + (self.rect.width // 3) * pygame.math.Vector2(1, 0).rotate(angle).x,
                self.rect.centery + (self.rect.height // 3) * pygame.math.Vector2(1, 0).rotate(angle).y
            )
            pygame.draw.circle(surface, (0, 255, 0) if self.is_finish else (255, 0, 0), pos, int(radius))

    def activate(self):
        """Активация портала"""
        self.active = True


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

        # Игровые объекты
        self.platforms: List[Platform] = []  # Список платформ
        self.obstacles: List[Obstacle] = []  # Список препятствий
        self.bonuses: List[Bonus] = []  # Список бонусов
        self.artifacts: List[Artifact] = []  # Список артефактов
        self.portals: List[Portal] = []  # Список порталов

        # Генерация уровня
        self.generate_level()

    @abstractmethod
    def generate_level(self):
        """Генерация элементов уровня"""
        pass

    def remove_start_portal(self):
        """Удаляет стартовый портал после появления игрока"""
        if not self.start_portal_removed:
            for i, portal in enumerate(self.portals[:]):  # Делаем копию списка для безопасного удаления
                if not portal.is_finish:
                    self.portals.pop(i)
                    self.start_portal_removed = True
                    break

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
        finish_portal = next((p for p in self.portals if p.is_finish), None)
        if finish_portal and finish_portal.active:
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
                        if portal.is_finish:
                            portal.activate()
        return collected

    def check_hazard_collision(self, player_rect: pygame.Rect) -> bool:
        """Проверка опасных столкновений (шипы, пилы)"""
        for obstacle in self.obstacles:
            if isinstance(obstacle, (Spike, CircularSaw)) and obstacle.check_collision(player_rect):
                return True
        return False

    def check_fall_into_pit(self, player_rect: pygame.Rect) -> bool:
        """Проверка падения в яму"""
        for platform in self.platforms:
            for hole in platform.holes:
                if player_rect.colliderect(hole.rect):
                    return True
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
    def generate_level(self):
        # Создаем платформы (как ранее)
        platform_positions = [
            (0, SCREEN_HEIGHT - 150),  # Нижняя
            (0, SCREEN_HEIGHT - 350),  # Средняя (с люком)
            (0, SCREEN_HEIGHT - 550)  # Верхняя
        ]
        self.platforms = [Platform(pos, LEVEL_WIDTH) for pos in platform_positions]

        # Создаем люк на средней платформе
        middle_platform = self.platforms[1]
        hole = middle_platform.add_hole(
            width=150,
            position_x=middle_platform.rect.width // 2 - 75,
            all_platforms=self.platforms
        )

        # Создаем и привязываем лифт
        lift = MovingPlatformVertical(30)  # Только высота
        hole.set_lift(lift)  # Здесь устанавливаются все параметры
        self.obstacles.append(lift)

        # Вертикальные стены (тупики) по краям средней платформы
        wall_height = 120
        left_wall = StaticVerticalPlatform(
            (middle_platform.rect.x + 50, middle_platform.rect.y - wall_height),
            wall_height
        )
        right_wall = StaticVerticalPlatform(
            (middle_platform.rect.right - 80, middle_platform.rect.y - wall_height),
            wall_height
        )
        self.obstacles.extend([left_wall, right_wall])

        # Горизонтальные соединительные платформы между уровнями
        self.obstacles.extend([
            StaticHorizontalPlatform((300, SCREEN_HEIGHT - 250), 200),  # Между 1 и 2
            StaticHorizontalPlatform((800, SCREEN_HEIGHT - 450), 200)  # Между 2 и 3
        ])

        # Портал старта (на нижней платформе) и финиша (на верхней)
        self.portals.extend([
            Portal((100, SCREEN_HEIGHT - 250), False),  # Старт
            Portal((LEVEL_WIDTH - 200, SCREEN_HEIGHT - 650), True)  # Финиш
        ])

        # Артефакт на средней платформе рядом с люком
        self.artifacts.append(Artifact((
            middle_platform.rect.centerx + 200,
            middle_platform.rect.y - 50
        )))

        # Шипы на платформах
        for platform in self.platforms:
            for _ in range(3):
                x = random.randint(platform.rect.x + 100, platform.rect.x + platform.rect.width - 100)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        # Монеты
        for _ in range(20):
            x = random.randint(100, LEVEL_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            for _ in range(20):
                self.bonuses.append(Coin((random.randint(100, LEVEL_WIDTH - 100),
                                          random.randint(100, SCREEN_HEIGHT - 200))))
    """Первый уровень с люком и лифтом на средней платформе"""

    def generate_level(self):
        # Основные платформы (3 уровня) на всю ширину
        platform_positions = [
            (0, SCREEN_HEIGHT - 150),  # Нижний уровень (1)
            (0, SCREEN_HEIGHT - 350),  # Средний уровень (2) - здесь будет люк
            (0, SCREEN_HEIGHT - 550)   # Верхний уровень (3)
        ]

        # Создаем платформы
        for x, y in platform_positions:
            platform = Platform((x, y), LEVEL_WIDTH)
            self.platforms.append(platform)

        # Средняя платформа (2)
        middle_platform = self.platforms[1]

        # Создаем люк на средней платформе (примерно по центру)
        hole_width = 150
        hole_position_x = middle_platform.rect.centerx - hole_width//2
        hole = middle_platform.add_hole(
            width=hole_width,
            position_x=hole_position_x,
            all_platforms=self.platforms
        )

        # Создаем лифт для этого люка (движется между средней и нижней платформами)
        lift = MovingPlatformVertical(
            (hole.rect.centerx - 75, middle_platform.rect.y - 30),  # Позиция по x центру люка
            30,  # Высота лифта
            middle_platform,  # Нижняя граница (средняя платформа)
            self.platforms[0]  # Верхняя граница (нижняя платформа)
        )
        self.obstacles.append(lift)
        hole.set_lift(lift)

        # Вертикальные стены (тупики) по краям средней платформы
        wall_height = 120
        left_wall = StaticVerticalPlatform(
            (middle_platform.rect.x + 50, middle_platform.rect.y - wall_height),
            wall_height
        )
        right_wall = StaticVerticalPlatform(
            (middle_platform.rect.right - 80, middle_platform.rect.y - wall_height),
            wall_height
        )
        self.obstacles.extend([left_wall, right_wall])

        # Горизонтальные соединительные платформы между уровнями
        self.obstacles.extend([
            StaticHorizontalPlatform((300, SCREEN_HEIGHT - 250), 200),  # Между 1 и 2
            StaticHorizontalPlatform((800, SCREEN_HEIGHT - 450), 200)   # Между 2 и 3
        ])

        # Портал старта (на нижней платформе) и финиша (на верхней)
        self.portals.extend([
            Portal((100, SCREEN_HEIGHT - 250), False),  # Старт
            Portal((LEVEL_WIDTH - 200, SCREEN_HEIGHT - 650), True)  # Финиш
        ])

        # Артефакт на средней платформе рядом с люком
        self.artifacts.append(Artifact((
            middle_platform.rect.centerx + 200,
            middle_platform.rect.y - 50
        )))

        # Шипы на платформах
        for platform in self.platforms:
            for _ in range(3):
                x = random.randint(platform.rect.x + 100, platform.rect.x + platform.rect.width - 100)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        # Монеты
        for _ in range(20):
            x = random.randint(100, LEVEL_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            self.bonuses.append(Coin((x, y)))


class Level2(Level1):
    """Второй уровень с дополнительными тупиками"""

    def generate_level(self):
        super().generate_level()

        # Основные платформы уже созданы в родительском классе (на всю ширину)
        # Добавляем тупик на нижней платформе
        bottom_platform = self.platforms[0]
        wall_x = bottom_platform.rect.right - 70
        wall_height = 150

        wall = StaticVerticalPlatform(
            (wall_x, bottom_platform.rect.y - wall_height),
            wall_height
        )
        self.obstacles.append(wall)

        hole = bottom_platform.add_hole(
            width=120,
            position_x=wall_x - bottom_platform.rect.x - 120,
            all_platforms=self.platforms
        )

        # Лифт движется между нижней и средней платформами
        lift = MovingPlatformVertical(
            (hole.rect.centerx - 50, bottom_platform.rect.y - 50),
            30,
            bottom_platform,  # Нижняя граница
            self.platforms[1]  # Верхняя платформа (средняя)
        )
        self.obstacles.append(lift)
        hole.set_lift(lift)

        # [остальной код без изменений]

        # Остальные оригинальные объекты Level2
        for platform in self.platforms:
            for _ in range(2):
                y = random.randint(platform.rect.y + 50, platform.rect.y + platform.rect.height - 50)
                self.obstacles.append(Spike((platform.rect.x + 16, y), False))

        top_platform = self.platforms[-1]
        self.artifacts.append(Artifact((top_platform.rect.x + 350, top_platform.rect.y - 50)))

        for obstacle in self.obstacles:
            if isinstance(obstacle, (MovingPlatformVertical, CircularSaw)):
                obstacle.speed *= 1.5


class Level3(Level2):
    """Третий уровень с тупиками на всех платформах"""

    def generate_level(self):
        super().generate_level()

        # Добавляем тупик на верхней платформе
        top_platform = self.platforms[-1]
        wall_x = top_platform.rect.right - 90
        wall_height = 180

        wall = StaticVerticalPlatform(
            (wall_x, top_platform.rect.y - wall_height),
            wall_height
        )
        self.obstacles.append(wall)

        hole = top_platform.add_hole(
            width=140,
            position_x=wall_x - top_platform.rect.x - 140,
            all_platforms=self.platforms
        )

        # Лифт движется между верхней и средней платформами
        lift = MovingPlatformVertical(
            (hole.rect.centerx - 50, top_platform.rect.y - 50),
            30,
            top_platform,  # Нижняя граница
            self.platforms[1]  # Верхняя платформа (средняя)
        )
        self.obstacles.append(lift)
        hole.set_lift(lift)

        # Оригинальные объекты Level3
        for platform in self.platforms:
            for _ in range(4):
                y = random.randint(platform.rect.y + 50, platform.rect.y + platform.rect.height - 50)
                self.obstacles.append(Spike((platform.rect.x + 16, y), False))

            for _ in range(4):
                x = random.randint(platform.rect.x + 50, platform.rect.x + platform.rect.width - 50)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        self.artifacts.append(Artifact((top_platform.rect.x + 500, top_platform.rect.y - 50)))

        for obstacle in self.obstacles:
            if isinstance(obstacle, (MovingPlatformVertical, CircularSaw)):
                obstacle.speed *= 2.0


class DebugLevel(Level):
    """Отладочный уровень с исправленными лифтами"""

    def generate_level(self):
        self.width = LEVEL_WIDTH
        self.height = SCREEN_HEIGHT
        self.artifacts_required = 1

        # Основные платформы (3 уровня)
        platform_positions = [
            (0, SCREEN_HEIGHT - 150),  # Нижний уровень (1)
            (0, SCREEN_HEIGHT - 350),  # Средний уровень (2)  # Верхний уровень (3)
        ]

        # Создаем платформы
        self.platforms = [Platform(pos, LEVEL_WIDTH) for pos in platform_positions]
        lower_platform = self.platforms[0]
        middle_platform = self.platforms[1]
        

        # 1. Люк и лифт на нижней платформе (движется к средней)
        hole1 = lower_platform.add_hole(
            width=150,
            position_x=400,
            all_platforms=self.platforms
        )
        lift1 = MovingPlatformVertical(
            (hole1.rect.centerx - 75, lower_platform.rect.y - 30),  # Позиция
            30,  # Высота
            lower_platform,  # Нижняя платформа (где люк)
            middle_platform  # Верхняя платформа (куда едет)
        )
        self.obstacles.append(lift1)
        hole1.set_lift(lift1)

        # 2. Люк и лифт на средней платформе (движется к верхней)
        hole2 = middle_platform.add_hole(
            width=150,
            position_x=800,
            all_platforms=self.platforms
        )
        lift2 = MovingPlatformVertical(
            (hole2.rect.centerx - 75, middle_platform.rect.y - 30),
            30,
            middle_platform,
            upper_platform
        )
        self.obstacles.append(lift2)
        hole2.set_lift(lift2)

        # Статические препятствия
        self.obstacles.extend([

            StaticVerticalPlatform((700, middle_platform.rect.y - 120), 120),
            StaticHorizontalPlatform((200, SCREEN_HEIGHT - 250), 150),
            StaticHorizontalPlatform((900, SCREEN_HEIGHT - 450), 150),
            Spike((500, lower_platform.rect.y - 16), True),
            CircularSaw((400, SCREEN_HEIGHT - 400), 100)
        ])

        # Бонусы и артефакты
        self.bonuses.extend([
            Coin((250, SCREEN_HEIGHT - 200)),
            Coin((850, SCREEN_HEIGHT - 400))
        ])
        self.artifacts.append(Artifact((700, SCREEN_HEIGHT - 300)))

        # Портал старта и финиша
        self.portals.extend([
            Portal((100, SCREEN_HEIGHT - 250), False),
            Portal((1100, SCREEN_HEIGHT - 600), True)
        ])


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

    def reset(self, debug_mode=False):
        """Сброс менеджера уровней с возможностью debug режима"""
        self.current_level_num = 0 if debug_mode else 1
        self.total_score = 0
        self.total_artifacts = 0
        self.game_over = False
        self.current_level = self.create_level(self.current_level_num)

    def get_level_completion_message(self) -> str:
        """Возвращает сообщение о завершении уровня"""
        if self.current_level.completed:
            if self.current_level_num < 3:
                return f"Level {self.current_level_num} complete! Score: {self.total_score}"
            else:
                return f"Game completed! Final score: {self.total_score}"
        return ""
