import pygame
import sys
from levels import LevelManager, Spike, Pit
from custom_logging import Logger

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer - Level System Demo")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Шрифт
font = pygame.font.SysFont('Arial', 24)


class DemoPlayer:
    """Демонстрационный игрок для автоматической прокрутки уровней"""

    def __init__(self):
        self.rect = pygame.Rect(100, SCREEN_HEIGHT - 100, 30, 50)
        self.speed = 3
        self.is_moving = True
        self.color = RED

    def update(self, level):
        """Автоматическое движение игрока"""
        if self.is_moving:
            self.rect.x += self.speed

            # Проверка столкновений с препятствиями (упрощенная)
            for obstacle in level.obstacles:
                if obstacle.rect.colliderect(self.rect):
                    if isinstance(obstacle, Spike):
                        self.color = (255, 0, 0)  # Красный при столкновении с шипами
                    elif isinstance(obstacle, Pit):
                        self.rect.y = SCREEN_HEIGHT - 100  # "Падение" в яму
                    break

            # Проверка сбора бонусов
            collected = level.collect_bonuses(self.rect)
            if collected > 0:
                level.score += collected
                self.color = GREEN  # Зеленый при сборе бонусов
                pygame.time.delay(50)  # Мигание

            # Возврат к нормальному цвету
            if self.color == GREEN and pygame.time.get_ticks() % 200 < 100:
                self.color = RED

            # Проверка достижения финиша
            if level.check_finish(self.rect):
                level.completed = True
                self.is_moving = False

    def draw(self, surface):
        """Отрисовка игрока"""
        pygame.draw.rect(surface, self.color, self.rect)


def main():
    """Основной игровой цикл"""
    clock = pygame.time.Clock()
    level_manager = LevelManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    player = DemoPlayer()
    Logger().initialize()
    # Автоматическое переключение уровней
    auto_level_switch = False
    switch_timer = 0
    running = True
    Logger().info("Игра начата!")
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Ручное переключение уровней
                    if level_manager.current_level.completed:
                        if not level_manager.next_level():
                            Logger().info("Игра завершена!")
                            running = False
                        else:
                            player = DemoPlayer()

        # Обновление игрового состояния
        if not level_manager.current_level.completed:
            player.update(level_manager.current_level)
        else:
            # Автоматическое переключение через 3 секунды
            if not auto_level_switch:
                auto_level_switch = True
                switch_timer = pygame.time.get_ticks()

            if auto_level_switch and pygame.time.get_ticks() - switch_timer > 3000:
                if not level_manager.next_level():
                    Logger().info("Игра завершена!")
                    running = False
                else:
                    player = DemoPlayer()
                    auto_level_switch = False

        level_manager.update()

        # Отрисовка
        level_manager.draw(screen)
        player.draw(screen)

        # Отображение информации
        level_text = font.render(f"Уровень: {level_manager.current_level_num}", True, WHITE)
        score_text = font.render(f"Счет: {level_manager.current_level.score}", True, WHITE)
        total_text = font.render(f"Общий счет: {level_manager.total_score}", True, WHITE)

        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(total_text, (10, 70))

        if level_manager.current_level.completed:
            completion_text = font.render(level_manager.get_level_completion_message(), True, WHITE)
            screen.blit(completion_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()