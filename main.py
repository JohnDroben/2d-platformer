import pygame
import sys
from levels import LevelManager, LEVEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT
from custom_logging import Logger

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer - Level Demo")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (20, 30, 15)

# Шрифт
font = pygame.font.SysFont('Arial', 24)


class DemoPlayer:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.speed = 5  # Скорость автоматического движения
        self.color = BLUE
        self.is_active = True

    def update(self, level):
        if not self.is_active:
            return

        # Автоматическое движение вправо
        self.rect.x += self.speed

        # Проверка выхода за границы уровня
        if self.rect.x > LEVEL_WIDTH:
            self.rect.x = -self.rect.width

        # Проверка финиша
        if level.check_finish(self.rect):
            level.completed = True
            self.is_active = False

    def draw(self, surface, camera_offset):
        player_rect = self.rect.move(camera_offset[0], camera_offset[1])
        pygame.draw.rect(surface, self.color, player_rect)
        pygame.draw.circle(surface, WHITE, (player_rect.right - 10, player_rect.top + 15), 5)
        pygame.draw.circle(surface, WHITE, (player_rect.right - 10, player_rect.top + 35), 5)


def main():
    clock = pygame.time.Clock()
    level_manager = LevelManager()
    Logger().initialize()

    # Инициализация игрока у стартового портала
    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (100, SCREEN_HEIGHT - 150)
    player = DemoPlayer(*start_pos)

    # Параметры камеры
    camera_offset = [0, 0]
    running = True

    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and level_manager.current_level.completed:
                    if not level_manager.next_level():
                        Logger().info("Демо завершено!")
                        running = False
                    else:
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                        player = DemoPlayer(*start_pos)

        # Обновление
        if not level_manager.current_level.completed:
            player.update(level_manager.current_level)

            # Позиция камеры (следим за игроком)
            camera_offset[0] = SCREEN_WIDTH // 2 - player.rect.centerx
            # Ограничиваем камеру границами уровня
            camera_offset[0] = max(min(camera_offset[0], 0), SCREEN_WIDTH - LEVEL_WIDTH)
        else:
            # Автопереход на следующий уровень через 3 секунды
            if pygame.time.get_ticks() - level_manager.current_level.completion_time > 3000:
                if not level_manager.next_level():
                    running = False
                else:
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                    player = DemoPlayer(*start_pos)

        # Отрисовка
        screen.fill(DARK_GREEN)

        # Отрисовка уровня с учетом смещения камеры
        level_surface = pygame.Surface((LEVEL_WIDTH, SCREEN_HEIGHT))
        level_manager.current_level.draw(level_surface)
        screen.blit(level_surface, camera_offset)

        # Отрисовка игрока
        player.draw(screen, camera_offset)

        # UI
        info_y = 20
        for text in [
            f"Уровень: {level_manager.current_level_num}/3",
            f"Счет: {level_manager.total_score + level_manager.current_level.score}",
            f"Артефакты: {level_manager.current_level.artifacts_collected}/{level_manager.current_level.artifacts_required}"
        ]:
            screen.blit(font.render(text, True, WHITE), (20, info_y))
            info_y += 30

        if level_manager.current_level.completed:
            text = font.render(level_manager.get_level_completion_message(), True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()