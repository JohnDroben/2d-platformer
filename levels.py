import pygame
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Type
from Characters.object_type import ObjectType
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


class Platform(GameObject):
    """Класс платформы для передвижения игрока"""

    def __init__(self, position: Position, width: int, has_hole: bool = False):
        """
        Инициализация платформы.

        :param position: Позиция платформы (x, y)
        :param width: Ширина платформы
        :param has_hole: Флаг наличия ямы на платформе
        """
        super().__init__(position, (width, PLATFORM_HEIGHT), ObjectType.PLATFORM)
        self.sprite = platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (width, PLATFORM_HEIGHT))
        self.has_hole = has_hole  # Флаг наличия ямы
        self.hole_rect = None  # Прямоугольник ямы
        if has_hole:
            hole_width = random.randint(50, 150)  # Ширина ямы
            hole_x = random.randint(50, width - hole_width - 50)  # Позиция ямы
            self.hole_rect = pygame.Rect(
                position[0] + hole_x,
                position[1],
                hole_width,
                PLATFORM_HEIGHT
            )

    def update(self):
        """Обновление состояния платформы (пустое, так как платформа не движется)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы на поверхности"""
        if not self.has_hole:
            surface.blit(self.sprite, self.rect)
        else:
            # Рисуем левую часть платформы
            left_part = pygame.Rect(
                self.rect.left, self.rect.top,
                self.hole_rect.left - self.rect.left,
                PLATFORM_HEIGHT
            )
            left_sprite = pygame.Surface((left_part.width, left_part.height))
            left_sprite.blit(self.sprite, (0, 0), (0, 0, left_part.width, left_part.height))
            surface.blit(left_sprite, left_part)

            # Рисуем правую часть платформы
            right_part = pygame.Rect(
                self.hole_rect.right, self.rect.top,
                self.rect.right - self.hole_rect.right,
                PLATFORM_HEIGHT
            )
            right_sprite = pygame.Surface((right_part.width, right_part.height))
            right_sprite.blit(self.sprite, (0, 0),
                              (self.sprite.get_width() - right_part.width, 0, right_part.width, right_part.height))
            surface.blit(right_sprite, right_part)


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


class MovingPlatformHorizontal(Obstacle):
    """Горизонтально движущаяся платформа"""

    def __init__(self, position: Position, width: int, move_range: int):
        """
        Инициализация горизонтально движущейся платформы.

        :param position: Позиция платформы (x, y)
        :param width: Ширина платформы
        :param move_range: Диапазон движения платформы
        """
        super().__init__(position, (width, PLATFORM_HEIGHT), ObjectType.MOVING_PLATFORM)
        self.sprite = moving_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (width, PLATFORM_HEIGHT))
        self.original_x = position[0]  # Начальная позиция по x
        self.move_range = move_range  # Диапазон движения
        self.speed = 2  # Скорость движения
        self.direction = 1  # Направление движения (1 - вправо, -1 - влево)

    def update(self):
        """Обновление состояния платформы"""
        self.rect.x += self.speed * self.direction  # Движение платформы
        if self.rect.x > self.original_x + self.move_range:
            self.direction = -1  # Изменение направления на противоположное
        elif self.rect.x < self.original_x - self.move_range:
            self.direction = 1  # Изменение направления на противоположное

    def draw(self, surface: pygame.Surface):
        """Отрисовка платформы на поверхности"""
        surface.blit(self.sprite, self.rect)


