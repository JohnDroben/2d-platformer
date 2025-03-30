import pygame
import sys

from Characters.Hero.hero import Hero
from levels import LevelManager, LEVEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT
from custom_logging import Logger

from Characters.action import Action
from Characters.animation2 import AnimatedObject


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

ground_level = SCREEN_HEIGHT+200


def create_player(x, y):
    player = Hero(
        x=x,  # Стартовая позиция X (не привязывать к ground_level)
        y=y,  # Ставим на поверхность (ground_level - высота)
        width=60,  # Ширина hitbox (рекомендую уменьшить)
        height=80,  # Высота hitbox (рекомендую уменьшить)
        speed=8.0,  # Оптимальная скорость движения
        jump_force=12,  # Сила прыжка
        gravity=0.6,  # Гравитация
        ground_level=ground_level  # Уровень земли
    )
    player_anim = AnimatedObject(player)
    # Для каждого действия указываем файл и количество кадров
    player_anim.load_action_frames(Action.IDLE, 'Characters/assets/sprites/idle.png', 7)
    player_anim.load_action_frames(Action.MOVE, 'Characters/assets/sprites/idle.png', 7)

    player_anim.load_action_frames(Action.JUMP, 'Characters/assets/sprites/jump.png', 13)
    player_anim.load_action_frames(Action.SIT, 'Characters/assets/sprites/sit.png', 4, True)
    player_anim.load_action_frames(Action.SIT_MOVE, 'Characters/assets/sprites/sit.png', 4, True)
    player_anim.load_action_frames(Action.SIT_IDLE, 'Characters/assets/sprites/sit.png', 4, True)
    return player, player_anim


def main():
    clock = pygame.time.Clock()
    level_manager = LevelManager()
    level_manager.reset()
    Logger().initialize()

    # Инициализация игрока у стартового портала
    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (100, SCREEN_HEIGHT - 150)
    player, player_anim = create_player(*start_pos)

    Logger().debug(f"INIT_CREATE: start_pos:{start_pos}")

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
                        player, player_anim = create_player(*start_pos)
                        Logger().debug(f"NEW_LEVEL: start_pos:{start_pos}")
                elif event.key == pygame.K_r and game_over:  # Рестарт по нажатию R
                    # Сброс игры
                    level_manager.reset()
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                    player, player_anim = create_player(*start_pos)
                    Logger().debug(f"RESTART_GAME: start_pos:{start_pos}")
                    level_manager.current_level.remove_start_portal()  # Добавляем удаление портала
                    game_over = False

            # Управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            player.sit_down()
        else:
            if player.is_sitting:
                player.sit_handler.stand_up(level_manager.current_level.get_all_game_objects())

        if keys[pygame.K_s]:
            player.sit_down()
            # Приседание (без проверки)
            # Вставание (с проверкой)
        elif player.is_sitting:
            player.sit_handler.stand_up(level_manager.current_level.get_all_game_objects())  # передаем список всех объектов

            # Автоматическое вставание при прыжке/движении
            if (keys[pygame.K_SPACE] or
                    (player.is_sitting and (keys[pygame.K_a] or keys[pygame.K_d]))):
                player.sit_handler.stand_up(level_manager.current_level.get_all_game_objects())

        if keys[pygame.K_a]:
            player.move(-1)
        elif keys[pygame.K_d]:
            player.move(1)
        else:
            player.move(0)

        if keys[pygame.K_SPACE]:
            player.jump()

        # Обновление
        if not level_manager.current_level.completed:
            # Отрисовка игрока
            player_anim.update()
            # В основном цикле отрисовки
            player.apply_physics(level_manager.current_level.get_all_game_objects(), LEVEL_WIDTH, SCREEN_HEIGHT)

            # Проверка падения за экран (Game Over)
            if player.rect.top > SCREEN_HEIGHT:
                game_over = True

            # Проверка опасных столкновений
            if level_manager.current_level.check_hazard_collision(player.rect):
                # Респавн при смерти
                start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                player, player_anim = create_player(*start_pos)

            # Проверка падения в яму
            if level_manager.current_level.check_fall_into_pit(player.rect):
                start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                player, player_anim = create_player(*start_pos)

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
                    player, player_anim = create_player(*start_pos)
                    Logger().debug(f"NEW_LEVEL: start_pos:{start_pos}")

        # Отрисовка
        screen.fill(DARK_GREEN)

        # Отрисовка уровня
        level_surface = pygame.Surface((LEVEL_WIDTH, SCREEN_HEIGHT))
        level_manager.current_level.draw(level_surface)
        screen.blit(level_surface, camera_offset)

        # Отрисовка игрока
        player_anim.draw(screen, camera_offset)

        #player_anim.draw(screen)
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