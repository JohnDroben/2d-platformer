import pygame
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Type
from custom_logging import Logger

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
LEVEL_WIDTH = SCREEN_WIDTH * 3  # Ширина уровня в 3 экрана
PLATFORM_HEIGHT = 30
PLATFORM_COUNT = 3  # Количество платформ на уровне
PLATFORM_GAP = 200  # Вертикальный отступ между платформами

# Типы для аннотаций
Color = Tuple[int, int, int]
Position = Tuple[int, int]
Size = Tuple[int, int]


class GameObject(ABC):
    """Базовый класс для всех игровых объектов"""
    def __init__(self, position: Position, size: Size):
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.is_active = True
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
    def __init__(self, position: Position, size: Size, points: int):
        super().__init__(position, size)
        self.points = points

    def collect(self) -> int:
        """Сбор бонуса"""
        self.is_active = False
        return self.points

class Coin(Bonus):
    """Монеты - базовые бонусы"""
    def __init__(self, position: Position):
        super().__init__(position, (16, 16), 100)
        self.color = (255, 215, 0)  # Золотой

    def update(self):
        pass

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)

class Obstacle(GameObject):
    """Базовый класс препятствий"""
    pass


class Platform(GameObject):
    """Класс платформы для передвижения игрока"""

    def __init__(self, position: Position, width: int, has_hole: bool = False):
        super().__init__(position, (width, PLATFORM_HEIGHT))
        self.color = (100, 100, 100)  # Серый цвет
        self.has_hole = has_hole
        self.hole_rect = None
        if has_hole:
            hole_width = random.randint(50, 150)
            hole_x = random.randint(50, width - hole_width - 50)
            self.hole_rect = pygame.Rect(
                position[0] + hole_x,
                position[1],
                hole_width,
                PLATFORM_HEIGHT
            )

    def update(self):
        pass

    def draw(self, surface: pygame.Surface):
        if not self.has_hole:
            pygame.draw.rect(surface, self.color, self.rect)
        else:
            # Рисуем платформу с дыркой
            pygame.draw.rect(surface, self.color,
                             pygame.Rect(self.rect.left, self.rect.top,
                                         self.hole_rect.left - self.rect.left,
                                         PLATFORM_HEIGHT))
            pygame.draw.rect(surface, self.color,
                             pygame.Rect(self.hole_rect.right, self.rect.top,
                                         self.rect.right - self.hole_rect.right,
                                         PLATFORM_HEIGHT))


class Spike(Obstacle):
    """Шипы - опасные препятствия"""

    def __init__(self, position: Position, horizontal: bool = False):
        size = (32, 16) if horizontal else (32, 32)
        super().__init__(position, size)
        self.color = (139, 0, 0)  # Темно-красный
        self.horizontal = horizontal

    def update(self):
        pass

    def draw(self, surface: pygame.Surface):
        if self.horizontal:
            pygame.draw.polygon(surface, self.color, [
                (self.rect.left, self.rect.centery),
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.centery)
            ])
        else:
            pygame.draw.polygon(surface, self.color, [
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.bottom)
            ])


class MovingPlatformHorizontal(Obstacle):
    """Горизонтально движущаяся платформа для преодоления ям"""

    def __init__(self, position: Position, width: int, move_range: int):
        super().__init__(position, (width, PLATFORM_HEIGHT))
        self.original_x = position[0]
        self.move_range = move_range
        self.speed = 2
        self.direction = 1
        self.color = (150, 75, 0)  # Коричневый

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x > self.original_x + self.move_range:
            self.direction = -1
        elif self.rect.x < self.original_x - self.move_range:
            self.direction = 1

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


class MovingPlatformVertical(Obstacle):
    """Вертикально движущаяся платформа (лифт)"""

    def __init__(self, position: Position, height: int, move_range: int):
        super().__init__(position, (100, height))
        self.original_y = position[1]
        self.move_range = move_range
        self.speed = 1
        self.direction = 1
        self.color = (150, 150, 150)  # Светло-серый

    def update(self):
        self.rect.y += self.speed * self.direction
        if self.rect.y > self.original_y + self.move_range:
            self.direction = -1
        elif self.rect.y < self.original_y - self.move_range:
            self.direction = 1

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