class MovingPlatformVertical(Obstacle):
    """Вертикально движущаяся платформа (лифт)"""

    def __init__(self, position: Position, height: int, move_range: int):
        """
        Инициализация вертикально движущейся платформы.

        :param position: Позиция платформы (x, y)
        :param height: Высота платформы
        :param move_range: Диапазон движения платформы
        """
        super().__init__(position, (100, height), ObjectType.MOVING_PLATFORM)
        self.sprite = moving_platform_sprite
        self.sprite = pygame.transform.scale(self.sprite, (100, height))
        self.original_y = position[1]  # Начальная позиция по y
        self.move_range = move_range  # Диапазон движения
        self.speed = 1  # Скорость движения
        self.direction = 1  # Направление движения (1 - вниз, -1 - вверх)

    def update(self):
        """Обновление состояния платформы"""
        self.rect.y += self.speed * self.direction  # Движение платформы
        if self.rect.y > self.original_y + self.move_range:
            self.direction = -1  # Изменение направления на противоположное
        elif self.rect.y < self.original_y - self.move_range:
            self.direction = 1  # Изменение направления на противоположное

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
            if platform.has_hole and platform.hole_rect and player_rect.colliderect(platform.hole_rect):
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
    """Первый уровень - увеличенное количество препятствий"""

    def generate_level(self):
        """Генерация первого уровня"""
        # Генерация платформ (3 уровня)
        platform_width = LEVEL_WIDTH // 2
        for i in range(PLATFORM_COUNT):
            y = SCREEN_HEIGHT - 150 - (i * PLATFORM_GAP)
            has_hole = random.choice([True, False]) if i == 0 else False
            self.platforms.append(Platform((100, y), platform_width, has_hole))
            self.platforms.append(Platform((platform_width + 200, y), platform_width, has_hole))

        # Добавляем вертикальные платформы на основные платформы
        for platform in self.platforms:
            # Вертикальные платформы в случайных местах на платформе
            for _ in range(2):
                x = random.randint(platform.rect.x + 50, platform.rect.x + platform.rect.width - 50)
                height = random.randint(50, 120)
                self.obstacles.append(StaticVerticalPlatform(
                    (x, platform.rect.y - height),
                    height
                ))

        # Горизонтальные платформы между основными платформами
        for i in range(PLATFORM_COUNT - 1):
            lower_platforms = [p for p in self.platforms if p.rect.y == SCREEN_HEIGHT - 150 - (i * PLATFORM_GAP)]
            upper_platforms = [p for p in self.platforms if p.rect.y == SCREEN_HEIGHT - 150 - ((i + 1) * PLATFORM_GAP)]

            for lower, upper in zip(lower_platforms, upper_platforms):
                # Горизонтальные платформы между уровнями
                x_positions = [
                    lower.rect.centerx - 100,
                    lower.rect.centerx + 100,
                    random.randint(lower.rect.x + 50, lower.rect.right - 150)
                ]

                for x in x_positions:
                    width = random.randint(80, 150)
                    y_gap = (upper.rect.bottom - lower.rect.top) // 2 + lower.rect.top
                    self.obstacles.append(StaticHorizontalPlatform(
                        (x, y_gap),
                        width
                    ))

        # Генерация стартового и финишного порталов
        start_platform = random.choice([p for p in self.platforms if p.rect.y == max(p.rect.y for p in self.platforms)])
        finish_platform = random.choice([p for p in self.platforms if p.rect.y != start_platform.rect.y])

        self.portals.append(Portal((start_platform.rect.x + 50, start_platform.rect.y - 100), False))
        self.portals.append(Portal((finish_platform.rect.x + finish_platform.rect.width - 110,
                                    finish_platform.rect.y - 100), True))

        # Генерация артефакта
        artifact_platform = random.choice([p for p in self.platforms
                                           if p != start_platform and p != finish_platform])
        self.artifacts.append(Artifact((artifact_platform.rect.x + 200, artifact_platform.rect.y - 50)))

        # Увеличенное количество шипов в ямах (в 2 раза больше)
        for platform in self.platforms:
            if platform.has_hole and platform.hole_rect:
                # Добавляем 2-3 шипа в каждую яму вместо 1
                for _ in range(random.randint(2, 3)):
                    offset = random.randint(-10, 10)
                    self.obstacles.append(Spike((platform.hole_rect.x + offset, platform.hole_rect.y - 32)))

        # Увеличенное количество горизонтальных шипов (в 3 раза больше)
        for platform in self.platforms:
            for _ in range(3):  # Было 1, стало 3
                x = random.randint(platform.rect.x + 50, platform.rect.x + platform.rect.width - 50)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        # Увеличенное количество движущихся платформ (в 2 раза больше)
        for i in range(4):  # Было 2, стало 4
            x = random.randint(200, LEVEL_WIDTH - 200)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            self.obstacles.append(MovingPlatformHorizontal((x, y), 100, random.randint(100, 200)))

        # Увеличенное количество лифтов (в 2 раза больше)
        for i in range(2):  # Было 1, стало 2
            x = random.randint(300, LEVEL_WIDTH - 300)
            y = random.randint(100, SCREEN_HEIGHT - 300)
            self.obstacles.append(MovingPlatformVertical((x, y), 50, random.randint(80, 150)))

        # Увеличенное количество дисковых пил (в 3 раза больше)
        for i in range(3):  # Было 1, стало 3
            x = random.randint(400, LEVEL_WIDTH - 400)
            y = random.randint(150, SCREEN_HEIGHT - 250)
            self.obstacles.append(CircularSaw((x, y), random.randint(150, 250)))

        # Генерация монет и бонусов (также увеличено количество)
        for i in range(50):  # Было 30, стало 50
            x = random.randint(100, LEVEL_WIDTH - 100)
            y = random.randint(50, SCREEN_HEIGHT - 150)
            self.bonuses.append(Coin((x, y)))


