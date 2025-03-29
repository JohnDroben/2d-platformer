import pygame
import sys
from levels import LevelManager, LEVEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT
from custom_logging import Logger

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (20, 30, 15)

# Шрифт
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 72)  # Для Game Over текста


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.color = BLUE
        self.speed = 5
        self.jump_power = 12
        self.vertical_momentum = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, level):
        # Гравитация
        self.vertical_momentum += 0.5
        self.rect.y += self.vertical_momentum

        # Проверка нахождения на платформе
        self.on_ground = False
        for platform in level.platforms:
            if (self.rect.bottom >= platform.rect.top and
                    self.rect.bottom <= platform.rect.top + 10 and
                    self.rect.right > platform.rect.left and
                    self.rect.left < platform.rect.right and
                    not (platform.has_hole and
                         platform.hole_rect and
                         self.rect.centerx > platform.hole_rect.left and
                         self.rect.centerx < platform.hole_rect.right)):
                self.rect.bottom = platform.rect.top
                self.vertical_momentum = 0
                self.on_ground = True
                break

        # Ограничение по границам уровня
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vertical_momentum = -self.jump_power
            self.on_ground = False

    def draw(self, surface, camera_offset):
        player_rect = self.rect.move(camera_offset[0], camera_offset[1])
        pygame.draw.rect(surface, self.color, player_rect)

        # Отрисовка глаз (смотрят в направлении движения)
        eye_offset = 10 if self.facing_right else -10
        pygame.draw.circle(surface, WHITE, (player_rect.centerx + eye_offset, player_rect.top + 15), 5)
        pygame.draw.circle(surface, WHITE, (player_rect.centerx + eye_offset, player_rect.top + 35), 5)


def main():
    clock = pygame.time.Clock()
    level_manager = LevelManager()
    level_manager.reset()
    Logger().initialize()

    # Инициализация игрока у стартового портала
    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (100, SCREEN_HEIGHT - 150)
    player = Player(*start_pos)
    level_manager.current_level.remove_start_portal() # удаляем стартовый портал после появления игрока, чтобы он не двигалс

    # Камера
    camera_offset = [0, 0]
    running = True
    game_over = False  # Флаг состояния Game Over

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
                        Logger().info("Игра завершена!")
                        running = False
                    else:
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player = Player(*start_pos)
                elif event.key == pygame.K_r and game_over:  # Рестарт по нажатию R
                    # Сброс игры
                    level_manager.reset()
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                    player = Player(*start_pos)
                    level_manager.current_level.remove_start_portal()  # Добавляем удаление портала
                    game_over = False

        # Обновление
        if not level_manager.current_level.completed and not game_over:
            player.handle_input()
            player.update(level_manager.current_level)

            # Проверка падения за экран (Game Over)
            if player.rect.top > SCREEN_HEIGHT:
                game_over = True

            # Проверка опасных столкновений
            if level_manager.current_level.check_hazard_collision(player.rect):
                # Респавн при смерти
                start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                player = Player(*start_pos)

            # Проверка падения в яму
            if level_manager.current_level.check_fall_into_pit(player.rect):
                start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                player = Player(*start_pos)

            # Сбор бонусов и артефактов
            level_manager.current_level.collect_bonuses(player.rect)
            level_manager.current_level.collect_artifacts(player.rect)

            # Проверка финиша
            if level_manager.current_level.check_finish(player.rect):
                level_manager.current_level.completed = True
                level_manager.current_level.completion_time = pygame.time.get_ticks()

            # Позиция камеры
            camera_offset[0] = SCREEN_WIDTH // 2 - player.rect.centerx
            camera_offset[0] = max(min(camera_offset[0], 0), SCREEN_WIDTH - LEVEL_WIDTH)
        elif level_manager.current_level.completed and not game_over:
            # Автопереход на следующий уровень
            if pygame.time.get_ticks() - level_manager.current_level.completion_time > 3000:
                if not level_manager.next_level():
                    running = False
                else:
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                    player = Player(*start_pos)

        # Отрисовка
        screen.fill(DARK_GREEN)

        # Отрисовка уровня
        level_surface = pygame.Surface((LEVEL_WIDTH, SCREEN_HEIGHT))
        level_manager.current_level.draw(level_surface)
        screen.blit(level_surface, camera_offset)

        # Отрисовка игрока
        if not game_over:
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

        # Отрисовка Game Over экрана
        if game_over:
            # Затемнение экрана
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))

            # Текст Game Over
            game_over_text = large_font.render("GAME OVER", True, RED)
            restart_text = font.render("Нажмите R для рестарта", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                       SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()