import pygame
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Type

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
        """Проверка коллизии с другим объектом (заглушка)"""
        return self.rect.colliderect(other_rect)


class Obstacle(GameObject):
    """Базовый класс препятствий"""
    pass


class Spike(Obstacle):
    """Статичные шипы"""

    def __init__(self, position: Position):
        super().__init__(position, (32, 32))
        self.color = (139, 0, 0)  # Темно-красный

    def update(self):
        pass  # Шипы статичны

    def draw(self, surface: pygame.Surface):
        pygame.draw.polygon(surface, self.color, [
            (self.rect.left, self.rect.bottom),
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom)
        ])


class Pit(Obstacle):
    """Ямы различной ширины"""

    def __init__(self, position: Position, width: int):
        super().__init__(position, (width, 50))
        self.color = (0, 0, 0)  # Черный

    def update(self):
        pass  # Ямы статичны

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


class MovingObstacle(Obstacle):
    """Объекты с патрулирующим движением"""

    def __init__(self, position: Position, size: Size, move_range: int):
        super().__init__(position, size)
        self.original_x = position[0]
        self.move_range = move_range
        self.speed = 2
        self.direction = 1
        self.color = (255, 165, 0)  # Оранжевый

    def update(self):
        self.rect.x += self.speed * self.direction

        # Разворот при достижении границы движения
        if self.rect.x > self.original_x + self.move_range:
            self.direction = -1
        elif self.rect.x < self.original_x - self.move_range:
            self.direction = 1

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


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
    """Базовые монеты (100 очков)"""

    def __init__(self, position: Position):
        super().__init__(position, (16, 16), 100)
        self.color = (255, 215, 0)  # Золотой

    def update(self):
        pass  # Монеты статичны

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)


class SpecialBonus(Bonus):
    """Специальные бонусы (500 очков)"""

    def __init__(self, position: Position):
        super().__init__(position, (24, 24), 500)
        self.color = (0, 255, 255)  # Голубой
        self.animation_counter = 0

    def update(self):
        # Простая анимация пульсации
        self.animation_counter = (self.animation_counter + 0.1) % 360
        size_factor = 1 + 0.1 * abs(pygame.math.Vector2(1, 0).rotate(self.animation_counter).x)
        self.rect.width = int(24 * size_factor)
        self.rect.height = int(24 * size_factor)

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)


class Level(ABC):
    """Абстрактный базовый класс уровня"""

    def __init__(self, level_num: int, screen_size: Tuple[int, int]):
        self.level_num = level_num
        self.screen_width, self.screen_height = screen_size
        self.difficulty = level_num  # 1x-5x
        self.completed = False
        self.score = 0

        # Игровые объекты
        self.obstacles: List[Obstacle] = []
        self.bonuses: List[Bonus] = []

        # Позиции игрока и финиша
        self.player_start_pos = (100, screen_size[1] - 100)
        self.finish_rect = pygame.Rect(screen_size[0] - 100, screen_size[1] - 150, 50, 100)

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

    def draw(self, surface: pygame.Surface):
        """Отрисовка уровня"""
        # Фон (заглушка)
        surface.fill((50, 50, 70))  # Темно-синий

        # Отрисовка объектов
        for obstacle in self.obstacles:
            if obstacle.is_active:
                obstacle.draw(surface)

        for bonus in self.bonuses:
            if bonus.is_active:
                bonus.draw(surface)

        # Отрисовка финиша (заглушка)
        pygame.draw.rect(surface, (0, 255, 0), self.finish_rect)

    def check_finish(self, player_rect: pygame.Rect) -> bool:
        """Проверка достижения финиша"""
        return player_rect.colliderect(self.finish_rect)

    def collect_bonuses(self, player_rect: pygame.Rect) -> int:
        """Сбор бонусов игроком"""
        collected_points = 0
        for bonus in self.bonuses:
            if bonus.is_active and bonus.check_collision(player_rect):
                collected_points += bonus.collect()
        return collected_points

    def get_active_bonuses_count(self) -> int:
        """Количество оставшихся бонусов"""
        return sum(1 for bonus in self.bonuses if bonus.is_active)


class Level1(Level):
    """Первый уровень"""

    def generate_level(self):
        # Генерация препятствий (10 штук)
        for _ in range(10):
            # Случайный выбор типа препятствия
            obstacle_type = random.choice([Spike, Pit, MovingObstacle])

            if obstacle_type == Spike:
                x = random.randint(200, self.screen_width - 100)
                y = self.screen_height - 50
                self.obstacles.append(Spike((x, y)))

            elif obstacle_type == Pit:
                width = random.randint(50, 150)
                x = random.randint(200, self.screen_width - width - 100)
                y = self.screen_height - 50
                self.obstacles.append(Pit((x, y), width))

            elif obstacle_type == MovingObstacle:
                x = random.randint(200, self.screen_width - 200)
                y = random.randint(100, self.screen_height - 150)
                size = (random.randint(30, 60), random.randint(30, 60))
                move_range = random.randint(50, 150)
                self.obstacles.append(MovingObstacle((x, y), size, move_range))

        # Генерация бонусов (20 монет)
        for _ in range(20):
            x = random.randint(150, self.screen_width - 150)
            y = random.randint(50, self.screen_height - 100)
            self.bonuses.append(Coin((x, y)))