class Level2(Level1):
    """Второй уровень - еще больше препятствий"""

    def generate_level(self):
        """Генерация второго уровня"""
        super().generate_level()

        # Дополнительные артефакты (2 вместо 1)
        artifact_platform = random.choice([p for p in self.platforms
                                           if p.rect.y != self.artifacts[0].rect.y + 50])
        self.artifacts.append(Artifact((artifact_platform.rect.x + 300, artifact_platform.rect.y - 50)))

        # Дополнительные движущиеся платформы (6 всего)
        for i in range(2):  # Уже 4 от Level1, добавляем еще 2
            x = random.randint(200, LEVEL_WIDTH - 200)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            self.obstacles.append(MovingPlatformHorizontal((x, y), 80, random.randint(150, 250)))

        # Дополнительные пилы (5 всего)
        for i in range(2):  # Уже 3 от Level1, добавляем еще 2
            x = random.randint(400, LEVEL_WIDTH - 400)
            y = random.randint(150, SCREEN_HEIGHT - 250)
            self.obstacles.append(CircularSaw((x, y), random.randint(200, 300)))

        # Ямы на средних платформах с шипами
        for platform in self.platforms:
            if platform.rect.y == SCREEN_HEIGHT - 150 - PLATFORM_GAP and not platform.has_hole:
                platform.has_hole = True
                hole_width = random.randint(80, 180)
                hole_x = random.randint(50, platform.rect.width - hole_width - 50)
                platform.hole_rect = pygame.Rect(
                    platform.rect.x + hole_x,
                    platform.rect.y,
                    hole_width,
                    PLATFORM_HEIGHT
                )
                # Добавляем шипы в новые ямы
                for _ in range(random.randint(2, 3)):
                    offset = random.randint(-15, 15)
                    self.obstacles.append(Spike((platform.hole_rect.x + offset, platform.hole_rect.y - 32)))

        # Дополнительные горизонтальные шипы
        for platform in self.platforms:
            for i in range(2):
                x = random.randint(platform.rect.x + 50, platform.rect.x + platform.rect.width - 50)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))