class CircularSaw(Obstacle):
    """Дисковая пила - движется вертикально между платформами"""

    def __init__(self, position: Position, move_range: int):
        super().__init__(position, (50, 50))
        self.original_y = position[1]
        self.move_range = move_range
        self.speed = 3
        self.direction = 1
        self.color = (200, 200, 200)  # Металлический

    def update(self):
        self.rect.y += self.speed * self.direction
        if self.rect.y > self.original_y + self.move_range:
            self.direction = -1
        elif self.rect.y < self.original_y - self.move_range:
            self.direction = 1

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)
        # Зубья пилы
        for i in range(8):
            angle = i * (360 / 8)
            end_pos = (
                self.rect.centerx + (self.rect.width // 2 + 5) * pygame.math.Vector2(1, 0).rotate(angle).x,
                self.rect.centery + (self.rect.height // 2 + 5) * pygame.math.Vector2(1, 0).rotate(angle).y
            )
            pygame.draw.line(surface, (255, 0, 0), self.rect.center, end_pos, 3)


class Artifact(Bonus):
    """Артефакт - специальный бонус для завершения уровня"""

    def __init__(self, position: Position):
        super().__init__(position, (40, 40), 1000)
        self.color = (255, 215, 0)  # Золотой
        self.animation_angle = 0

    def update(self):
        self.animation_angle = (self.animation_angle + 2) % 360

    def draw(self, surface: pygame.Surface):
        # Основа артефакта
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)

        # Анимация сияния
        for i in range(0, 360, 45):
            angle = (self.animation_angle + i) % 360
            end_pos = (
                self.rect.centerx + (self.rect.width) * pygame.math.Vector2(1, 0).rotate(angle).x,
                self.rect.centery + (self.rect.height) * pygame.math.Vector2(1, 0).rotate(angle).y
            )
            pygame.draw.line(surface, (255, 255, 0), self.rect.center, end_pos, 3)


class Portal(GameObject):
    """Портал для старта и финиша уровня"""

    def __init__(self, position: Position, is_finish: bool = False):
        super().__init__(position, (60, 100))
        self.is_finish = is_finish
        self.color = (0, 255, 0) if is_finish else (255, 0, 0)
        self.animation_phase = 0
        self.active = not is_finish  # Стартовый портал всегда активен

    def update(self):
        self.animation_phase = (self.animation_phase + 0.1) % 360

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # Основа портала
        pygame.draw.rect(surface, self.color, self.rect, 3)

        # Анимация портала
        for i in range(0, 360, 30):
            angle = (self.animation_phase + i) % 360
            radius = 20 + 10 * abs(pygame.math.Vector2(1, 0).rotate(angle).x)
            pos = (
                self.rect.centerx + (self.rect.width // 3) * pygame.math.Vector2(1, 0).rotate(angle).x,
                self.rect.centery + (self.rect.height // 3) * pygame.math.Vector2(1, 0).rotate(angle).y
            )
            pygame.draw.circle(surface, self.color, pos, int(radius))

    def activate(self):
        self.active = True


class Level(ABC):
    """Абстрактный базовый класс уровня"""

    def __init__(self, level_num: int):
        self.level_num = level_num
        self.width = LEVEL_WIDTH
        self.height = SCREEN_HEIGHT
        self.completed = False
        self.score = 0
        self.artifacts_collected = 0
        self.artifacts_required = level_num  # Для 1 уровня - 1 артефакт и т.д.

        # Игровые объекты
        self.platforms: List[Platform] = []
        self.obstacles: List[Obstacle] = []
        self.bonuses: List[Bonus] = []
        self.artifacts: List[Artifact] = []
        self.portals: List[Portal] = []

        # Генерация уровня
        self.generate_level()

    @abstractmethod
    def generate_level(self):
        """Генерация элементов уровня"""
        pass

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
        # Фон (лес с механизмами)
        surface.fill((20, 30, 15))  # Темно-зеленый

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

    def get_active_artifacts_count(self) -> int:
        """Количество оставшихся артефактов"""
        return sum(1 for artifact in self.artifacts if artifact.is_active)


class Level1(Level):
    """Первый уровень - древний механический лес"""

    def generate_level(self):
        # Генерация платформ (3 уровня)
        platform_width = LEVEL_WIDTH // 2
        for i in range(PLATFORM_COUNT):
            y = SCREEN_HEIGHT - 150 - (i * PLATFORM_GAP)
            has_hole = random.choice([True, False]) if i == 0 else False  # Ямы только на нижней платформе
            self.platforms.append(Platform((100, y), platform_width, has_hole))
            self.platforms.append(Platform((platform_width + 200, y), platform_width, has_hole))

        # Генерация стартового и финишного порталов (на разных платформах)
        start_platform = random.choice([p for p in self.platforms if p.rect.y == max(p.rect.y for p in self.platforms)])
        finish_platform = random.choice([p for p in self.platforms if p.rect.y != start_platform.rect.y])

        self.portals.append(Portal((start_platform.rect.x + 50, start_platform.rect.y - 100), False))
        self.portals.append(Portal((finish_platform.rect.x + finish_platform.rect.width - 110,
                                    finish_platform.rect.y - 100), True))

        # Генерация артефакта (1 штука)
        artifact_platform = random.choice([p for p in self.platforms
                                           if p != start_platform and p != finish_platform])
        self.artifacts.append(Artifact((artifact_platform.rect.x + 200, artifact_platform.rect.y - 50)))

        # Генерация шипов в ямах
        for platform in self.platforms:
            if platform.has_hole and platform.hole_rect and random.choice([True, False]):
                self.obstacles.append(Spike((platform.hole_rect.x, platform.hole_rect.y - 32)))

        # Генерация горизонтальных шипов
        for platform in self.platforms:
            if random.choice([True, False]):
                x = random.randint(platform.rect.x + 100, platform.rect.x + platform.rect.width - 100)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))

        # Генерация движущихся платформ
        for i in range(2):
            x = random.randint(200, LEVEL_WIDTH - 200)
            y = random.randint(SCREEN_HEIGHT - 300, SCREEN_HEIGHT - 150)
            self.obstacles.append(MovingPlatformHorizontal((x, y), 100, 150))

        # Генерация лифтов
        for i in range(1):
            x = random.randint(300, LEVEL_WIDTH - 300)
            y = random.randint(SCREEN_HEIGHT - 400, SCREEN_HEIGHT - 200)
            self.obstacles.append(MovingPlatformVertical((x, y), 50, 100))

        # Генерация дисковых пил
        for i in range(1):
            x = random.randint(400, LEVEL_WIDTH - 400)
            y = random.randint(SCREEN_HEIGHT - 350, SCREEN_HEIGHT - 150)
            self.obstacles.append(CircularSaw((x, y), 150))

        # Генерация монет и бонусов
        for i in range(30):
            x = random.randint(100, LEVEL_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            self.bonuses.append(Coin((x, y)))


class Level2(Level1):
    """Второй уровень - увеличиваем сложность"""

    def generate_level(self):
        super().generate_level()
        # Добавляем еще артефакт (всего 2)
        artifact_platform = random.choice([p for p in self.platforms
                                           if p.rect.y != self.artifacts[0].rect.y + 50])  # На другой платформе
        self.artifacts.append(Artifact((artifact_platform.rect.x + 300, artifact_platform.rect.y - 50)))

        # Увеличиваем количество движущихся платформ
        for i in range(2):
            x = random.randint(200, LEVEL_WIDTH - 200)
            y = random.randint(SCREEN_HEIGHT - 400, SCREEN_HEIGHT - 150)
            self.obstacles.append(MovingPlatformHorizontal((x, y), 80, 200))

        # Добавляем больше пил
        for i in range(2):
            x = random.randint(400, LEVEL_WIDTH - 400)
            y = random.randint(SCREEN_HEIGHT - 350, SCREEN_HEIGHT - 150)
            self.obstacles.append(CircularSaw((x, y), 200))

        # Добавляем ямы на среднюю платформу
        for platform in self.platforms:
            if platform.rect.y == SCREEN_HEIGHT - 150 - PLATFORM_GAP and not platform.has_hole:
                platform.has_hole = random.choice([True, False])
                if platform.has_hole:
                    hole_width = random.randint(50, 150)
                    hole_x = random.randint(50, platform.rect.width - hole_width - 50)
                    platform.hole_rect = pygame.Rect(
                        platform.rect.x + hole_x,
                        platform.rect.y,
                        hole_width,
                        PLATFORM_HEIGHT
                    )


class Level3(Level2):
    """Третий уровень - максимальная сложность"""

    def generate_level(self):
        super().generate_level()
        # Добавляем третий артефакт
        artifact_platform = random.choice([p for p in self.platforms
                                           if p.rect.y != self.artifacts[0].rect.y + 50
                                           and p.rect.y != self.artifacts[1].rect.y + 50])
        self.artifacts.append(Artifact((artifact_platform.rect.x + 400, artifact_platform.rect.y - 50)))

        # Добавляем ямы на верхнюю платформу
        for platform in self.platforms:
            if platform.rect.y == SCREEN_HEIGHT - 150 - 2 * PLATFORM_GAP and not platform.has_hole:
                platform.has_hole = True
                hole_width = random.randint(80, 180)
                hole_x = random.randint(50, platform.rect.width - hole_width - 50)
                platform.hole_rect = pygame.Rect(
                    platform.rect.x + hole_x,
                    platform.rect.y,
                    hole_width,
                    PLATFORM_HEIGHT
                )

        # Увеличиваем количество и скорость опасных объектов
        for obstacle in self.obstacles:
            if isinstance(obstacle, (MovingPlatformHorizontal, MovingPlatformVertical, CircularSaw)):
                obstacle.speed += 1

        # Добавляем больше горизонтальных шипов
        for platform in self.platforms:
            for i in range(2):
                x = random.randint(platform.rect.x + 100, platform.rect.x + platform.rect.width - 100)
                self.obstacles.append(Spike((x, platform.rect.y - 16), True))


class LevelManager:
    """Менеджер уровней"""

    def __init__(self):
        self.current_level_num = 1
        self.total_score = 0
        self.total_artifacts = 0
        self.current_level = self.create_level(self.current_level_num)

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