class Level2(Level1):
    """Второй уровень (наследуем от Level1 и модифицируем)"""

    def generate_level(self):
        super().generate_level()
        # Добавляем еще 10 препятствий (итого 20)
        for _ in range(10):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(100, self.screen_height - 150)
            size = (random.randint(30, 60), random.randint(30, 60))
            move_range = random.randint(50, 200)
            self.obstacles.append(MovingObstacle((x, y), size, move_range))

        # Добавляем еще 20 монет (итого 40)
        for _ in range(20):
            x = random.randint(150, self.screen_width - 150)
            y = random.randint(50, self.screen_height - 100)
            self.bonuses.append(Coin((x, y)))

        # Добавляем 2 специальных бонуса
        for _ in range(2):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(100, self.screen_height - 150)
            self.bonuses.append(SpecialBonus((x, y)))


class Level3(Level2):
    """Третий уровень"""

    def generate_level(self):
        super().generate_level()
        # Добавляем еще 10 препятствий (итого 30)
        for _ in range(10):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(50, self.screen_height - 200)
            size = (random.randint(20, 40), random.randint(20, 40))
            move_range = random.randint(100, 250)
            self.obstacles.append(MovingObstacle((x, y), size, move_range))

        # Добавляем еще 20 монет (итого 60)
        for _ in range(20):
            x = random.randint(150, self.screen_width - 150)
            y = random.randint(50, self.screen_height - 100)
            self.bonuses.append(Coin((x, y)))

        # Добавляем 3 специальных бонуса
        for _ in range(3):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(100, self.screen_height - 150)
            self.bonuses.append(SpecialBonus((x, y)))


class Level4(Level3):
    """Четвертый уровень"""

    def generate_level(self):
        super().generate_level()
        # Добавляем еще 10 препятствий (итого 40)
        for _ in range(10):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(50, self.screen_height - 200)
            self.obstacles.append(Spike((x, y)))

        # Добавляем еще 20 монет (итого 80)
        for _ in range(20):
            x = random.randint(150, self.screen_width - 150)
            y = random.randint(50, self.screen_height - 100)
            self.bonuses.append(Coin((x, y)))

        # Добавляем 4 специальных бонуса
        for _ in range(4):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(100, self.screen_height - 150)
            self.bonuses.append(SpecialBonus((x, y)))


class Level5(Level4):
    """Пятый уровень"""

    def generate_level(self):
        super().generate_level()
        # Добавляем еще 10 препятствий (итого 50)
        for _ in range(10):
            width = random.randint(80, 200)
            x = random.randint(200, self.screen_width - width - 100)
            y = self.screen_height - 50
            self.obstacles.append(Pit((x, y), width))

        # Добавляем еще 20 монет (итого 100)
        for _ in range(20):
            x = random.randint(150, self.screen_width - 150)
            y = random.randint(50, self.screen_height - 100)
            self.bonuses.append(Coin((x, y)))

        # Добавляем 5 специальных бонусов
        for _ in range(5):
            x = random.randint(200, self.screen_width - 200)
            y = random.randint(100, self.screen_height - 150)
            self.bonuses.append(SpecialBonus((x, y)))


class LevelManager:
    """Менеджер уровней"""

    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.current_level_num = 1
        self.total_score = 0
        self.current_level = self.create_level(self.current_level_num)

    def create_level(self, level_num: int) -> Level:
        """Создание уровня по номеру"""
        level_classes = {
            1: Level1,
            2: Level2,
            3: Level3,
            4: Level4,
            5: Level5
        }
        return level_classes[level_num](level_num, self.screen_size)

    def update(self):
        """Обновление текущего уровня"""
        self.current_level.update()

    def draw(self, surface: pygame.Surface):
        """Отрисовка текущего уровня"""
        self.current_level.draw(surface)

    def next_level(self) -> bool:
        """Переход на следующий уровень"""
        self.total_score += self.current_level.score

        if self.current_level_num < 5:
            self.current_level_num += 1
            self.current_level = self.create_level(self.current_level_num)
            return True
        return False  # Игра завершена

    def is_game_complete(self) -> bool:
        """Проверка завершения всех уровней"""
        return self.current_level_num == 5 and self.current_level.completed

    def get_level_completion_message(self) -> str:
        """Сообщение о завершении уровня"""
        if self.current_level.completed:
            if self.current_level_num < 5:
                return f"Уровень {self.current_level_num} пройден! Счет: {self.total_score}"
            else:
                return f"Игра завершена! Итоговый счет: {self.total_score}"
        return ""