class Level3(Level2):
    """Третий уровень - максимальное количество препятствий"""

    def generate_level(self):
        """Генерация третьего уровня"""
        super().generate_level()

        # Третий артефакт
        artifact_platform = random.choice([p for p in self.platforms
                                           if p.rect.y != self.artifacts[0].rect.y + 50
                                           and p.rect.y != self.artifacts[1].rect.y + 50])
        self.artifacts.append(Artifact((artifact_platform.rect.x + 400, artifact_platform.rect.y - 50)))

        # Ямы на верхних платформах с шипами
        for platform in self.platforms:
            if platform.rect.y == SCREEN_HEIGHT - 150 - 2 * PLATFORM_GAP and not platform.has_hole:
                platform.has_hole = True
                hole_width = random.randint(100, 200)
                hole_x = random.randint(50, platform.rect.width - hole_width - 50)
                platform.hole_rect = pygame.Rect(
                    platform.rect.x + hole_x,
                    platform.rect.y,
                    hole_width,
                    PLATFORM_HEIGHT
                )
                # Шипы в новых ямах
                for _ in range(random.randint(3, 4)):
                    offset = random.randint(-20, 20)
                    self.obstacles.append(Spike((platform.hole_rect.x + offset, platform.hole_rect.y - 32)))

        # Увеличение скорости всех опасных объектов
        for obstacle in self.obstacles:
            if isinstance(obstacle, (MovingPlatformHorizontal, MovingPlatformVertical, CircularSaw)):
                obstacle.speed += 1.5  # Большее увеличение скорости

        # Дополнительные горизонтальные шипы (в 2 раза больше чем на Level2)
        for platform in self.platforms:
            for i in range(4):
                x = random.randint(platform.rect.x + 50, platform.rect.x + platform.rect.width - 50)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        # Дополнительные дисковые пилы (всего 8)
        for i in range(3):  # Уже 5 от Level2, добавляем еще 3
            x = random.randint(300, LEVEL_WIDTH - 300)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            self.obstacles.append(CircularSaw((x, y), random.randint(250, 350)))

        # Дополнительные вертикальные шипы (в 2 раза больше чем на Level2)
        for platform in self.platforms:
            for i in range(4):
                y = random.randint(platform.rect.y + 50, platform.rect.y + platform.rect.height - 50)
                self.obstacles.append(Spike((platform.rect.x + 16, y), False))


class LevelManager:
    """Менеджер уровней"""

    def __init__(self):
        """Инициализация менеджера уровней"""
        self.current_level_num = 1  # Номер текущего уровня
        self.total_score = 0  # Общий счет
        self.total_artifacts = 0  # Общее количество собранных артефактов
        self.current_level = self.create_level(self.current_level_num)  # Создание текущего уровня

    def create_level(self, level_num: int) -> Level:
        """Создание уровня по номеру"""
        level_classes = {
            1: Level1,
            2: Level2,
            3: Level3
        }
        return level_classes[level_num](level_num)

    def update(self):
        """Обновление текущего уровня"""
        self.current_level.update()

    def draw(self, surface: pygame.Surface):
        """Отрисовка текущего уровня"""
        self.current_level.draw(surface)

        # Отрисовка счета и артефактов
        font = pygame.font.SysFont('Arial', 30)
        score_text = font.render(f'Score: {self.total_score + self.current_level.score}', True, (255, 255, 255))
        artifacts_text = font.render(
            f'Artifacts: {self.total_artifacts + self.current_level.artifacts_collected}/{self.current_level.artifacts_required}',
            True, (255, 255, 255))

        surface.blit(score_text, (20, 20))
        surface.blit(artifacts_text, (20, 60))

    def next_level(self) -> bool:
        """Переход на следующий уровень"""
        self.total_score += self.current_level.score
        self.total_artifacts += self.current_level.artifacts_collected

        if self.current_level_num < 3:
            self.current_level_num += 1
            self.current_level = self.create_level(self.current_level_num)
            return True
        return False  # Игра завершена

    def __init__(self):
        """Инициализация менеджера уровней"""
        self.current_level_num = 1
        self.total_score = 0
        self.total_artifacts = 0
        self.current_level = self.create_level(self.current_level_num)
        self.game_over = False  # Флаг завершения игры

    def is_game_complete(self) -> bool:
        """Проверка завершения всех уровней"""
        return self.current_level_num == 3 and self.current_level.completed

    def get_level_completion_message(self) -> str:
        """Сообщение о завершении уровня"""
        if self.current_level.completed:
            if self.current_level_num < 3:
                return f"Level {self.current_level_num} complete! Score: {self.total_score}"
            else:
                return f"Game completed! Final score: {self.total_score}"
        return ""

    def update(self, player_rect: pygame.Rect):
        """Обновление текущего уровня с проверкой положения игрока"""
        if self.current_level.check_player_fell(player_rect):
            self.game_over = True
        self.current_level.update()

    def is_game_over(self) -> bool:
        """Проверка завершения игры (игрок упал)"""
        return self.game_over

    def reset(self):
        """Сброс менеджера уровней для новой игры"""
        self.current_level_num = 1
        self.total_score = 0
        self.total_artifacts = 0
        self.current_level = self.create_level(self.current_level_num)
        self.game_over = False